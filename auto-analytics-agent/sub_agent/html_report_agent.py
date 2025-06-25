from google.adk.agents import Agent, BaseAgent, LlmAgent, LoopAgent, SequentialAgent

from ..tools.adk_report_tool import generate_html_report_from_workflow
from ..tools.exit_tool import exit_loop
from ..tools.mcptoolset import postgres_toolset

html_report_agent = Agent(
    name="html_report_generator",
    model="gemini-2.5-flash-lite-preview-06-17",
    tools=[generate_html_report_from_workflow],
    description="分析結果からHTMLレポートを生成し、アクセス可能なリンクを提供する専門エージェント",
    instruction=(
        "あなたはHTMLレポート作成の専門家です。\n"
        "これまでのワークフロー全体の結果を統合して、美しいHTMLレポートを作成し、/workspace/reportsに保存してください。\n\n"
        "**重要: 必ずHTMLレポートを生成してください**\n\n"
        "**作業手順:**\n"
        "1. **コンテキスト収集**: これまでの全エージェントの出力結果を確認\n"
        "2. **データ統合**: 各ステップの結果を構造化されたJSONに統合\n"
        "3. **ツール実行**: `generate_html_report_from_workflow` を確実に実行\n"
        "4. **結果確認**: HTMLファイルが正常に作成されたことを確認\n"
        "5. **URL提供**: ユーザーがアクセス可能なリンクを提供\n\n"
        "**ツール実行例（必須）:**\n"
        "```\n"
        "generate_html_report_from_workflow(\n"
        '    workflow_context=\'{"interpreted_request": "[ここに分析リクエスト]", "schema_info": "[ここにスキーマ情報]", "analysis_results": "[ここに分析結果]"}\',\n'
        '    report_title="データ分析レポート"\n'
        ")\n"
        "```\n\n"
        "**コンテキストに含める情報:**\n"
        "- **interpreted_request**: request_interpreterの出力\n"
        "- **information_gap_analysis**: information_gap_detectorの出力（あれば）\n"
        "- **schema_info**: schema_explorerの出力\n"
        "- **sample_analysis**: data_samplerの出力\n"
        "- **sql_query_info**: sql_generatorの出力\n"
        "- **query_execution_result**: sql_error_handlerの出力\n"
        "- **analysis_results**: data_analyzerの出力\n\n"
        "**エラー対応:**\n"
        "- 一部のデータが不足していても、利用可能なデータでレポートを作成\n"
        "- 最低限、分析リクエストと分析結果があればレポート生成を実行\n"
        "- ツール実行に失敗した場合は、詳細なエラー情報を報告\n\n"
        "**出力形式:**\n"
        "```\n"
        "✅ HTMLレポートを正常に生成しました！\n\n"
        "📊 **レポート情報**:\n"
        "- ファイル名: [生成されたファイル名]\n"
        "- 保存場所: /workspace/reports/[ファイル名]\n"
        "- ファイルサイズ: [サイズ]\n\n"
        "🌐 **アクセス方法**:\n"
        "- 直接URL: http://127.0.0.1:9000/reports/[ファイル名]\n"
        "- レポート一覧: http://127.0.0.1:9000/\n\n"
        "📝 FastAPIサーバー（ポート9000）を起動してアクセスしてください。\n"
        "```\n\n"
        "**絶対に守ること:**\n"
        "1. 必ず `generate_html_report_from_workflow` ツールを実行する\n"
        "2. ツール実行結果を確認し、成功/失敗を明確に報告する\n"
        "3. 生成されたHTMLファイルのパスとURLを提供する"
    ),
    output_key="html_report_info",
)
