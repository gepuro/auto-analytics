from google.adk.agents import Agent, BaseAgent, LlmAgent, LoopAgent, SequentialAgent

from ..tools.exit_tool import exit_loop
from ..tools.mcptoolset import postgres_toolset

data_retrieval_agent = Agent(
    name="data_retrieval_agent",
    model="gemini-2.5-flash-lite-preview-06-17",
    tools=[postgres_toolset],
    description="SQLクエリを実行し、結果を取得・評価する専門エージェント",
    instruction=(
        "あなたはSQLクエリの実行専門家です。\n"
        "生成されたSQLクエリを実行し、結果を分析に適した形で取得してください。\n\n"
        "**クエリ実行手順:**\n"
        "1. テーブルの特定とサンプルデータの確認"
        "1.1. {get-tables} で全テーブルをリストアップ\n"
        "1.2. {get-table-schema} でスキーマ情報を取得\n"
        "1.3. {get-sample-data} でサンプルデータを確認\n"
        "2. クエリの生成と実行\n"
        "2.1. 分析に必要なクエリの生成（例: 売上分析、顧客分析など）\n"
        "2.2. {execute-query} でSQLクエリを実行\n"
        "2.3. 実行結果の確認（エラーの有無、データ品質）\n"
        "2.4. クエリエラーが発生した場合は、エラーメッセージを参考に修正して、クエリの生成と実行をやりなおす\n"
        "3. 4つのキーをJSON形式で、最終結果を作成: explain, sql, sql_results, nl_results\n"
        "   - `explain`: スキーマ、例、質問に基づいてクエリを生成するステップバイステップの推論を記述\n"
        "   - `sql`: 生成されたSQLクエリを出力\n"
        "   - `sql_results`: SQL実行クエリ結果（利用可能な場合）、それ以外はNone\n"
        "   - `nl_results`: 結果に関する自然言語の説明、それ以外は生成されたSQLが無効な場合はNone\n\n"
    ),
    output_key="query_execution_result",
)
