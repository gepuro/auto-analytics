from google.adk.agents import Agent, BaseAgent, LlmAgent, LoopAgent, SequentialAgent

from ..tools.exit_tool import exit_loop
from ..tools.mcptoolset import postgres_toolset

table_explorer = LlmAgent(
    name="table_explorer",
    model="gemini-2.5-flash-lite-preview-06-17",
    tools=[postgres_toolset],
    description="データベース内のテーブルを探索し、分析に最適なテーブルを特定してスキーマとサンプルデータを確認する統合エージェント",
    instruction=(
        "あなたはデータベース探索の専門家です。\n"
        "分析要件に基づいて、最適なテーブルを見つけ出し、詳細な情報を提供してください。\n\n"
        "**探索プロセス（ループ実行）:**\n"
        "1. **テーブル一覧取得**: `get-tables` で全テーブルをリストアップ\n"
        "2. **関連性評価**: 各テーブル名から分析要件との関連性を判定\n"
        "3. **詳細調査ループ**: 関連性の高いテーブルを順次調査\n"
        "   - `get-table-schema` でスキーマ情報を取得\n"
        "   - `execute-query` でサンプルデータを確認（SELECT * FROM table LIMIT 5）\n"
        "   - データの品質と適合性を評価\n"
        "4. **最適テーブル選定**: 複数の候補から最も適したテーブルを決定\n\n"
        "5. **統合レポートの作成**: \n\n"
        "**評価基準:**\n"
        "- テーブル名と分析要件の関連性\n"
        "- 必要なカラムの存在\n"
        "- データの品質（欠損値、データ型、値の範囲）\n"
        "- レコード数とデータの鮮度\n"
        "- 他テーブルとの結合可能性\n\n"
        "**スキーマ取得クエリ:**\n"
        "```sql\n"
        "SELECT column_name, data_type, is_nullable, column_default\n"
        "FROM information_schema.columns\n"
        "WHERE table_name = 'テーブル名' AND table_schema = 'public'\n"
        "ORDER BY ordinal_position;\n"
        "```\n\n"
        "**統合レポート形式:**\n"
        "調査結果を包括的に報告してください：\n"
        "```\n"
        "【探索結果サマリー】\n"
        "• 調査したテーブル数: X個\n"
        "• 最適なテーブル: table_name\n"
        "• 選定理由: [具体的な理由]\n\n"
        "【テーブル詳細】\n"
        "• カラム構成: [主要カラムとデータ型]\n"
        "• レコード数: 約X件\n"
        "• データ品質: [良好/注意点あり]\n"
        "• サンプルデータの特徴: [簡潔な説明]\n\n"
        "【分析への適用性】\n"
        "• 必要データの充足度: X%\n"
        "• 推奨される分析アプローチ: [具体的な提案]\n"
        "```\n\n"
        "**重要な注意事項:**\n"
        "- 複数のテーブルを効率的に調査（最大5テーブルまで詳細確認）\n"
        "- 各テーブルの調査結果を内部で比較評価\n"
        "- 最終的に1つの統合レポートとして出力\n"
        "- 技術的詳細と分かりやすさのバランスを保つ"
    ),
    output_key="table_explorer_info",
)
table_explorer_exit = LlmAgent(
    name="table_explorer_exit",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="テーブル探索の終了を判断し、ループを終了するエージェント",
    tools=[exit_loop],
    instruction=(
        "あなたはテーブル探索の終了を判断する専門家です。\n"
        "終了する場合は、exit_loopを実行してください。\n\n"
        "**終了判断基準:**\n"
        "- 主要なテーブルの情報が十分に得られた\n"
        "- データの品質と構造が分析に適していると判断された\n"
        "- 追加のテーブル調査が不要と判断された\n\n"
        "**追加情報は出力しないでください。**\n"
    ),
)


table_explorer_loop = LoopAgent(
    name="table_explorer_loop",
    # Agent order is crucial: Critique first, then Refine/Exit
    sub_agents=[table_explorer, table_explorer_exit],
    max_iterations=5,  # Limit loops
)

sample_data_explorer = LlmAgent(
    name="sample_data_explorer",
    model="gemini-2.5-flash-lite-preview-06-17",
    tools=[postgres_toolset],
    description="テーブルのサンプルデータを取得し、分析に適したデータの品質と構造を評価する専門エージェント",
    instruction=(
        "あなたはデータ分析におけるサンプルデータの専門家です。\n"
        "指定された全てのテーブルをからサンプルデータを取得し、データ例を示しながら、分析に適した品質と構造を評価してください。\n\n"
        "**サンプルデータ取得: `get-sample-data` でテーブルのサンプルを取得**\n"
    ),
    output_key="sample_data_info",
)
sample_data_explorer_exit = LlmAgent(
    name="sample_data_explorer_exit",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="サンプルデータ探索の終了を判断し、ループを終了するエージェント",
    tools=[exit_loop],
    instruction=(
        "あなたはサンプルデータ探索の終了を判断する専門家です。\n"
        "終了する場合は、exit_loopを実行してください。\n\n"
        "**終了判断基準:**\n"
        "- 主要なテーブルのサンプルデータが十分に得られた\n"
        "- データの品質と構造が分析に適していると判断された\n"
        "- 追加のサンプルデータ取得が不要と判断された\n"
        "\n"
        "**追加情報は出力しないでください。**\n"
    ),
)
sample_data_explorer_loop = LoopAgent(
    name="sample_data_explorer_loop",
    # Agent order is crucial: Critique first, then Refine/Exit
    sub_agents=[sample_data_explorer, sample_data_explorer_exit],
    max_iterations=5,  # Limit loops
)

table_and_sameple_explorer = SequentialAgent(
    name="table_and_sample_explorer",
    sub_agents=[
        table_explorer_loop,
        sample_data_explorer_loop,
    ],
    description="テーブル探索とサンプルデータ取得を統合的に行うエージェント",
)
