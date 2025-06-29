import json
from datetime import datetime
from typing import Any, Dict, Optional

import markdown
from google.adk.agents import Agent
from google.adk.tools import ToolContext, load_artifacts
from google.genai import types


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
        interpreted_request = markdown.markdown(
            workflow_data.get("interpreted_request", "分析リクエストが見つかりません")
        )
        schema_info = markdown.markdown(workflow_data.get("schema_info", ""))
        sql_query = markdown.markdown(workflow_data.get("sql_query_info", ""))
        query_results = workflow_data.get("query_execution_result", {})

        analysis_results = markdown.markdown(workflow_data.get("analysis_results", ""))

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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
        
        {f'<div class="info-box"><h2>🗄️ データベーススキーマ情報</h2><pre>{schema_info}</pre></div>' if schema_info else ''}
        
        {f'<div class="sql-box"><h2>💻 実行されたSQLクエリ</h2><pre>{sql_query}</pre></div>' if sql_query else ''}
        
        <div>
            <h2>📊 クエリ実行結果</h2>
            {_format_query_results(query_results)}
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
            "message": f"HTMLレポートが http://localhost:9000/reports/{filename.split('/')[-1]} で表示可能です。",
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
        "あなたはHTMLレポート作成の専門家です。\n"
        "これまでのワークフロー全体の結果を統合して、美しいHTMLレポートを作成し、ADK artifactとして保存してください。\n\n"
        "**重要: 必ずHTMLレポートを生成してください**\n\n"
        "**作業手順:**\n"
        "1. **コンテキスト収集**: これまでの全エージェントの出力結果を確認\n"
        "2. **データ統合**: 各ステップの結果を辞書形式に統合\n"
        "3. **ツール実行**: `create_html_report` を確実に実行\n"
        "4. **結果確認**: Artifactが正常に保存されたことを確認\n"
        "5. **結果報告**: 生成結果をユーザーに報告\n\n"
        "**ツール実行例（必須）:**\n"
        "```python\n"
        "# ワークフローデータを辞書形式で準備\n"
        "workflow_data = {\n"
        '    "interpreted_request": "ユーザーの分析リクエスト",\n'
        '    "sql_query_info": "実行されたSQLクエリ",\n'
        '    "data_table": {"data": [...]},\n'
        '    "javascript_chart": {"chart": [...]},\n'
        '    "analysis_results": "データ分析の結果と洞察"\n'
        "}\n\n"
        "# レポート生成関数を呼び出し\n"
        "result = create_html_report(\n"
        "    workflow_data=workflow_data,\n"
        '    report_title="データ分析レポート"\n'
        ")\n"
        "```\n\n"
        "**収集すべき情報:**\n"
        "- **interpreted_request**: request_interpreterの出力\n"
        "- **sql_query_info**: data_retrivalで実行したクエリ\n"
        "- **query_execution_result**: data_retrivalのクエリを実行した結果\n"
        "- **analysis_results**: data_analyzerの出力\n\n"
        "**エラー対応:**\n"
        "- 一部のデータが不足していても、利用可能なデータでレポートを作成\n"
        "- 最低限、分析リクエストと分析結果があればレポート生成を実行\n"
        "- ツール実行に失敗した場合は、詳細なエラー情報を報告\n\n"
        "**出力形式:**\n"
        "```\n"
        "- {artifact.message} のリンクを含めてください。\n"
        "- HTMLレポートをArtifactとして正常に保存しました！\n\n"
        "📊 **レポート情報**:\n"
        "- Artifact名: [生成されたファイル名]\n"
        "- レポートタイトル: [レポートタイトル]\n"
        "- 生成時刻: [生成時刻]\n\n"
        "📝 このレポートはADK Artifactとして保存されており、\n"
        "   セッション内で再利用可能です。\n"
        "```\n\n"
        "**絶対に守ること:**\n"
        "1. 必ず `create_html_report` ツールを実行する\n"
        "2. ツール実行結果を確認し、成功/失敗を明確に報告する\n"
        "3. {artifact.message} のリンクを含めて、生成されたHTMLレポートの情報を報告する\n"
    ),
    output_key="html_report_info",
)
