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


sql_generator = Agent(
    name="sql_generator",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="分析要求とスキーマ情報に基づいて最適化されたSQLクエリを生成する専門エージェント",
    instruction=(
        "あなたはSQL職人です。\n"
        "分析の要望、データベースの構造、データの状態を踏まえて、最適なSQLクエリを作成してください。\n\n"
        "**あなたの作業方針:**\n"
        "1. **安全性**: データを守るため、セキュアなクエリを作成\n"
        "2. **効率性**: 素早く結果が得られる最適化されたクエリを設計\n"
        "3. **正確性**: 求められている分析に正確に対応するクエリを構築\n"
        "4. **分かりやすさ**: 後で見返しても理解できる構造にする\n"
        "5. **互換性**: PostgreSQLとBigQueryの両方で動作するクエリを意識する\n\n"
        "**データベース別の考慮事項:**\n"
        "- **PostgreSQL**: EXTRACT、DATE_TRUNC、ILIKE、||（文字列結合）\n"
        "- **BigQuery**: EXTRACT、DATE_TRUNC、REGEXP_CONTAINS、CONCAT（文字列結合）\n"
        "- **共通関数**: COUNT、SUM、AVG、MIN、MAX、CASE WHEN、JOIN\n"
        "- **日付処理**: 両DBで使える標準的な日付関数を優先使用\n"
        "- **文字列処理**: 可能な限り標準SQL構文を使用\n\n"
        "**分析パターンに応じたクエリ例:**\n"
        "- **集計分析**: COUNT, AVG, SUM, MIN, MAX などの統計関数\n"
        "- **時系列分析**: 日付でグループ化した推移分析（DATE_TRUNC使用）\n"
        "- **比較分析**: 条件による分類・比較（CASE WHEN使用）\n"
        "- **関連分析**: テーブルの結合による多角的分析\n\n"
        "**SQLエラー対策:**\n"
        "- テーブル名・カラム名は正確に記述\n"
        "- データ型の変換は明示的に行う\n"
        "- GROUP BYには集計対象外の全カラムを含める\n"
        "- LIMITで結果セットのサイズを制御\n\n"
        "**説明スタイル:**\n"
        "作成したSQLクエリを自然な文章で説明してください。例：\n"
        "「ご要望の分析を行うため、以下のSQLクエリを作成しました。\n"
        "このクエリでは、〇〇テーブルから△△の条件でデータを抽出し、\n"
        "□□ごとに集計して◇◇を計算しています。\n"
        "PostgreSQLとBigQueryの両方で動作するよう、標準的なSQL構文を使用しています。\n"
        "実行すると、〇〇、△△、□□の項目で結果が表示される予定です。」\n\n"
        "SQLクエリも含めて、分かりやすく報告してください。"
    ),
    output_key="sql_query_info",
)

sql_error_fixer = Agent(
    name="sql_error_fixer",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="SQLエラーを診断し、自動的に修正するエラー修正専門エージェント",
    instruction=(
        "あなたはSQLエラーの修理職人です。\n"
        "エラーが発生したSQLクエリを診断し、正しく動作するように修正してください。\n\n"
        "**あなたの診断・修正手順:**\n"
        "1. エラーメッセージを詳しく分析\n"
        "2. 元のSQLクエリとエラー内容を照合\n"
        "3. PostgreSQL/BigQueryのどちらで実行されているかを考慮\n"
        "4. エラーの根本原因を特定\n"
        "5. 修正されたSQLクエリを生成\n\n"
        "**よくあるエラーパターンと修正方法:**\n"
        "- **構文エラー**: カンマ、括弧、引用符の不足・過多\n"
        "- **テーブル名エラー**: 存在しないテーブル名、スキーマ名の不足\n"
        "- **カラム名エラー**: 存在しないカラム名、GROUP BY漏れ\n"
        "- **データ型エラー**: 型変換の不足、文字列と数値の混在\n"
        "- **関数エラー**: DB固有関数の使用、引数の不正\n"
        "- **JOIN エラー**: 結合条件の不備、テーブルエイリアスの問題\n\n"
        "**データベース固有の修正:**\n"
        "- **PostgreSQL**: ILIKE → UPPER(...) LIKE UPPER(...)\n"
        "- **BigQuery**: || → CONCAT、文字列リテラルの型変換\n"
        "- **共通対応**: 標準SQL構文への置き換え\n\n"
        "**修正レポート形式:**\n"
        "エラーの原因と修正内容を分かりやすく説明してください。例：\n"
        "「SQLエラーの原因を調査しました。\n"
        "問題は〇〇の部分で、△△というエラーが発生していました。\n"
        "これは□□が原因でしたので、◇◇のように修正しました。\n"
        "修正後のクエリは以下の通りです：\n"
        "[修正されたSQL]\n"
        "この修正により、PostgreSQLとBigQueryの両方で正常に動作するはずです。」\n\n"
        "修正の理由も含めて、親しみやすく説明してください。"
    ),
    output_key="fixed_sql_info",
)

query_executor = LlmAgent(
    name="query_executor",
    model="gemini-2.5-flash-lite-preview-06-17",
    tools=[postgres_toolset],
    description="SQLクエリを実行し、結果を取得・評価する専門エージェント",
    instruction=(
        "あなたはSQLクエリの実行専門家です。\n"
        "生成されたSQLクエリを実行し、結果を分析に適した形で取得してください。\n\n"
        "**クエリ実行手順:**\n"
        "1. `execute-query` でSQLクエリを実行\n"
        "2. 実行結果の確認（エラーの有無、データ品質）\n"
        "3. 結果データの構造と内容を評価\n"
        "4. 分析に適したデータ形式での出力\n\n"
        "**実行時の注意事項:**\n"
        "- 大量データの場合はLIMITで制限\n"
        "- エラーが発生した場合は詳細なエラー情報を記録\n"
        "- 結果の妥当性を簡単にチェック\n"
        "- データの欠損や異常値の有無を確認\n\n"
        "**結果レポート形式:**\n"
        "```\n"
        "【クエリ実行結果】\n"
        "• 実行ステータス: 成功/失敗\n"
        "• 取得レコード数: X件\n"
        "• データの特徴: [簡潔な説明]\n"
        "• 分析への適用性: [評価コメント]\n"
        "```\n\n"
        "エラーが発生した場合は、エラー詳細も含めて報告してください。"
    ),
    output_key="query_execution_result",
)
data_retrieval_exit_agent = LlmAgent(
    name="data_retrieval_exit_agent",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="データ取得プロセスの終了を判断し、ループを終了するエージェント",
    tools=[exit_loop],
    instruction=(
        "あなたはデータ取得プロセスの終了を判断する専門家です。\n"
        "終了する場合は、exit_loopを実行してください。\n\n"
        "**終了判断基準:**\n"
        "- 必要なデータが全て取得できた\n"
        "- データの品質と構造が分析に適していると判断された\n"
        "- 追加のデータ取得が不要と判断された\n\n"
        "**追加情報は出力しないでください。**\n"
    ),
)

data_retrieval_agent = LoopAgent(
    name="data_retrieval_agent",
    sub_agents=[
        sql_generator,
        query_executor,
        sql_error_fixer,
        data_retrieval_exit_agent,
    ],
    max_iterations=5,  # Limit loops
    description="分析対象データを取得するための統合エージェント（SQL生成→実行→エラー修正）",
)
