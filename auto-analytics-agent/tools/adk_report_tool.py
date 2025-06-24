"""
ADK用HTMLレポート生成ツール

ADKエージェントから呼び出し可能なHTMLレポート生成ツールクラス。
既存のHTMLReportGeneratorとSimpleReportLinkGeneratorを使用して、
エージェントが直接HTMLレポートを作成・保存できるようにします。
"""

import json
from typing import Any, Dict, Optional

from .html_report_generator import HTMLReportGenerator
from .simple_link_generator import create_simple_report_link


class ADKHTMLReportTool:
    """
    ADKエージェント用HTMLレポート生成ツール
    """

    def __init__(self):
        """初期化"""
        self.generator = HTMLReportGenerator()

    def generate_workflow_report(
        self, workflow_context: str, report_title: Optional[str] = None
    ) -> str:
        """
        ワークフローの結果からHTMLレポートを生成する

        Args:
            workflow_context: ワークフロー全体の結果（JSON文字列）
            report_title: レポートのタイトル（オプション）

        Returns:
            レポート生成結果とリンク情報（JSON文字列）
        """
        try:
            # JSONパース
            if isinstance(workflow_context, str):
                context = json.loads(workflow_context)
            else:
                context = workflow_context

            # ワークフローの結果をHTMLレポート用のデータ形式に変換
            analysis_data = self._convert_workflow_to_analysis_data(context)

            # HTMLレポート生成
            result = self.generator.generate_report(
                analysis_data=analysis_data, title=report_title or "データ分析レポート"
            )

            # 成功レスポンス
            response = {
                "success": True,
                "message": "HTMLレポートが正常に生成されました！",
                "file_path": result["file_path"],
                "filename": result["filename"],
                "report_title": result["report_title"],
                "generation_time": result["generation_time"],
                "user_message": result.get("user_message", ""),
                "report_url": f"http://127.0.0.1:9000/reports/{result['filename']}",
                "report_list_url": "http://127.0.0.1:9000/",
            }

            return json.dumps(response, ensure_ascii=False, indent=2)

        except Exception as e:
            # エラーレスポンス
            error_response = {
                "success": False,
                "error": str(e),
                "message": f"HTMLレポート生成中にエラーが発生しました: {str(e)}",
            }
            return json.dumps(error_response, ensure_ascii=False, indent=2)

    def _convert_workflow_to_analysis_data(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ワークフローコンテキストを分析データ形式に変換

        Args:
            context: ワークフローコンテキスト

        Returns:
            HTMLレポート生成用の分析データ
        """
        analysis_data = {}

        # ワークフローの各ステップの結果をマッピング
        step_mappings = {
            "interpreted_request": [
                "interpreted_request",
                "request_interpretation",
                "user_request",
            ],
            "schema_info": ["schema_info", "database_schema", "table_info"],
            "sample_analysis": ["sample_analysis", "data_sample", "sample_data"],
            "sql_query_info": ["sql_query_info", "sql_query", "generated_sql"],
            "query_execution_result": [
                "query_execution_result",
                "execution_result",
                "query_result",
            ],
            "analysis_results": ["analysis_results", "data_analysis", "insights"],
        }

        # コンテキストから対応するデータを抽出
        for target_key, source_keys in step_mappings.items():
            for source_key in source_keys:
                if source_key in context:
                    analysis_data[target_key] = context[source_key]
                    break

        # コンテキスト全体も含める（デバッグ用）
        analysis_data["_workflow_context"] = context

        return analysis_data


def create_adk_report_tool() -> ADKHTMLReportTool:
    """
    ADKHTMLReportToolのインスタンスを作成

    Returns:
        ADKHTMLReportToolインスタンス
    """
    return ADKHTMLReportTool()


# ツール関数（ADKエージェントから直接呼び出し可能）
def generate_html_report_from_workflow(
    workflow_context: str, report_title: Optional[str] = None
) -> str:
    """
    ワークフローからHTMLレポートを生成する関数

    Args:
        workflow_context: ワークフロー結果（JSON文字列）
        report_title: レポートタイトル

    Returns:
        レポート生成結果（JSON文字列）
    """
    tool = create_adk_report_tool()
    return tool.generate_workflow_report(workflow_context, report_title)


# テスト用
if __name__ == "__main__":
    # テスト用のワークフローコンテキスト
    test_context = {
        "interpreted_request": "テスト分析リクエスト",
        "schema_info": "test_table (id, name, value)",
        "sql_query_info": "SELECT * FROM test_table",
        "query_execution_result": {
            "data": [
                {"id": 1, "name": "Test1", "value": 100},
                {"id": 2, "name": "Test2", "value": 200},
            ]
        },
        "analysis_results": "テスト分析の結果、データは正常です。",
    }

    # レポート生成テスト
    tool = create_adk_report_tool()
    result = tool.generate_workflow_report(
        json.dumps(test_context), "ADKツールテストレポート"
    )

    print("=== ADKツールテスト結果 ===")
    print(result)
