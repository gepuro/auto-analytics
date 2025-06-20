# Auto Analytics AI Agent - 設計仕様書

## 1. システム概要

### 1.1 プロジェクト名
Auto Analytics（オートアナリティクス）

### 1.2 目的
データ分析の民主化を実現し、専門知識の有無に関わらず全社員がデータから洞察を得られるようにする

### 1.3 アーキテクチャ概要
- **マルチエージェントシステム**: Google ADKを基盤とした協調動作
- **主要コンポーネント**: メインエージェント、SQLエージェント、分析エージェント、レポートエージェント
- **データベース接続**: genai-toolboxによるMCPサーバー経由でのPostgreSQL接続
- **AI基盤**: Google Gemini 2.5 Flash

## 2. システムアーキテクチャ

### 2.1 全体構成図
```
┌─────────────────────────────────────────────────────────────────┐
│                    Auto Analytics System                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ Main Agent  │  │ SQL Agent   │  │Analysis Agt │  │ Report  │ │
│  │(Coordinator)│◄─┤(Query Gen.) │◄─┤(Insights)   │◄─┤ Agent   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│         │                  │                                    │
│         ▼                  ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Google Gemini 2.5 Flash API                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              genai-toolbox MCP Server                       │ │
│  │                    (port 5000)                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                PostgreSQL Database                          │ │
│  │                   (port 5432)                               │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 プロジェクト構造
```
src/
├── agents/
│   ├── __init__.py
│   ├── main_agent.py          # メインコーディネーターエージェント
│   ├── sql_agent.py           # SQLクエリ生成・実行エージェント
│   ├── analysis_agent.py      # データ分析・洞察エージェント
│   └── report_agent.py        # レポート生成エージェント
├── utils/
│   ├── __init__.py
│   ├── gemini_client.py       # Gemini 2.5 Flash APIラッパー
│   └── prompt_templates.py    # 構造化プロンプトテンプレート
├── models/
│   ├── __init__.py
│   └── schemas.py             # Pydanticデータモデル
├── config/
│   ├── tools.yaml             # genai-toolbox設定ファイル
│   └── settings.py            # アプリケーション設定
└── main.py                    # CLIエントリーポイント
```

## 3. エージェント設計

### 3.1 Main Agent（メインコーディネーター）
**役割**: 自然言語理解、意図分析、適切なエージェントへのルーティング

**主要機能**:
- ユーザー入力の意図分析（Gemini 2.5 Flash使用）
- 会話コンテキストの管理
- 他エージェントへのタスク委譲
- エラーハンドリングと復旧

**実装パターン**:
```python
from google.adk.agents import LlmAgent

main_agent = LlmAgent(
    name="main_coordinator",
    model="gemini-2.0-flash-exp",
    instruction="""
    あなたはデータ分析のコーディネーターです。
    ユーザーの要求を理解し、適切なエージェントに振り分けてください。
    """,
    tools=[intent_analysis_tool, context_management_tool]
)
```

### 3.2 SQL Agent（SQLクエリエージェント）
**役割**: 自然言語からのSQLクエリ生成、検証、最適化、実行

**主要機能**:
- 自然言語からSQLクエリの生成
- SQLクエリの構文・論理検証
- クエリパフォーマンス最適化
- MCPツール経由でのクエリ実行

**MCP統合**:
- `execute-analytics-query`: 動的SQLクエリ実行
- `validate-sql-query`: SQLクエリ検証
- `get-table-schema`: テーブルスキーマ取得

### 3.3 Analysis Agent（分析エージェント）
**役割**: データの統計分析、トレンド検出、洞察抽出

**主要機能**:
- 記述統計の算出
- トレンド分析と予測
- 異常値検出
- 相関分析
- 洞察の自動生成

### 3.4 Report Agent（レポートエージェント）
**役割**: 分析結果の可視化、HTMLレポート生成

**主要機能**:
- チャート・グラフの自動生成
- HTMLレポートの作成
- 洞察の要約とアクションアイテム提案
- 結果のエクスポート機能

## 4. genai-toolbox統合設計

### 4.1 MCP Server設定

#### PostgreSQL接続設定（tools.yaml）
```yaml
sources:
  analytics-postgres:
    kind: postgres
    host: ${POSTGRES_HOST}
    port: 5432
    database: ${POSTGRES_DB}
    user: ${POSTGRES_USER}
    password: ${POSTGRES_PASSWORD}
    pool_size: 10
    max_overflow: 20

tools:
  execute-analytics-query:
    kind: postgres-execute-sql
    source: analytics-postgres
    description: "動的SQLクエリを実行してデータ分析を行う"
    
  validate-sql-query:
    kind: postgres-sql
    source: analytics-postgres
    description: "SQLクエリの構文と実行計画を検証する"
    statement: EXPLAIN (FORMAT JSON, ANALYZE false) $1
    parameters:
      - name: query
        type: string
        description: "検証するSQLクエリ"

  get-table-schema:
    kind: postgres-sql
    source: analytics-postgres
    description: "指定テーブルのスキーマ情報を取得する"
    statement: |
      SELECT 
        column_name, 
        data_type, 
        is_nullable,
        column_default,
        character_maximum_length
      FROM information_schema.columns 
      WHERE table_schema = 'public' 
      AND table_name = $1
      ORDER BY ordinal_position
    parameters:
      - name: table_name
        type: string
        description: "スキーマを取得するテーブル名"

  get-table-statistics:
    kind: postgres-sql
    source: analytics-postgres
    description: "テーブルの統計情報を取得する"
    statement: |
      SELECT 
        schemaname,
        tablename,
        n_tup_ins as inserts,
        n_tup_upd as updates,
        n_tup_del as deletes,
        n_live_tup as live_tuples,
        n_dead_tup as dead_tuples
      FROM pg_stat_user_tables 
      WHERE tablename = $1
    parameters:
      - name: table_name
        type: string
        description: "統計情報を取得するテーブル名"

toolsets:
  analytics-toolset:
    description: "データ分析用のPostgreSQLツールセット"
    tools:
      - execute-analytics-query
      - validate-sql-query
      - get-table-schema
      - get-table-statistics
```

### 4.2 セキュリティ設定
```python
# 環境変数による機密情報管理
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "analytics")
POSTGRES_USER = os.getenv("POSTGRES_USER", "analytics_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TOOLBOX_SERVER_URL = os.getenv("TOOLBOX_SERVER_URL", "http://127.0.0.1:5000")

# 最小権限の原則でのデータベースユーザー作成
CREATE USER analytics_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE analytics TO analytics_user;
GRANT USAGE ON SCHEMA public TO analytics_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;
```

## 5. Gemini 2.5 Flash統合

### 5.1 構造化プロンプト設計

#### 意図分析プロンプト
```python
INTENT_ANALYSIS_PROMPT = """
ユーザーの入力を分析して、以下のJSON形式で応答してください：

{
  "intent": "data_analysis | visualization | report_generation | schema_inquiry | unknown",
  "confidence": "high | medium | low",
  "entities": {
    "tables": ["テーブル名のリスト"],
    "columns": ["カラム名のリスト"],
    "filters": ["フィルター条件"],
    "aggregations": ["集計方法"],
    "time_range": "時間範囲"
  },
  "clarification_needed": boolean,
  "suggested_actions": ["推奨アクション"],
  "metadata": {
    "complexity": "simple | medium | complex",
    "estimated_duration": "推定処理時間"
  }
}

ユーザー入力: {user_input}
会話履歴: {conversation_history}
利用可能テーブル: {available_tables}
"""

SQL_GENERATION_PROMPT = """
以下の情報を基に、最適化されたPostgreSQLクエリを生成してください：

ユーザー要求: {user_request}
テーブルスキーマ: {table_schemas}
会話コンテキスト: {context}

以下のJSON形式で応答してください：
{
  "sql": "生成されたSQLクエリ",
  "explanation": "クエリの説明",
  "assumptions": ["前提条件"],
  "optimizations": ["適用した最適化"],
  "potential_issues": ["潜在的な問題"],
  "estimated_rows": "推定結果行数"
}
"""
```

### 5.2 レスポンス検証とエラーハンドリング
```python
async def validate_gemini_response(response: dict, expected_schema: dict) -> bool:
    """Geminiからのレスポンスを検証"""
    try:
        # Pydanticモデルによる検証
        validated_response = ResponseModel(**response)
        return True
    except ValidationError as e:
        logger.error(f"Gemini response validation failed: {e}")
        return False

async def handle_gemini_error(error: Exception) -> dict:
    """Gemini APIエラーのハンドリング"""
    if isinstance(error, RateLimitError):
        return {"status": "rate_limited", "retry_after": 60}
    elif isinstance(error, AuthenticationError):
        return {"status": "auth_error", "message": "API key invalid"}
    else:
        return {"status": "unknown_error", "message": str(error)}
```

## 6. 開発計画

### Phase 1: 基盤構築（2週間）
**目標**: 基本的なインフラストラクチャの構築

**タスク**:
1. **開発環境セットアップ**
   - Python 3.11+環境構築
   - 必要ライブラリのインストール
   - プロジェクト構造の作成

2. **genai-toolbox MCP Server構築**
   - genai-toolbox (v0.7.0) インストール
   - PostgreSQL接続設定
   - 基本的なSQLツール定義

3. **Gemini 2.5 Flash統合**
   - Google AI APIキー設定
   - 基本的なクライアントラッパー実装
   - 構造化レスポンス処理

4. **Google ADK基盤**
   - ADKプロジェクト初期化
   - 基本エージェント骨格実装

**成果物**:
- 動作する基本システム
- PostgreSQL接続確認
- Gemini API動作確認

### Phase 2: コアエージェント実装（3週間）
**目標**: 主要エージェントの基本機能実装

**タスク**:
1. **Main Agent実装**
   - 意図分析機能
   - 会話コンテキスト管理
   - エージェント間ルーティング

2. **SQL Agent実装**
   - 自然言語からSQL生成
   - MCPツール統合
   - クエリ検証機能

3. **Analysis Agent基盤**
   - 基本統計分析機能
   - pandasによるデータ処理
   - 結果構造化

4. **エラーハンドリング**
   - 各エージェントの例外処理
   - 復旧戦略実装
   - ログ機能統合

**成果物**:
- 動作するマルチエージェントシステム
- 基本的な分析ワークフロー
- エラー処理機能

### Phase 3: 高度な分析機能（2週間）
**目標**: 分析とレポート機能の拡張

**タスク**:
1. **Analysis Agent拡張**
   - トレンド分析
   - 異常値検出
   - 相関分析
   - 洞察自動生成

2. **Report Agent実装**
   - matplotlib/plotlyによる可視化
   - HTMLレポート生成
   - アクションアイテム提案

3. **パフォーマンス最適化**
   - クエリ最適化
   - キャッシュ機能
   - 並行処理改善

**成果物**:
- 完全な分析機能
- レポート生成機能
- パフォーマンス改善

### Phase 4: 統合テスト・改善（1週間）
**目標**: システム全体の品質確保

**タスク**:
1. **包括的テスト**
   - 単体テスト拡充
   - 統合テスト実施
   - パフォーマンステスト

2. **ドキュメント整備**
   - API仕様書作成
   - 利用者ガイド作成
   - 運用手順書作成

3. **最終調整**
   - ユーザビリティ改善
   - エラーメッセージ改善
   - ログ出力調整

**成果物**:
- 本番投入可能なシステム
- 完全なドキュメント
- 運用準備完了

## 7. 技術スタック

### 7.1 コア技術
- **Python 3.11+**: メイン開発言語
- **google-adk**: エージェントフレームワーク
- **genai-toolbox (v0.7.0)**: PostgreSQL MCP Server
- **toolbox-core**: MCP Client SDK
- **google-generativeai**: Gemini 2.5 Flash API

### 7.2 データ処理・分析
- **pandas**: データ操作・分析
- **numpy**: 数値計算
- **scipy**: 統計分析
- **matplotlib**: 基本可視化
- **plotly**: インタラクティブ可視化

### 7.3 その他
- **pydantic**: データ検証
- **structlog**: 構造化ログ
- **asyncio**: 非同期処理
- **pytest**: テストフレームワーク

## 8. 運用設計

### 8.1 環境変数設定
```bash
# PostgreSQL設定
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export POSTGRES_DB="analytics"
export POSTGRES_USER="analytics_user"
export POSTGRES_PASSWORD="secure_password"

# Google AI設定
export GOOGLE_API_KEY="your_gemini_api_key"
export GOOGLE_CLOUD_PROJECT="your_project_id"

# MCP Server設定
export TOOLBOX_SERVER_URL="http://127.0.0.1:5000"
export TOOLBOX_CONFIG_PATH="./config/tools.yaml"

# アプリケーション設定
export LOG_LEVEL="INFO"
export MAX_CONVERSATION_HISTORY="50"
export QUERY_TIMEOUT="300"
```

### 8.2 起動手順
```bash
# 1. genai-toolbox MCP Server起動
./toolbox --tools-file config/tools.yaml --port 5000

# 2. Auto Analytics起動
python main.py --config config/settings.py
```

### 8.3 監視・ログ
- **structlog**による構造化ログ出力
- **OpenTelemetry**によるメトリクス収集（genai-toolbox経由）
- **Gemini API使用量**の監視
- **データベース接続状況**の監視

## 9. セキュリティ考慮事項

### 9.1 データアクセス制御
- PostgreSQLユーザーの最小権限設定
- クエリ実行権限の制限（SELECT、EXPLAIN のみ）
- 機密テーブルへのアクセス制限

### 9.2 API セキュリティ
- Gemini APIキーの環境変数管理
- レート制限の適切な設定
- 機密データのAPI送信防止策

### 9.3 クエリセキュリティ
- SQLインジェクション対策
- 危険なSQL文の検出・ブロック
- 大量データアクセスの制限

## 10. 成功指標・KPI

### 10.1 技術指標
- **SQL生成精度**: 95%以上
- **API応答時間**: 3秒以内
- **システム稼働率**: 99.5%以上

### 10.2 ビジネス指標
- **データ分析時間短縮**: 従来比70%減
- **非技術職利用率**: 50%以上
- **意思決定スピード向上**: 従来比50%向上

### 10.3 品質指標
- **ユーザー満足度**: 4.0/5.0以上
- **エラー率**: 5%以下
- **問い合わせ件数**: 月10件以下

## 11. リスク管理

### 11.1 技術リスク
- **genai-toolbox beta版**の破壊的変更対応
- **Gemini API制限**への対応策
- **データベース負荷**の監視・対策

### 11.2 運用リスク
- **APIコスト**の予算管理
- **データ品質**の継続的監視
- **セキュリティインシデント**への対応準備

### 11.3 対策
- 定期的なバックアップ・復旧テスト
- フォールバック機能の実装
- 包括的な監視・アラート設定