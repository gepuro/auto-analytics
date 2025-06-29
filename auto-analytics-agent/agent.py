from typing import Any, Dict, Optional

from google.adk.agents import Agent, BaseAgent, LlmAgent

from .mytools import (
    call_data_analyzer_agent,
    call_data_retrieval_agent,
    call_html_report_agent,
    call_table_explorer_agent,
)
from .sub_agent.data_analyzer_agent import data_analyzer_agent
from .sub_agent.data_retrieval_agent import data_retrieval_agent
from .sub_agent.html_report_agent import html_report_agent
from .sub_agent.table_explorer_agent import table_explorer
from .tools.mcptoolset import postgres_toolset

root_agent = LlmAgent(
    name="auto_analytics_agent",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="自動データ分析エージェント。ユーザーのリクエストを解釈し、必要なデータを探索・分析してHTMLレポートを生成します。",
    instruction=(
        "あなたは自動データ分析エージェントです。ステップ1から5を実行して、データ分析を実施します\n"
        "**分析の流れ:**\n"
        "**1. ユーザーのリクエスト理解: ユーザーのリクエストを理解する\n"
        # "**2. SQLクエリ生成、実行、エラー修正 / Agent `data_retrieval_agent`**: データを取得に利用\n"
        # "**3. データ分析と洞察抽出 / Tool `data_analyzer_agent`**: `data_retrieval_agent`で取得したデータでデータ分析をする\n"
        # "**4: レポート生成 / Agent `html_report_agent`**: HTML形式のレポートを作成に利用\n\n"
        "**2. テーブル探索とスキーマ・サンプル確認 / Tool `call_table_explorer_agent`**: ユーザーのリクエストを理解し、toolで分析対象のテーブルを表示\n"
        "**3. 加工と集計 / Tool `call_data_retrieval_agent`**: call_table_explorer_agentでテーブルを特定したら、toolでデータを表示\n"
        "**4. データ分析と洞察抽出 / Tool `call_data_analyzer_agent`**: call_data_retrieval_agentを実行したら、toolで分析結果を表示\n"
        "**5: レポート生成 / Tool `call_html_report_agent`**: toolでHTML形式のレポートの作成結果を表示\n"
    ),
    # sub_agents=[
    # data_retrieval_agent,
    # data_analyzer_agent,
    # html_report_agent,
    # ],
    tools=[
        # postgres_toolset,
        call_data_retrieval_agent,
        call_table_explorer_agent,
        call_html_report_agent,
        call_data_analyzer_agent,
    ],
)
