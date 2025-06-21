# Auto Analytics エージェント設計書

## 1. マルチエージェントシステム概要

Auto Analyticsは専門性を持つ複数のエージェントが協調動作するマルチエージェントシステムです。各エージェントは特定の役割を担い、Gemini 2.5 Flashを活用して高度な分析機能を提供します。

## 2. エージェント構成

### 2.1 Agent Orchestrator（オーケストレーター）

#### 役割
- システム全体の制御とワークフロー管理
- エージェント間の協調と情報共有
- ユーザーとの主要な対話窓口

#### 機能詳細

```python
class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            'nlp': NaturalLanguageProcessingAgent(),
            'analyst': DataAnalystAgent(),
            'reporter': ReportGenerationAgent()
        }
        self.conversation_context = ConversationContext()
        self.workflow_state = WorkflowState()
    
    async def handle_user_request(self, user_input: str):
        # 1. 要求の分析と適切なエージェントへの振り分け
        request_analysis = await self.analyze_request(user_input)
        
        # 2. ワークフローの決定
        workflow = self.determine_workflow(request_analysis)
        
        # 3. エージェントの順次実行
        result = await self.execute_workflow(workflow)
        
        return result
    
    def determine_workflow(self, request_analysis):
        # 非決定論的アプローチによる動的ワークフロー決定
        if request_analysis.requires_clarification:
            return ['nlp', 'analyst', 'reporter']
        elif request_analysis.is_complex_analysis:
            return ['nlp', 'analyst', 'analyst', 'reporter']  # 複数回の分析
        else:
            return ['nlp', 'analyst', 'reporter']
```

#### プロンプト設計

```
あなたはデータ分析のオーケストレーターです。
ユーザーの要求を理解し、適切なエージェントに作業を振り分けてください。

コンテキスト:
- 現在の会話履歴: {conversation_history}
- 利用可能なデータ: {available_data}
- 過去の分析結果: {previous_results}

ユーザー要求: {user_request}

以下の形式で応答してください:
{
  "workflow": ["agent1", "agent2", ...],
  "priority": "high|medium|low",
  "estimated_time": "時間の見積もり",
  "clarification_needed": "必要な場合は明確化すべき点"
}
```

### 2.2 Natural Language Processing Agent

#### 役割
- 自然言語理解と意図抽出
- 曖昧な質問の明確化
- 多言語対応（日本語・英語）

#### 機能詳細

```python
class NaturalLanguageProcessingAgent:
    def __init__(self):
        self.context_manager = ContextManager()
        self.language_detector = LanguageDetector()
        self.intent_classifier = IntentClassifier()
    
    async def process_user_input(self, user_input: str, context: dict):
        # 1. 言語検出
        language = self.language_detector.detect(user_input)
        
        # 2. 意図分類
        intent = await self.classify_intent(user_input, context)
        
        # 3. エンティティ抽出
        entities = await self.extract_entities(user_input)
        
        # 4. 明確化の必要性判定
        clarification = await self.check_clarification_needed(intent, entities)
        
        return {
            'language': language,
            'intent': intent,
            'entities': entities,
            'clarification': clarification,
            'structured_request': self.structure_request(intent, entities)
        }
    
    async def classify_intent(self, user_input: str, context: dict):
        # Gemini 2.5 Flashを使用した意図分類
        pass
```

#### プロンプト設計

```
あなたは自然言語処理の専門家です。
ユーザーの分析要求を理解し、構造化してください。

ユーザーの入力: {user_input}
会話コンテキスト: {context}

以下の観点で分析してください:
1. 分析の種類（記述統計、相関分析、予測分析など）
2. 対象データ（テーブル名、カラム名の推定）
3. 時間範囲や条件の指定
4. 出力形式の要求

明確化が必要な点がある場合は、具体的な質問を提案してください。

回答形式:
{
  "intent": "分析の意図",
  "data_requirements": ["必要なデータ"],
  "analysis_type": "分析種別",
  "clarification_questions": ["明確化の質問"],
  "confidence": 0.0-1.0
}
```

### 2.3 Data Analyst Agent

#### 役割
- SQLクエリの自動生成・最適化
- データ分析の実行
- 統計分析と洞察の抽出

#### 機能詳細

```python
class DataAnalystAgent:
    def __init__(self):
        self.sql_generator = SQLGenerator()
        self.statistical_analyzer = StatisticalAnalyzer()
        self.insight_extractor = InsightExtractor()
        self.mcp_client = MCPClient()
    
    async def execute_analysis(self, structured_request: dict):
        # 1. SQLクエリ生成
        sql_query = await self.generate_sql(structured_request)
        
        # 2. データ取得
        raw_data = await self.mcp_client.execute_query(sql_query)
        
        # 3. データ分析
        analysis_results = await self.analyze_data(raw_data, structured_request)
        
        # 4. 洞察抽出
        insights = await self.extract_insights(analysis_results)
        
        # 5. 追加分析の提案
        additional_analysis = await self.suggest_additional_analysis(insights)
        
        return {
            'sql_query': sql_query,
            'raw_data': raw_data,
            'analysis_results': analysis_results,
            'insights': insights,
            'additional_analysis': additional_analysis
        }
    
    async def generate_sql(self, structured_request: dict):
        # Gemini 2.5 Flashを使用したSQL生成
        pass
```

#### プロンプト設計

```
あなたはデータ分析の専門家です。
構造化された分析要求に基づいて、最適なSQLクエリを生成してください。

分析要求:
- 意図: {intent}
- データ要件: {data_requirements}
- 分析タイプ: {analysis_type}

利用可能なデータベーススキーマ:
{database_schema}

以下の点を考慮してSQLを作成してください:
1. パフォーマンスの最適化
2. データの正確性確保
3. 適切なフィルタリング
4. 必要に応じた集計・グループ化

回答形式:
{
  "sql_query": "最適化されたSQLクエリ",
  "explanation": "クエリの説明",
  "expected_columns": ["結果の列名"],
  "estimated_rows": "推定行数",
  "performance_notes": "パフォーマンスに関する注意点"
}
```

### 2.4 Report Generation Agent

#### 役割
- 分析結果の可視化
- HTMLレポートの生成
- アクションアイテムの提案

#### 機能詳細

```python
class ReportGenerationAgent:
    def __init__(self):
        self.visualizer = DataVisualizer()
        self.report_builder = ReportBuilder()
        self.action_item_generator = ActionItemGenerator()
    
    async def generate_report(self, analysis_results: dict):
        # 1. 可視化の生成
        visualizations = await self.create_visualizations(analysis_results)
        
        # 2. レポート構造の決定
        report_structure = await self.determine_report_structure(analysis_results)
        
        # 3. HTMLレポートの生成
        html_report = await self.build_html_report(
            analysis_results, 
            visualizations, 
            report_structure
        )
        
        # 4. アクションアイテムの生成
        action_items = await self.generate_action_items(analysis_results)
        
        return {
            'html_report': html_report,
            'visualizations': visualizations,
            'action_items': action_items,
            'summary': self.create_summary(analysis_results)
        }
```

#### プロンプト設計

```
あなたはデータ可視化とレポート作成の専門家です。
分析結果を基に、分かりやすいレポートを作成してください。

分析結果:
{analysis_results}

洞察:
{insights}

以下の要素を含むレポートを作成してください:
1. エグゼクティブサマリー
2. 主要な発見事項
3. データの可視化提案
4. 詳細な分析結果
5. アクションアイテム
6. 次のステップの提案

回答形式:
{
  "report_structure": {
    "sections": ["セクション一覧"],
    "visualizations": ["推奨グラフタイプ"],
    "key_findings": ["主要発見事項"],
    "action_items": ["アクションアイテム"]
  },
  "executive_summary": "エグゼクティブサマリー",
  "next_steps": ["次のステップ提案"]
}
```

## 3. エージェント間協調機能

### 3.1 共有コンテキスト管理

```python
class SharedContext:
    def __init__(self):
        self.conversation_history = []
        self.data_schemas = {}
        self.previous_analyses = []
        self.user_preferences = {}
    
    def update_context(self, agent_id: str, context_data: dict):
        # コンテキストの更新
        pass
    
    def get_relevant_context(self, agent_id: str, task_type: str):
        # 関連するコンテキストの取得
        pass
```

### 3.2 メッセージングシステム

```python
class AgentMessaging:
    async def send_message(self, from_agent: str, to_agent: str, message: dict):
        # エージェント間メッセージ送信
        pass
    
    async def broadcast_message(self, from_agent: str, message: dict):
        # 全エージェントへのブロードキャスト
        pass
    
    def subscribe_to_events(self, agent_id: str, event_types: list):
        # イベント購読
        pass
```

## 4. 非決定論的アプローチの実装

### 4.1 探索的分析フロー

```python
class ExploratoryAnalysisFlow:
    async def execute_exploratory_analysis(self, initial_request: dict):
        current_findings = []
        analysis_depth = 0
        max_depth = 5
        
        while analysis_depth < max_depth:
            # 現在の発見事項に基づく次の分析の決定
            next_analysis = await self.determine_next_analysis(
                initial_request, 
                current_findings
            )
            
            if not next_analysis:
                break
            
            # 分析の実行
            result = await self.execute_analysis(next_analysis)
            current_findings.append(result)
            
            # 新しい仮説の生成
            new_hypotheses = await self.generate_hypotheses(result)
            
            analysis_depth += 1
        
        return self.synthesize_findings(current_findings)
```

### 4.2 仮説生成・検証システム

```python
class HypothesisSystem:
    async def generate_hypotheses(self, data_findings: dict):
        # データから仮説を生成
        pass
    
    async def design_verification_analysis(self, hypothesis: dict):
        # 仮説検証のための分析設計
        pass
    
    async def evaluate_hypothesis(self, hypothesis: dict, results: dict):
        # 仮説の評価
        pass
```

## 5. エラーハンドリングと回復

### 5.1 エラー処理戦略

```python
class ErrorHandler:
    async def handle_sql_error(self, sql_query: str, error: Exception):
        # SQLエラーの自動修正
        corrected_query = await self.correct_sql_query(sql_query, error)
        return corrected_query
    
    async def handle_analysis_error(self, analysis_params: dict, error: Exception):
        # 分析エラーの処理
        alternative_approach = await self.suggest_alternative_analysis(
            analysis_params, error
        )
        return alternative_approach
    
    async def handle_api_error(self, api_call: str, error: Exception):
        # API呼び出しエラーの処理
        retry_strategy = self.determine_retry_strategy(error)
        return retry_strategy
```

### 5.2 フォールバック機能

- **簡略化分析**: 複雑な分析が失敗した場合の簡単な代替分析
- **部分結果の活用**: 一部のデータが取得できない場合の対処
- **ユーザーへの明確な説明**: エラー状況の分かりやすい説明

## 6. パフォーマンス最適化

### 6.1 並列処理

- **並列クエリ実行**: 独立したクエリの同時実行
- **並列分析**: 複数の分析手法の同時適用
- **非同期処理**: ユーザー応答性の向上

### 6.2 キャッシュ戦略

- **クエリ結果キャッシュ**: 同一クエリの結果再利用
- **分析結果キャッシュ**: 類似分析の結果活用
- **コンテキストキャッシュ**: 会話コンテキストの効率的管理

## 7. 監視と最適化

### 7.1 エージェントパフォーマンス監視

```python
class AgentMonitor:
    def track_agent_performance(self, agent_id: str, task: str, duration: float):
        # エージェントパフォーマンスの追跡
        pass
    
    def analyze_bottlenecks(self):
        # ボトルネックの分析
        pass
    
    def suggest_optimizations(self):
        # 最適化提案
        pass
```

### 7.2 継続的改善

- **学習機能**: ユーザーフィードバックからの学習
- **プロンプト最適化**: 使用実績に基づくプロンプト改善
- **ワークフロー最適化**: 効率的なエージェント連携の学習