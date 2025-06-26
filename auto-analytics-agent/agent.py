from typing import Any, Dict, Optional

from google.adk.agents import Agent, BaseAgent, LlmAgent

from .mytools import (
    call_data_analyzer_agent,
    call_data_retrieval_agent,
    call_html_report_agent,
    call_request_interpreter_agent,
    call_table_explorer_agent,
)
from .tools.mcptoolset import postgres_toolset

root_agent = LlmAgent(
    name="auto_analytics_agent",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="自動データ分析エージェント。ユーザーのリクエストを解釈し、必要なデータを探索・分析してHTMLレポートを生成します。",
    instruction=(
        "あなたは自動データ分析エージェントです。\n"
        "ユーザーのリクエストを解釈し、必要なデータを探索・分析してHTMLレポートを生成します。\n"
        "**1. リクエストの解釈 / Tool `request_interpreter`**: ユーザーのリクエストが明確にするために、toolを利用してください。\n"
        "**2. テーブル探索とスキーマ・サンプル確認 / Tool `table_and_sameple_explorer`**: 分析対象のテーブルを特定するために、toolを利用してください。\n"
        "**3. SQLクエリ生成、実行、エラー修正 / Tool `data_retrieval_agent`**: table_and_sameple_explorerでテーブルを特定したら、data_retrieval_agentを実行してください。\n"
        "**4. データ分析と洞察抽出 / Tool `data_analyzer`**: data_retrieval_agentを実行したら、ユーザーのリクエストに答えてデータ分析をしてください。\n"
        # "**5: レポート生成 / Tool `html_report_agent`**: ユーザーの期待に応じて、HTML形式のレポートを作成してください\n"
    ),
    tools=[
        postgres_toolset,
        call_data_retrieval_agent,
        call_request_interpreter_agent,
        call_table_explorer_agent,
        # call_html_report_agent,
        call_data_analyzer_agent,
    ],
)
