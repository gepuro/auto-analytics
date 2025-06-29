from google.adk.agents import Agent, BaseAgent, LlmAgent, LoopAgent, SequentialAgent

from ..tools.mcptoolset import postgres_toolset

data_retrieval_agent = LlmAgent(
    name="data_retrieval_agent",
    model="gemini-2.5-flash-lite-preview-06-17",
    tools=[postgres_toolset],
    description="SQLクエリを実行し、結果を取得・評価する専門エージェント",
    instruction=(
        "あなたはPostgreSQLクエリの実行専門家です。\n"
        "生成されたSQLクエリを実行し、結果を分析に適した形で取得してください。\n\n"
        "クエリ実行手順:\n"
        "**2. クエリの生成と実行(繰り返し処理)**\n"
        "2.1. 分析に必要なクエリの生成（例: 売上分析、顧客分析など）\n"
        "2.2. Tool `execute-query` でSQLクエリを実行\n"
        "2.3. 実行結果の確認（エラーの有無、データ品質）\n"
        "2.4. クエリエラーが発生した場合は、エラーメッセージを参考に修正して、クエリの生成と実行をやりなおす\n\n"
        "**3. クエリの実行結果をユーザーに提示**\n"
        " - `sql`: SQLクエリ\n"
        " - `sql_results`: クエリ結果\n"
        " - `nl_results`: 結果に関する自然言語の説明\n\n"
        ""
    ),
    output_key="data_retrieval_result",
)
