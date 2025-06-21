# Auto Analytics API統合設計書

## 1. API統合概要

Auto AnalyticsはGoogle Gemini 2.5 Flash APIを中核とし、複数のAPI統合により高度な分析機能を実現します。本設計書では、各APIの統合方法、認証・セキュリティ、パフォーマンス最適化について詳述します。

## 2. Gemini 2.5 Flash API統合

### 2.1 API基本設定

```python
class GeminiAPIClient:
    def __init__(self, api_key: str, project_id: str = None):
        self.api_key = api_key
        self.project_id = project_id
        self.model_name = "gemini-2.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.client = self._initialize_client()
        
        # レート制限管理
        self.rate_limiter = RateLimiter(
            requests_per_minute=60,
            tokens_per_minute=32000
        )
        
        # リトライ設定
        self.retry_config = RetryConfig(
            max_retries=3,
            backoff_factor=2,
            retry_on_status=[429, 500, 502, 503, 504]
        )
    
    def _initialize_client(self):
        return genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
        )
```

### 2.2 エージェント別API設定

#### Natural Language Processing Agent用設定

```python
class NLPAgentAPI:
    def __init__(self, gemini_client):
        self.client = gemini_client
        self.system_prompt = """
あなたは自然言語処理の専門家です。
ユーザーのデータ分析要求を理解し、構造化された情報として出力してください。

出力形式は必ずJSONとし、以下の構造に従ってください:
{
  "intent": "分析の意図",
  "entities": {
    "metrics": ["対象指標"],
    "dimensions": ["分析軸"],
    "time_period": "時間範囲",
    "filters": ["フィルター条件"]
  },
  "analysis_type": "分析種別",
  "confidence": 0.0-1.0,
  "clarification_needed": boolean,
  "clarification_questions": ["必要な場合の質問"]
}
"""
        
    async def process_user_input(self, user_input: str, context: dict = None):
        prompt = self._build_nlp_prompt(user_input, context)
        
        response = await self.client.generate_response(
            prompt=prompt,
            temperature=0.1,  # 一貫性を重視
            max_tokens=2048
        )
        
        return self._parse_structured_response(response)
```

#### Data Analyst Agent用設定

```python
class DataAnalystAPI:
    def __init__(self, gemini_client):
        self.client = gemini_client
        self.system_prompt = """
あなたはデータ分析の専門家です。
構造化された分析要求に基づいて、最適なSQLクエリと分析手法を提案してください。

利用可能なデータベーススキーマ: {schema}

出力形式:
{
  "sql_query": "最適化されたSQLクエリ",
  "analysis_methods": ["適用する分析手法"],
  "expected_insights": ["期待される洞察"],
  "visualization_suggestions": ["推奨可視化"],
  "performance_notes": "パフォーマンスに関する注意"
}
"""
        
    async def generate_sql_query(self, structured_request: dict, schema: dict):
        prompt = self._build_analyst_prompt(structured_request, schema)
        
        response = await self.client.generate_response(
            prompt=prompt,
            temperature=0.05,  # 正確性を最重視
            max_tokens=4096
        )
        
        return self._validate_sql_response(response)
```

#### Report Generation Agent用設定

```python
class ReportGenerationAPI:
    def __init__(self, gemini_client):
        self.client = gemini_client
        self.system_prompt = """
あなたはビジネスレポート作成の専門家です。
分析結果を基に、経営陣向けの分かりやすいレポートを作成してください。

レポート構成:
1. エグゼクティブサマリー
2. 主要な発見事項
3. 詳細分析結果
4. アクションアイテム
5. 次のステップ

出力形式はHTML形式とし、グラフや表を含めてください。
"""
        
    async def generate_report(self, analysis_results: dict, insights: dict):
        prompt = self._build_report_prompt(analysis_results, insights)
        
        response = await self.client.generate_response(
            prompt=prompt,
            temperature=0.3,  # 創造性とのバランス
            max_tokens=8192
        )
        
        return self._process_html_response(response)
```

### 2.3 プロンプトエンジニアリング戦略

#### 構造化プロンプトテンプレート

```python
class PromptTemplateManager:
    def __init__(self):
        self.templates = {
            'nlp_analysis': self._load_nlp_template(),
            'sql_generation': self._load_sql_template(),
            'report_generation': self._load_report_template(),
            'insight_extraction': self._load_insight_template()
        }
        
    def _load_nlp_template(self):
        return """
## タスク
ユーザーの自然言語入力から分析要求を抽出し、構造化してください。

## 入力
- ユーザー入力: {user_input}
- 会話履歴: {conversation_history}
- 利用可能データ: {available_data}

## 出力要件
- 必ずJSON形式で出力
- 曖昧な部分は明確化質問を生成
- 信頼度スコアを0.0-1.0で算出

## 分析対象の例
- 売上分析、顧客分析、トレンド分析、予測分析
- 地域別、期間別、商品別などの軸
- 成長率、シェア、相関などの指標

{format_instructions}
"""
        
    def _load_sql_template(self):
        return """
## タスク
分析要求に基づいて最適なSQLクエリを生成してください。

## データベーススキーマ
{database_schema}

## 分析要求
{structured_request}

## SQL生成ガイドライン
1. パフォーマンスを考慮したクエリ作成
2. 適切なインデックス利用
3. 必要最小限のデータ取得
4. セキュリティ（SQLインジェクション対策）

## 出力要件
- 実行可能なSQLクエリ
- クエリの説明
- 期待される実行時間
- 結果の列説明

{format_instructions}
"""

    def build_prompt(self, template_name: str, variables: dict):
        template = self.templates[template_name]
        return template.format(**variables)
```

### 2.4 レスポンス処理・パース

```python
class ResponseProcessor:
    def __init__(self):
        self.json_parser = JSONParser()
        self.sql_validator = SQLValidator()
        self.html_sanitizer = HTMLSanitizer()
    
    async def process_nlp_response(self, response: str):
        try:
            parsed_data = self.json_parser.parse(response)
            validated_data = self._validate_nlp_structure(parsed_data)
            return validated_data
        except Exception as e:
            # フォールバック処理
            return await self._fallback_nlp_processing(response, e)
    
    async def process_sql_response(self, response: str):
        try:
            parsed_data = self.json_parser.parse(response)
            sql_query = parsed_data.get('sql_query')
            
            # SQL構文検証
            validation_result = await self.sql_validator.validate(sql_query)
            if not validation_result.is_valid:
                return await self._fix_sql_query(sql_query, validation_result.errors)
            
            return parsed_data
        except Exception as e:
            return await self._handle_sql_error(response, e)
    
    async def process_html_response(self, response: str):
        # HTMLの抽出と検証
        html_content = self._extract_html(response)
        sanitized_html = self.html_sanitizer.sanitize(html_content)
        
        return {
            'html_content': sanitized_html,
            'summary': self._extract_summary(response),
            'action_items': self._extract_action_items(response)
        }
```

## 3. API認証・セキュリティ

### 3.1 認証管理

```python
class APIAuthManager:
    def __init__(self):
        self.credentials = self._load_credentials()
        self.token_manager = TokenManager()
        
    def _load_credentials(self):
        return {
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'vertex_ai_credentials': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            'project_id': os.getenv('GOOGLE_CLOUD_PROJECT')
        }
    
    async def get_authenticated_client(self, service: str):
        if service == 'gemini':
            return await self._get_gemini_client()
        elif service == 'vertex_ai':
            return await self._get_vertex_ai_client()
        else:
            raise ValueError(f"Unknown service: {service}")
    
    async def _get_gemini_client(self):
        api_key = self.credentials['gemini_api_key']
        if not api_key:
            raise AuthenticationError("Gemini API key not found")
        
        # APIキーの有効性確認
        if not await self._validate_api_key(api_key):
            raise AuthenticationError("Invalid Gemini API key")
        
        return GeminiAPIClient(api_key)
```

### 3.2 データプライバシー保護

```python
class DataPrivacyManager:
    def __init__(self):
        self.pii_detector = PIIDetector()
        self.data_masker = DataMasker()
        
    async def sanitize_for_api(self, data: dict):
        # PII検出
        pii_fields = await self.pii_detector.detect(data)
        
        if pii_fields:
            # データマスキング
            sanitized_data = await self.data_masker.mask_data(data, pii_fields)
            
            # 監査ログ
            await self._log_data_sanitization(data, pii_fields)
            
            return sanitized_data
        
        return data
    
    def check_data_sensitivity(self, query: str, data: dict):
        sensitivity_score = self._calculate_sensitivity_score(query, data)
        
        if sensitivity_score > 0.8:
            return {'allowed': False, 'reason': 'High sensitivity data'}
        elif sensitivity_score > 0.5:
            return {'allowed': True, 'warning': 'Moderate sensitivity data'}
        else:
            return {'allowed': True}
```

## 4. パフォーマンス最適化

### 4.1 レート制限管理

```python
class RateLimitManager:
    def __init__(self):
        self.limiters = {
            'gemini': RateLimiter(
                requests_per_minute=60,
                tokens_per_minute=32000,
                requests_per_day=1000
            )
        }
        
    async def acquire_permit(self, service: str, estimated_tokens: int = 0):
        limiter = self.limiters.get(service)
        if not limiter:
            return True
        
        # リクエスト制限チェック
        if not await limiter.can_make_request():
            wait_time = await limiter.get_wait_time()
            await asyncio.sleep(wait_time)
        
        # トークン制限チェック
        if estimated_tokens > 0:
            if not await limiter.can_use_tokens(estimated_tokens):
                wait_time = await limiter.get_token_wait_time()
                await asyncio.sleep(wait_time)
        
        return await limiter.acquire()
```

### 4.2 キャッシュ戦略

```python
class APIResponseCache:
    def __init__(self):
        self.cache = Redis(host='localhost', port=6379, db=0)
        self.default_ttl = 3600  # 1時間
        
    async def get_cached_response(self, prompt_hash: str):
        cached_data = await self.cache.get(f"api_response:{prompt_hash}")
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def cache_response(self, prompt_hash: str, response: dict, ttl: int = None):
        ttl = ttl or self.default_ttl
        await self.cache.setex(
            f"api_response:{prompt_hash}",
            ttl,
            json.dumps(response)
        )
    
    def generate_prompt_hash(self, prompt: str, model_config: dict):
        # プロンプトと設定の組み合わせからハッシュ生成
        combined = f"{prompt}:{json.dumps(model_config, sort_keys=True)}"
        return hashlib.sha256(combined.encode()).hexdigest()
```

### 4.3 バッチ処理最適化

```python
class BatchAPIProcessor:
    def __init__(self, api_client):
        self.api_client = api_client
        self.batch_size = 10
        self.max_concurrent = 5
        
    async def process_batch_requests(self, requests: List[dict]):
        # リクエストのバッチ化
        batches = self._create_batches(requests, self.batch_size)
        
        # セマフォによる同時実行制限
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_single_batch(batch):
            async with semaphore:
                return await self._process_batch(batch)
        
        # 全バッチの並列処理
        batch_results = await asyncio.gather(
            *[process_single_batch(batch) for batch in batches],
            return_exceptions=True
        )
        
        return self._merge_batch_results(batch_results)
```

## 5. エラーハンドリング・復旧

### 5.1 統合エラーハンドリング

```python
class APIErrorHandler:
    def __init__(self):
        self.retry_strategies = {
            429: ExponentialBackoffRetry(max_retries=5),
            500: LinearBackoffRetry(max_retries=3),
            503: ExponentialBackoffRetry(max_retries=3)
        }
        
    async def handle_api_error(self, error: Exception, context: dict):
        if isinstance(error, RateLimitError):
            return await self._handle_rate_limit_error(error, context)
        elif isinstance(error, AuthenticationError):
            return await self._handle_auth_error(error, context)
        elif isinstance(error, ValidationError):
            return await self._handle_validation_error(error, context)
        else:
            return await self._handle_generic_error(error, context)
    
    async def _handle_rate_limit_error(self, error, context):
        wait_time = self._calculate_backoff_time(error)
        await asyncio.sleep(wait_time)
        
        # リトライ
        return await self._retry_request(context)
    
    async def _handle_validation_error(self, error, context):
        # プロンプトの自動修正
        corrected_prompt = await self._correct_prompt(context['prompt'], error)
        context['prompt'] = corrected_prompt
        
        return await self._retry_request(context)
```

### 5.2 フォールバック機能

```python
class APIFallbackManager:
    def __init__(self):
        self.fallback_strategies = {
            'gemini_unavailable': self._use_alternative_model,
            'quota_exceeded': self._use_cached_responses,
            'response_invalid': self._use_simplified_prompt
        }
    
    async def execute_with_fallback(self, primary_function, *args, **kwargs):
        try:
            return await primary_function(*args, **kwargs)
        except Exception as e:
            fallback_strategy = self._determine_fallback_strategy(e)
            if fallback_strategy:
                return await fallback_strategy(*args, **kwargs)
            else:
                # 最終フォールバック: シンプルな固定レスポンス
                return self._generate_error_response(e)
```

## 6. 監視・ロギング

### 6.1 API使用量監視

```python
class APIUsageMonitor:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        
    async def track_api_call(self, service: str, endpoint: str, 
                           duration: float, tokens_used: int, 
                           status_code: int):
        
        metrics = {
            'api_call_duration': duration,
            'api_tokens_used': tokens_used,
            'api_call_count': 1,
            'api_error_count': 1 if status_code >= 400 else 0
        }
        
        tags = {
            'service': service,
            'endpoint': endpoint,
            'status_code': status_code
        }
        
        for metric_name, value in metrics.items():
            await self.metrics_collector.record_metric(
                metric_name, value, tags
            )
    
    async def generate_usage_report(self, time_period: str):
        # 使用量レポートの生成
        usage_data = await self.metrics_collector.query_metrics(
            metrics=['api_call_count', 'api_tokens_used'],
            time_range=time_period
        )
        
        return {
            'total_calls': sum(usage_data['api_call_count']),
            'total_tokens': sum(usage_data['api_tokens_used']),
            'average_response_time': np.mean(usage_data['api_call_duration']),
            'error_rate': self._calculate_error_rate(usage_data)
        }
```

### 6.2 品質監視

```python
class APIQualityMonitor:
    def __init__(self):
        self.quality_metrics = {
            'response_accuracy': AccuracyTracker(),
            'response_relevance': RelevanceTracker(),
            'response_completeness': CompletenessTracker()
        }
    
    async def evaluate_response_quality(self, request: dict, response: dict):
        quality_scores = {}
        
        for metric_name, tracker in self.quality_metrics.items():
            score = await tracker.evaluate(request, response)
            quality_scores[metric_name] = score
        
        overall_quality = np.mean(list(quality_scores.values()))
        
        # 低品質レスポンスのアラート
        if overall_quality < 0.7:
            await self._send_quality_alert(request, response, quality_scores)
        
        return quality_scores
```

## 7. 設定管理

### 7.1 環境別設定

```yaml
# config/api_config.yaml
development:
  gemini:
    model: "gemini-2.5-flash"
    temperature: 0.1
    max_tokens: 4096
    rate_limit:
      requests_per_minute: 30
      tokens_per_minute: 16000
  
production:
  gemini:
    model: "gemini-2.5-flash"
    temperature: 0.05
    max_tokens: 8192
    rate_limit:
      requests_per_minute: 60
      tokens_per_minute: 32000
    fallback:
      enabled: true
      cache_fallback: true
```

### 7.2 動的設定更新

```python
class ConfigManager:
    def __init__(self):
        self.config = self._load_config()
        self.config_watchers = []
        
    def _load_config(self):
        env = os.getenv('ENVIRONMENT', 'development')
        with open(f'config/api_config.yaml', 'r') as f:
            all_configs = yaml.safe_load(f)
        return all_configs[env]
    
    async def update_config(self, new_config: dict):
        self.config.update(new_config)
        
        # 設定変更の通知
        for watcher in self.config_watchers:
            await watcher.on_config_change(new_config)
    
    def register_config_watcher(self, watcher):
        self.config_watchers.append(watcher)
```