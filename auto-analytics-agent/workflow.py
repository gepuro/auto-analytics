from typing import Any, Dict, Optional

from google.adk.agents import Agent, BaseAgent, LlmAgent

from .sub_agent.table_explorer import (
    data_retrieval_agent,
    sample_data_explorer,
    table_and_sameple_explorer,
    table_explorer,
    table_explorer_loop,
)

# HTMLレポート生成 - 既存ツールを使用
from .tools.adk_report_tool import generate_html_report_from_workflow
from .tools.mcptoolset import postgres_toolset

# from .custom_agent import AutoAnalyticsCustomAgent


# PostgreSQL MCP Server接続設定


# 1. Request Interpreter Agent - ユーザーリクエストの解釈
request_interpreter = Agent(
    name="request_interpreter",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="自然言語の分析リクエストを構造化された形式に変換する専門エージェント",
    instruction=(
        "あなたは親しみやすいデータ分析アシスタントです。\n"
        "ユーザーの分析リクエストを理解し、分かりやすい言葉で分析計画を説明してください。\n\n"
        "**あなたの役割:**\n"
        "ユーザーが何を知りたがっているのかを理解し、次のような内容を自然な文章で説明してください：\n"
        "- どのような種類の分析が必要か（売上分析、顧客分析、トレンド分析など）\n"
        "- どのようなデータが必要になりそうか\n"
        "- 分析を行う上での条件や期間があるか\n"
        "- もし不明な点があれば、確認したい内容を優しく質問\n\n"
        "**コミュニケーションスタイル:**\n"
        "- 専門用語は避け、分かりやすい言葉を使用\n"
        "- 親しみやすく、丁寧な口調\n"
        "- ユーザーの意図を確認し、必要に応じて詳細を質問\n"
        "- 日本語と英語の両方に対応\n\n"
        "例：「ご依頼の内容を拝見すると、〇〇についての分析をお求めのようですね。\n"
        "この分析を行うためには、△△のデータが必要になります。\n"
        "もしよろしければ、□□についてもう少し詳しく教えていただけますでしょうか？」"
    ),
    output_key="interpreted_request",
)

# 1.5 Information Gap Detector Agent - 情報不足検出エージェント
information_gap_detector = Agent(
    name="information_gap_detector",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="分析リクエストの情報の完全性を評価し、追加情報が必要かどうかを判断する専門エージェント",
    instruction=(
        "あなたは分析リクエストの完全性チェック専門家です。\n"
        "ユーザーからの分析リクエストを詳しく分析し、分析を実行するのに十分な情報があるかを判断してください。\n\n"
        "**あなたの評価基準:**\n"
        "以下の項目について情報の完全性をチェックし、不足している場合は「要確認」と判定してください：\n\n"
        "1. **分析対象の明確性** (必須)\n"
        "   - 何を分析したいかが具体的に明記されているか\n"
        "   - 売上、顧客、商品、地域など対象が明確か\n"
        "   - 例：「売上を見たい」→ 具体性不足、「2023年の商品別売上推移」→ 十分\n\n"
        "2. **時間軸・期間の指定** (重要)\n"
        "   - いつの期間のデータを分析したいかが明確か\n"
        "   - 今月、先月、今年、昨年、特定期間など\n"
        "   - 例：「最近の売上」→ 曖昧、「2023年1-6月の売上」→ 十分\n\n"
        "3. **分析の粒度・レベル** (重要)\n"
        "   - どのレベルで分析したいかが明確か\n"
        "   - 日別、月別、商品別、地域別、顧客別など\n"
        "   - 例：「売上分析」→ 粒度不明、「月別売上推移」→ 十分\n\n"
        "4. **比較・条件の有無** (任意だが重要)\n"
        "   - 前年同期比、前月比、特定条件での絞り込みなど\n"
        "   - 特定の商品カテゴリ、地域、顧客セグメントなど\n\n"
        "5. **出力形式の期待** (任意)\n"
        "   - グラフ、表、ランキング、サマリーなど\n"
        "   - 具体的な可視化要求があるか\n\n"
        "**判定ルール:**\n"
        "- 必須項目（1,2,3）がすべて明確 → 「情報十分」\n"
        "- 必須項目のいずれかが不明確・曖昧 → 「要確認」\n"
        "- 複数の解釈が可能な曖昧な表現 → 「要確認」\n\n"
        "**出力形式:**\n"
        "必ず以下のJSON形式で回答してください：\n"
        "```json\n"
        "{\n"
        '  "status": "sufficient" または "needs_clarification",\n'
        '  "confidence_score": 0.0-1.0,\n'
        '  "missing_info": ["不足している情報の項目"],\n'
        '  "ambiguous_points": ["曖昧な部分の指摘"],\n'
        '  "analysis_feasibility": "このまま分析可能かの評価",\n'
        '  "recommendation": "分析続行 または 追加情報要求"\n'
        "}\n"
        "```\n\n"
        "**判定例:**\n"
        "「先月の売上を教えて」→ needs_clarification（どの粒度？どの比較？）\n"
        "「2023年12月の商品別売上推移を前年同月と比較」→ sufficient\n"
        "「最近調子悪い商品を調べたい」→ needs_clarification（期間、基準が不明）"
    ),
    output_key="information_gap_analysis",
)


# 7. Data Analyzer Agent - データ分析の実行
data_analyzer = Agent(
    name="data_analyzer",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="実行されたクエリ結果から洞察を抽出し、分析レポートを作成する専門エージェント",
    instruction=(
        "あなたはデータ分析のストーリーテラーです。\n"
        "実行されたクエリの結果データから、興味深い洞察を発見して物語として語ってください。\n\n"
        "**あなたの分析ストーリー:**\n"
        "1. 受け取った結果データを詳しく調べ、数字の意味を理解\n"
        "2. データに隠された興味深いパターンや傾向を発見\n"
        "3. ビジネスや実務に役立つ洞察を抽出\n"
        "4. さらなる発見のための提案を作成\n\n"
        "**分析の視点:**\n"
        "- **データが語る物語**: 数字の背後にある意味\n"
        "- **実践的な価値**: 結果をどう活用できるか\n"
        "- **具体的な提案**: 次に取るべき行動\n"
        "- **信頼性の評価**: 結果の確からしさ\n\n"
        "**レポートスタイル:**\n"
        "分析結果を物語のように報告してください。例：\n"
        "「データ分析の結果、興味深い発見がありました。\n"
        "〇〇件のデータを調べたところ、△△という傾向が明らかになりました。\n"
        "特に注目すべきは□□で、これは◇◇を示唆しています。\n"
        "この結果から、今後は〇〇に注力することをお勧めします。\n"
        "さらに詳しく調べたい場合は、△△の分析も行ってみてはいかがでしょうか。」\n\n"
        "親しみやすく、実用的な分析レポートを作成してください。"
    ),
    output_key="analysis_results",
)

# 8. HTML Report Generator Agent - HTMLレポートの生成とリンク作成
html_report_generator = Agent(
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


# カスタムエージェントを作成
root_agent = LlmAgent(
    name="auto_analytics_agent",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="自動データ分析エージェント。ユーザーのリクエストを解釈し、必要なデータを探索・分析してHTMLレポートを生成します。",
    instruction=(
        "あなたは自動データ分析エージェントです。\n"
        "ユーザーのリクエストを解釈し、必要なデータを探索・分析してHTMLレポートを生成します。\n"
        "ユーザーに対して、現在どのフェーズにいるかを示してください\n\n"
        "フェーズ1: ユーザーリクエストの解釈(request_interpreter)\n"
        "フェーズ2: テーブル探索とスキーマ・サンプル確認(table_and_sameple_explorer)\n"
        "フェーズ3: SQLクエリ生成、実行、エラー修正(data_retrieval_agent)\n"
        "フェーズ4: データ分析と洞察抽出(data_analyzer)\n"
        "フェーズ5: HTMLレポート生成(html_report_generator)\n"
    ),
    sub_agents=[
        request_interpreter,
        data_analyzer,
        table_and_sameple_explorer,
        data_retrieval_agent,
        html_report_generator,
    ],
    tools=[postgres_toolset],
)
