import json
from datetime import datetime
from typing import Any, Dict, Optional

import google.genai.types as types
import markdown
from google.adk.agents import Agent, BaseAgent, LlmAgent
from google.adk.tools import ToolContext, load_artifacts

from ..utils.gemini import gemini


def _process_data_to_markdown(data: Any) -> str:
    """データをマークダウン形式に変換する共通処理"""
    if isinstance(data, dict):
        markdown_text = _convert_dict_to_markdown(data)
    else:
        markdown_text = str(data)

    return markdown.markdown(markdown_text)


def _convert_dict_to_markdown(data: Dict[str, Any]) -> str:
    """辞書をLLMを使ってマークダウン形式に変換"""
    try:
        prompt = f"""
以下の辞書データを、日本語で読みやすいマークダウン形式に変換してください。
構造化された情報として整理し、見出しやリストを適切に使用してください。

データ:
{json.dumps(data, ensure_ascii=False, indent=2)}

マークダウン形式で出力してください（```markdownタグは不要）:
"""
        response = gemini(
            content=prompt,
            model="gemini-2.5-flash-lite-preview-06-17",
            max_output_tokens=10000,
        )

        return response.text.strip()

    except Exception:
        # LLM変換に失敗した場合はJSON形式でそのまま返す
        return f"```json\n" f"{json.dumps(data, ensure_ascii=False, indent=2)}\n```"


def create_html_report(
    workflow_data: Dict[str, Any], report_title: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """
    ワークフローデータからHTMLレポートを生成し、ADK artifactとして保存する

    Args:
        workflow_data: ワークフロー全体の結果データ
        report_title: レポートのタイトル
        tool_context: ADKのToolContext（artifact保存に使用）

    Returns:
        成功/失敗の情報を含む辞書
    """
    try:
        # タイムスタンプの生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        generation_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

        # データの抽出と整形
        interpreted_request_raw = workflow_data.get(
            "interpreted_request", "分析リクエストが見つかりません"
        )
        interpreted_request = _process_data_to_markdown(interpreted_request_raw)

        table_explorer_info_raw = workflow_data.get("table_explorer_info", {})
        table_explorer_info = _process_data_to_markdown(table_explorer_info_raw)

        data_retrieval_result_raw = workflow_data.get("data_retrieval_result", "")
        data_retrieval_result = _process_data_to_markdown(data_retrieval_result_raw)

        analysis_results_raw = workflow_data.get("analysis_results", "")
        analysis_results = _process_data_to_markdown(analysis_results_raw)

        # HTMLコンテンツの生成
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                         Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .info-box {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .sql-box {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .analysis-section {{
            background-color: #e8f5e9;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: right;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{report_title}</h1>
        <p class="timestamp">生成日時: {generation_time}</p>
        
        <div class="info-box">
            <h2>📋 分析リクエスト</h2>
            <p>{interpreted_request}</p>
        </div>
        
        <div class="info-box">
            <h2>📊 テーブル情報</h2
            <p>{table_explorer_info}</p>
        </div>

        <div class="info-box">
            <h2>📊 データ取得結果</h2>
            {data_retrieval_result}
        </div>        
        <div class="analysis-section">
            <h2>🔍 分析結果</h2>
            {analysis_results}
        </div>
    </div>
</body>
</html>
        """

        filename = f"/workspace/reports/analysis_report_{timestamp}.html"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        # ADK Partオブジェクトを作成（文字列から直接作成）
        html_part = types.Part.from_text(text=html_content)

        # artifactとして保存
        tool_context.save_artifact(filename, html_part)

        return {
            "success": True,
            "message": (
                f"HTMLレポートが http://localhost:9000/reports/"
                f"{filename.split('/')[-1]} で表示可能です。"
            ),
            "filename": filename,
            "report_title": report_title,
            "generation_time": generation_time,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"HTMLレポート生成中にエラーが発生しました: {str(e)}",
        }


def _format_query_results(query_results: Any) -> str:
    """クエリ結果をHTMLテーブル形式にフォーマット"""
    if not query_results:
        return "<p>クエリ結果がありません</p>"

    if isinstance(query_results, dict) and "data" in query_results:
        data = query_results["data"]
        if isinstance(data, list) and len(data) > 0:
            # テーブルヘッダーの作成
            if isinstance(data[0], dict):
                headers = list(data[0].keys())
                html = "<table>\n<thead>\n<tr>\n"
                for header in headers:
                    html += f"<th>{header}</th>\n"
                html += "</tr>\n</thead>\n<tbody>\n"

                # テーブル行の作成
                for row in data[:100]:  # 最大100行まで表示
                    html += "<tr>\n"
                    for header in headers:
                        html += f"<td>{row.get(header, '')}</td>\n"
                    html += "</tr>\n"

                html += "</tbody>\n</table>\n"

                if len(data) > 100:
                    html += f"<p><em>他 {len(data) - 100} 件のデータがあります</em></p>"

                return html

    return f"<pre>{str(query_results)}</pre>"


html_report_agent = Agent(
    name="html_report_generator",
    model="gemini-2.5-flash-lite-preview-06-17",
    tools=[create_html_report, load_artifacts],
    description="分析結果からHTMLレポートを生成し、ADK artifactとして保存する専門エージェント",
    instruction=(
        "あなたはデータ分析の結果をHTMLレポートとしてまとめる専門家です。create_html_reportを必ず実行してください。\n"
        "**実行順序:**\n"
        "**1. これまでの分析結果を集約するためのworkflow_data辞書を作成してください。**\n"
        "{\n"
        "    'interpreted_request': 'ユーザーのリクエストをここに記述',\n"
        "    'table_explorer_info': 'table_explorer_info',\n"
        "    'data_retrieval_result': 'data_retrieval_result',\n"
        "    'analysis_results': 'analysis_results'\n"
        "}\n\n"
        "**2. create_html_report(workflow_data, report_title)を実行して、HTMLレポートを作成**\n"
        "**3. 'artifact.message'に含まれるURLをユーザーに報告**\n\n"
        "データが不足している場合は空文字列や空辞書を使用してもツールを必ず実行してください。"
    ),
    output_key="html_report_info",
)
