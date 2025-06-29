from typing import Any, Dict, Optional

from google.adk.agents import Agent, BaseAgent, LlmAgent

from .mytools import (
    call_data_analyzer_agent,
    call_data_retrieval_agent,
    call_html_report_agent,
    call_table_explorer_agent,
)
from .tools.mcptoolset import postgres_toolset

root_agent = LlmAgent(
    name="auto_analytics_agent",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="自動データ分析エージェント。ユーザーのリクエストを解釈し、必要なデータを探索・分析してHTMLレポートを生成します。",
    instruction=(
        "あなたは自動データ分析エージェントです。ステップ1から5を実行して、データ分析を実施します\n"
        "**分析の流れ:**\n"
        "**1. ユーザーのリクエスト理解: ユーザーのリクエストを理解する\n"
        "**2. テーブル探索とスキーマ・サンプル確認 / Tool `call_table_explorer_agent`**: ユーザーのリクエストを理解したら、分析対象のテーブルをcall_table_explorer_agentで特定してください。\n"
        "**3. SQLクエリ生成、実行、エラー修正 / Tool `call_data_retrieval_agent`**: call_table_explorer_agentでテーブルを特定したら、call_data_retrieval_agentでデータを取得してください。\n"
        "**4. データ分析と洞察抽出 / Tool `call_data_analyzer_agent`**: call_data_retrieval_agentを実行したら、call_data_analyzer_agentでデータ分析をしてください。\n"
        "**5: レポート生成 / Tool `call_html_report_agent`**: call_html_report_agentでHTML形式のレポートを作成してください。\n"
    ),
    tools=[
        postgres_toolset,
        call_data_retrieval_agent,
        call_table_explorer_agent,
        call_html_report_agent,
        call_data_analyzer_agent,
    ],
)
