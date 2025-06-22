"""
カスタムエージェント実装
情報の完全性に基づいて動的にワークフローを制御し、
条件に応じて自動的に次のステップに進む
"""

import json
from typing import Any, AsyncIterator, Dict

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part
from pydantic import Field


class AutoAnalyticsCustomAgent(BaseAgent):
    """
    情報の完全性に基づいて自動的に次のステップに進むカスタムエージェント

    このエージェントは以下の機能を提供：
    1. 情報完全性の自動判定
    2. 条件に応じた動的ワークフロー制御
    3. 必要な場合のみユーザー確認を実施
    4. エラー時の適切なフォールバック
    """

    # サブエージェントのフィールド定義
    request_interpreter: Any = Field(default=None)
    information_gap_detector: Any = Field(default=None)
    user_confirmation_agent: Any = Field(default=None)
    schema_explorer: Any = Field(default=None)
    data_sampler: Any = Field(default=None)
    sql_generator: Any = Field(default=None)
    sql_error_handler: Any = Field(default=None)
    data_analyzer: Any = Field(default=None)
    html_report_generator: Any = Field(default=None)

    def __init__(self, sub_agents: Dict[str, Any]):
        """
        カスタムエージェントの初期化

        Args:
            sub_agents: 各フェーズで使用するサブエージェントの辞書
        """
        # サブエージェントリストを先に準備（BaseAgentの初期化で必要）
        sub_agents_list = list(sub_agents.values())

        super().__init__(
            name="auto_analytics_custom",
            description="データ分析の動的ワークフロー制御エージェント",
            sub_agents=sub_agents_list,  # BaseAgentに直接渡す
            # サブエージェントのフィールドを設定
            request_interpreter=sub_agents["request_interpreter"],
            information_gap_detector=sub_agents["information_gap_detector"],
            user_confirmation_agent=sub_agents["user_confirmation_agent"],
            schema_explorer=sub_agents["schema_explorer"],
            data_sampler=sub_agents["data_sampler"],
            sql_generator=sub_agents["sql_generator"],
            sql_error_handler=sub_agents["sql_error_handler"],
            data_analyzer=sub_agents["data_analyzer"],
            html_report_generator=sub_agents["html_report_generator"],
        )

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        """
        動的ワークフロー実行の実装

        情報の完全性に基づいて、自動的に適切なワークフローパスを選択
        """

        # Phase 1: リクエスト解釈
        yield Event(
            author="auto_analytics_agent",
            content=Content(parts=[Part(text="📝 分析リクエストを解釈しています...")]),
        )

        async for event in self.request_interpreter.run_async(ctx):
            yield event

        # Phase 2: 情報完全性チェック
        yield Event(
            author="auto_analytics_agent",
            content=Content(
                parts=[Part(text="🔍 情報の完全性をチェックしています...")]
            ),
        )

        async for event in self.information_gap_detector.run_async(ctx):
            yield event

        # 情報完全性の判定
        gap_analysis = ctx.session.state.get("information_gap_analysis", "")

        # 自動判定ロジック
        is_sufficient, confidence = self._analyze_information_completeness(gap_analysis)

        if is_sufficient:
            # 情報が十分な場合、自動的に分析フローに進む
            message = (
                f"✅ 情報が十分です（信頼度: {confidence:.0%}）。"
                "自動的にデータ分析を開始します。"
            )
            yield Event(
                author="auto_analytics_agent",
                content=Content(parts=[Part(text=message)]),
            )

            # 通常の分析フローを自動実行
            async for event in self._run_analysis_workflow(ctx):
                yield event

        else:
            # 情報が不足している場合、ユーザー確認フローへ
            message = (
                f"❓ 追加情報が必要です（信頼度: {confidence:.0%}）。"
                "確認事項をお送りします。"
            )
            yield Event(
                author="auto_analytics_agent",
                content=Content(parts=[Part(text=message)]),
            )

            # ユーザー確認質問を生成
            async for event in self.user_confirmation_agent.run_async(ctx):
                yield event

            # ユーザー入力待機状態を示す
            message = (
                "ユーザーからの追加情報をお待ちしています... "
                "ユーザー入力後、自動的に分析を再開します"
            )
            yield Event(
                author="auto_analytics_agent",
                content=Content(parts=[Part(text=message)]),
            )

    def _analyze_information_completeness(
        self, gap_analysis: str
    ) -> tuple[bool, float]:
        """
        情報の完全性を自動判定

        Args:
            gap_analysis: 情報不足検出エージェントの出力

        Returns:
            (情報が十分かどうか, 信頼度スコア)
        """
        try:
            # JSON形式の場合
            if gap_analysis.strip().startswith("{"):
                data = json.loads(gap_analysis)
                status = data.get("status", "").lower()
                confidence = float(data.get("confidence_score", 0))

                # 高信頼度で情報が十分な場合は自動進行
                is_sufficient = status == "sufficient" and confidence >= 0.7
                return is_sufficient, confidence

            else:
                # テキスト形式の場合、キーワードで判定
                text_lower = gap_analysis.lower()

                # キーワードベースの判定
                sufficient_keywords = [
                    "sufficient",
                    "十分",
                    "完全",
                    "問題なし",
                    "分析可能",
                    "情報が揃",
                ]
                insufficient_keywords = [
                    "needs_clarification",
                    "要確認",
                    "不足",
                    "曖昧",
                    "不明",
                    "追加情報",
                ]

                # スコア計算
                sufficient_count = sum(
                    1 for kw in sufficient_keywords if kw in text_lower
                )
                insufficient_count = sum(
                    1 for kw in insufficient_keywords if kw in text_lower
                )

                # 信頼度スコアの計算
                if sufficient_count + insufficient_count == 0:
                    confidence = 0.5  # デフォルト
                else:
                    confidence = sufficient_count / (
                        sufficient_count + insufficient_count
                    )

                # 十分キーワードが多く、不足キーワードが少ない場合は自動進行
                is_sufficient = (
                    sufficient_count > insufficient_count and confidence >= 0.7
                )

                return is_sufficient, confidence

        except Exception as e:
            # エラー時は安全側に倒して確認を求める
            print(f"情報完全性の判定中にエラー: {e}")
            return False, 0.0

    async def _run_analysis_workflow(self, ctx: InvocationContext):
        """
        通常の分析ワークフローを実行

        各フェーズを順次実行し、進捗状況を報告
        """

        # Phase 3: スキーマ探索
        yield Event(
            author="auto_analytics_agent",
            content=Content(
                parts=[Part(text="🗄️ データベーススキーマを調査しています...")]
            ),
        )

        async for event in self.schema_explorer.run_async(ctx):
            yield event

        # Phase 4: サンプルデータ確認
        yield Event(
            author="auto_analytics_agent",
            content=Content(parts=[Part(text="📊 サンプルデータを確認しています...")]),
        )

        async for event in self.data_sampler.run_async(ctx):
            yield event

        # Phase 5: SQL生成
        yield Event(
            author="auto_analytics_agent",
            content=Content(parts=[Part(text="🔨 SQLクエリを生成しています...")]),
        )

        async for event in self.sql_generator.run_async(ctx):
            yield event

        # Phase 6: SQL実行（エラーハンドリング付き）
        yield Event(
            author="auto_analytics_agent",
            content=Content(parts=[Part(text="⚡ SQLクエリを実行しています...")]),
        )

        async for event in self.sql_error_handler.run_async(ctx):
            yield event

        # Phase 7: データ分析
        yield Event(
            author="auto_analytics_agent",
            content=Content(parts=[Part(text="🧠 データを分析しています...")]),
        )

        async for event in self.data_analyzer.run_async(ctx):
            yield event

        # Phase 8: HTMLレポート生成
        yield Event(
            author="auto_analytics_agent",
            content=Content(parts=[Part(text="📄 HTMLレポートを生成しています...")]),
        )

        async for event in self.html_report_generator.run_async(ctx):
            yield event

        # 完了通知
        yield Event(
            author="auto_analytics_agent",
            content=Content(
                parts=[
                    Part(text="✅ データ分析が完了しました！レポートが生成されました。")
                ]
            ),
        )

    async def resume_after_user_input(
        self, ctx: InvocationContext, user_response: str
    ) -> AsyncIterator[Event]:
        """
        ユーザー入力後のワークフロー再開

        Args:
            ctx: 実行コンテキスト
            user_response: ユーザーからの追加情報
        """

        # ユーザー入力を統合
        original_request = ctx.session.state.get("interpreted_request", "")

        # 情報を統合して完全なリクエストを作成
        completed_request = self._integrate_user_feedback(
            original_request, user_response
        )

        # コンテキストを更新
        ctx.session.state["interpreted_request"] = completed_request
        ctx.session.state["information_complete"] = True

        yield Event(
            author="auto_analytics_agent",
            content=Content(
                parts=[Part(text="📝 追加情報を受け取りました。分析を再開します。")]
            ),
        )

        # 分析ワークフローを自動的に開始
        async for event in self._run_analysis_workflow(ctx):
            yield event

    def _integrate_user_feedback(
        self, original_request: str, user_response: str
    ) -> str:
        """
        元のリクエストとユーザーの追加情報を統合

        Args:
            original_request: 元の分析リクエスト
            user_response: ユーザーからの追加情報

        Returns:
            統合された完全なリクエスト
        """
        return f"""
【完成した分析リクエスト】

元のリクエスト: {original_request}

追加情報: {user_response}

統合された要件:
• {original_request}
• 追加条件: {user_response}

これらの情報を基に、包括的なデータ分析を実行します。
"""
