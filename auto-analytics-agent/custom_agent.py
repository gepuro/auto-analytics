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
    schema_explorer: Any = Field(default=None)
    data_sampler: Any = Field(default=None)
    sql_generator: Any = Field(default=None)
    sql_error_handler: Any = Field(default=None)
    data_analyzer: Any = Field(default=None)
    html_report_generator: Any = Field(default=None)
    phase_coordinator: Any = Field(default=None)

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
            schema_explorer=sub_agents["schema_explorer"],
            data_sampler=sub_agents["data_sampler"],
            sql_generator=sub_agents["sql_generator"],
            sql_error_handler=sub_agents["sql_error_handler"],
            data_analyzer=sub_agents["data_analyzer"],
            html_report_generator=sub_agents["html_report_generator"],
            phase_coordinator=sub_agents["phase_coordinator"],
        )

    # 各フェーズ実行メソッド
    async def _run_phase_1(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        """Phase 1: リクエスト解釈"""
        yield Event(
            author="auto_analytics_agent",
            content=Content(
                parts=[Part(text="📝 Phase 1: 分析リクエストを解釈しています...")]
            ),
        )
        async for event in self.request_interpreter.run_async(ctx):
            yield event

    async def _run_phase_2(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        """Phase 2: 情報完全性チェック"""
        yield Event(
            author="auto_analytics_agent",
            content=Content(
                parts=[Part(text="🔍 Phase 2: 情報の完全性をチェックしています...")]
            ),
        )
        async for event in self.information_gap_detector.run_async(ctx):
            yield event


    async def _run_phase_3(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        """Phase 3: スキーマ探索"""
        yield Event(
            author="auto_analytics_agent",
            content=Content(
                parts=[Part(text="🗄️ Phase 3: データベーススキーマを調査しています...")]
            ),
        )
        async for event in self.schema_explorer.run_async(ctx):
            yield event

    async def _run_phase_4(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        """Phase 4: サンプルデータ確認"""
        yield Event(
            author="auto_analytics_agent",
            content=Content(
                parts=[Part(text="📊 Phase 4: サンプルデータを確認しています...")]
            ),
        )
        async for event in self.data_sampler.run_async(ctx):
            yield event

    async def _run_phase_5(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        """Phase 5: SQL生成"""
        yield Event(
            author="auto_analytics_agent",
            content=Content(
                parts=[Part(text="🔨 Phase 5: SQLクエリを生成しています...")]
            ),
        )
        async for event in self.sql_generator.run_async(ctx):
            yield event

    async def _run_phase_6(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        """Phase 6: SQL実行"""
        yield Event(
            author="auto_analytics_agent",
            content=Content(
                parts=[Part(text="⚡ Phase 6: SQLクエリを実行しています...")]
            ),
        )
        async for event in self.sql_error_handler.run_async(ctx):
            yield event

    async def _run_phase_7(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        """Phase 7: データ分析"""
        yield Event(
            author="auto_analytics_agent",
            content=Content(parts=[Part(text="🧠 Phase 7: データを分析しています...")]),
        )
        async for event in self.data_analyzer.run_async(ctx):
            yield event

    async def _run_phase_8(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        """Phase 8: HTMLレポート生成"""
        yield Event(
            author="auto_analytics_agent",
            content=Content(
                parts=[Part(text="📄 Phase 8: HTMLレポートを生成しています...")]
            ),
        )
        async for event in self.html_report_generator.run_async(ctx):
            yield event

    async def _run_dynamic_workflow(
        self, ctx: InvocationContext
    ) -> AsyncIterator[Event]:
        """
        動的ワークフローループ - フェーズ判定による適応的実行
        """
        # フェーズ実行状況を追跡
        if "executed_phases" not in ctx.session.state:
            ctx.session.state["executed_phases"] = []

        # フェーズ実行メソッドのマッピング
        phase_methods = {
            "request_interpreter": self._run_phase_1,
            "information_gap_detector": self._run_phase_2,
            "schema_explorer": self._run_phase_3,
            "data_sampler": self._run_phase_4,
            "sql_generator": self._run_phase_5,
            "sql_error_handler": self._run_phase_6,
            "data_analyzer": self._run_phase_7,
            "html_report_generator": self._run_phase_8,
        }

        # 最初は Phase 1 から開始
        current_phase = "request_interpreter"
        max_iterations = 20  # 無限ループ防止
        iteration_count = 0

        yield Event(
            author="auto_analytics_agent",
            content=Content(parts=[Part(text="🚀 動的ワークフローを開始します...")]),
        )

        while iteration_count < max_iterations:
            iteration_count += 1

            # 現在のフェーズを実行
            if current_phase in phase_methods:
                yield Event(
                    author="auto_analytics_agent",
                    content=Content(
                        parts=[Part(text=f"▶️ {current_phase} を実行中...")]
                    ),
                )

                async for event in phase_methods[current_phase](ctx):
                    yield event

                # 実行済みフェーズに追加
                if current_phase not in ctx.session.state["executed_phases"]:
                    ctx.session.state["executed_phases"].append(current_phase)

            # Phase Coordinator で次のフェーズを判定
            # コンテキスト情報を整理してより良い判定を支援
            self._prepare_context_for_coordinator(ctx, current_phase)

            yield Event(
                author="auto_analytics_agent",
                content=Content(
                    parts=[Part(text="🤔 次のフェーズを判定しています...")]
                ),
            )

            async for event in self.phase_coordinator.run_async(ctx):
                yield event

            # 判定結果を取得
            phase_decision = ctx.session.state.get("phase_decision", "")
            next_phase_info = self._parse_phase_decision(phase_decision)

            next_phase = next_phase_info.get("next_phase", "")
            auto_proceed = next_phase_info.get("auto_proceed", False)
            confidence = next_phase_info.get("confidence", 0.0)
            reason = next_phase_info.get("reason", "")

            # confidence >= 0.7 の場合は自動進行を有効化
            if confidence >= 0.7:
                auto_proceed = True
                confidence_message = (
                    f"🎯 高信頼度判定 (confidence: {confidence:.2f}) - 自動進行します"
                )
            else:
                confidence_message = (
                    f"🤔 低信頼度判定 (confidence: {confidence:.2f}) - 慎重に進行します"
                )

            # 判定結果を報告
            yield Event(
                author="auto_analytics_agent",
                content=Content(
                    parts=[
                        Part(text=f"📋 次のアクション: {next_phase} (理由: {reason})")
                    ]
                ),
            )

            # confidence判定結果を報告
            yield Event(
                author="auto_analytics_agent",
                content=Content(parts=[Part(text=confidence_message)]),
            )

            # 特殊な判定結果の処理
            if next_phase == "complete":
                yield Event(
                    author="auto_analytics_agent",
                    content=Content(
                        parts=[Part(text="✅ ワークフローが完了しました！")]
                    ),
                )
                break
            elif next_phase == "user_confirmation":
                yield Event(
                    author="auto_analytics_agent",
                    content=Content(
                        parts=[Part(text="⏳ ユーザー入力をお待ちしています...")]
                    ),
                )
                break
            elif next_phase.startswith("retry_"):
                # リトライ指示の場合
                retry_phase = next_phase.replace("retry_", "")
                if retry_phase in phase_methods:
                    current_phase = retry_phase
                    continue

            # 自動進行チェック
            if not auto_proceed:
                yield Event(
                    author="auto_analytics_agent",
                    content=Content(
                        parts=[Part(text="⚠️ 手動確認が必要です。一時停止します。")]
                    ),
                )
                break

            # 次のフェーズに進む
            if next_phase in phase_methods:
                current_phase = next_phase
            else:
                yield Event(
                    author="auto_analytics_agent",
                    content=Content(
                        parts=[Part(text=f"❌ 未知のフェーズです: {next_phase}")]
                    ),
                )
                break

        if iteration_count >= max_iterations:
            yield Event(
                author="auto_analytics_agent",
                content=Content(
                    parts=[
                        Part(
                            text="⚠️ 最大反復回数に達しました。ワークフローを終了します。"
                        )
                    ]
                ),
            )

    def _prepare_context_for_coordinator(
        self, ctx: InvocationContext, current_phase: str
    ):
        """フェーズコーディネーター用のコンテキスト情報を準備"""
        # 実行状況の要約を作成
        executed_phases = ctx.session.state.get("executed_phases", [])

        # エラー状況をチェック
        has_sql_error = (
            "sql_error"
            in str(ctx.session.state.get("query_execution_result", "")).lower()
        )

        # 情報完全性をチェック
        gap_analysis = ctx.session.state.get("information_gap_analysis", "")
        is_info_sufficient = "sufficient" in gap_analysis.lower()

        # スキーマの複雑性を評価
        schema_info = ctx.session.state.get("schema_info", "")
        is_complex_schema = any(
            word in schema_info.lower() for word in ["join", "複数", "関連", "foreign"]
        )

        # コーディネーター用のメタ情報を設定
        ctx.session.state["workflow_metadata"] = {
            "current_phase": current_phase,
            "executed_phases": executed_phases,
            "total_phases_executed": len(executed_phases),
            "has_sql_error": has_sql_error,
            "information_sufficient": is_info_sufficient,
            "complex_schema": is_complex_schema,
            "iteration_count": len(executed_phases),
        }

    def _get_fallback_next_phase(self, current_phase: str) -> str:
        """エラー時のフォールバック次フェーズを取得"""
        fallback_sequence = {
            "request_interpreter": "information_gap_detector",
            "information_gap_detector": "schema_explorer",
            "schema_explorer": "data_sampler",
            "data_sampler": "sql_generator",
            "sql_generator": "sql_error_handler",
            "sql_error_handler": "data_analyzer",
            "data_analyzer": "html_report_generator",
            "html_report_generator": "complete",
        }
        return fallback_sequence.get(current_phase, "complete")

    def _parse_phase_decision(self, decision_output: str) -> Dict[str, Any]:
        """フェーズ判定結果をパースする"""
        try:
            if decision_output.strip().startswith("{"):
                return json.loads(decision_output)
            else:
                # JSON以外の場合は手動パース
                return {
                    "next_phase": "complete",
                    "reason": "JSON以外の出力のため終了",
                    "auto_proceed": False,
                }
        except Exception as e:
            print(f"フェーズ判定パースエラー: {e}")
            return None

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        """
        動的ワークフロー実行の実装

        情報の完全性に基づいて、自動的に適切なワークフローパスを選択
        """
        # 動的ワークフローを実行
        async for event in self._run_dynamic_workflow(ctx):
            yield event
