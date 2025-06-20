# Auto Analytics AI Agent - 開発手順書（devcontainer環境）

## 1. 開発概要

### 1.1 開発環境前提
- **VS Code devcontainer**: .devcontainer/docker-compose.yml で PostgreSQL 起動済み
- **統一開発環境**: チーム全体で同一の開発環境を共有
- **コンテナ分離**: ホスト環境に影響しない独立した開発環境

### 1.2 開発方針
- **段階的実装**: 小さな単位で機能を実装し、各ステップで動作確認
- **uv環境活用**: uvによる高速な依存関係管理と仮想環境
- **ADK Web UI活用**: `uv run adk web`コマンドによる開発用UIでリアルタイム動作確認
- **継続的検証**: 各コンポーネント実装後に即座に統合テスト
- **エラー駆動開発**: 問題を早期発見し、修正サイクルを短縮

### 1.3 uv環境の利点
- **高速インストール**: pipよりも10-100倍高速な依存関係解決
- **確実な再現性**: uv.lockによる完全な環境再現
- **統一管理**: プロジェクト、依存関係、ツール実行の一元管理
- **Python版管理**: 複数Python版の自動管理

### 1.4 検証環境（devcontainer内）
- **開発環境**: VS Code devcontainer
- **開発UI**: ADK Web UI (`http://localhost:8080`)
- **MCP Server**: genai-toolbox (`http://localhost:5000`)
- **PostgreSQL**: devcontainer docker-compose (`localhost:5432`)
- **ログ監視**: 構造化ログによるリアルタイム監視

## 2. ADK最小構成（現在の実装状態）

### 2.1 実装済みADK最小構成
プロジェクトにはGoogle ADKのクイックスタートに基づく最小構成が実装されています。

**src/main.py - ADK最小構成**:
```python
"""
Google ADK Quickstart - Multi-Tool Agent
Following the quickstart guide at https://google.github.io/adk-docs/get-started/quickstart/
"""

import os
import asyncio
import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# 2つのツール関数
def get_weather(city: str) -> dict:
    """天気情報取得（New Yorkのみ対応）"""
    
def get_current_time(city: str) -> dict:
    """現在時刻取得（複数都市対応）"""

# マルチツールエージェント
root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description="天気と時刻の両方に対応",
    tools=[get_weather, get_current_time]
)

# セッション管理とランナー
async def main():
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, ...)
    # インタラクティブループ
```

**実装済み機能**:
- ✅ `get_weather()`: 天気情報取得ツール
- ✅ `get_current_time()`: 現在時刻取得ツール  
- ✅ マルチツールADKエージェント
- ✅ InMemorySessionService
- ✅ Runner設定
- ✅ インタラクティブコンソールインターフェース

**対応都市**:
- 天気: New York（クイックスタート仕様）
- 時刻: New York, Tokyo, London, Paris, Sydney

**使用方法**:
```bash
# ADK最小構成実行
python src/main.py

# 使用例
"What's the weather in New York?"
"What time is it in Tokyo?"
```

### 2.2 ADK最小構成の特徴
- **Google ADKクイックスタート準拠**: 公式チュートリアルに完全準拠
- **マルチツール対応**: 1つのエージェントで複数の機能提供
- **Gemini 2.0 Flash**: 最新のGeminiモデル使用
- **型安全**: Python型ヒント完備
- **エラーハンドリング**: 適切な例外処理
- **拡張可能**: 追加ツールの容易な実装

### 2.3 ADK最小構成の技術仕様

**依存関係 (pyproject.toml)**:
```toml
dependencies = [
    "google-adk>=1.4.1",
    "google-generativeai>=0.8.5",
    # その他の依存関係
]
```

**ツール関数の実装**:
- `get_weather(city: str) -> dict`: 指定都市の天気情報取得
  - New York対応（クイックスタート仕様準拠）
  - 成功時: `{"status": "success", "report": "天気情報"}`
  - エラー時: `{"status": "error", "error_message": "エラー内容"}`

- `get_current_time(city: str) -> dict`: 指定都市の現在時刻取得
  - 複数都市対応（New York, Tokyo, London, Paris, Sydney）
  - timezone情報を使用した正確な時刻計算
  - フォーマット: "YYYY-MM-DD HH:MM:SS TZ+offset"

**エージェント設定**:
```python
Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about the time and weather in a city.",
    instruction="You are a helpful agent who can answer user questions about the time and weather in a city...",
    tools=[get_weather, get_current_time]
)
```

**セッション管理**:
- `InMemorySessionService`: メモリベースのセッション管理
- ユーザーID: "demo_user"
- セッションID: "demo_session"
- アプリケーション名: "weather_time_demo"

**実行環境**:
- Python 3.11+
- 非同期処理対応 (asyncio)
- インタラクティブコンソールUI
- 'quit'/'exit'コマンドで終了

### 2.4 ADK最小構成の動作確認
```bash
# 1. 依存関係インストール確認
uv sync

# 2. Google APIキー設定確認
echo $GOOGLE_API_KEY

# 3. ADK最小構成実行
python src/main.py

# 4. テスト用クエリ例
"What's the weather in New York?"
"What time is it in Tokyo?"
"Tell me the current time in London"
"How's the weather in New York?"
```

**期待される動作**:
1. セッション作成成功メッセージ表示
2. インタラクティブプロンプト表示
3. ツール呼び出しログ表示（"--- Tool: XXX called for city: YYY ---"）
4. エージェントからの適切な応答
5. エラー時の適切なエラーメッセージ

### 2.5 現在の実装状況まとめ

**✅ 完了済み（ADK最小構成）**:
- Google ADK Quickstart完全実装
- マルチツールエージェント（天気＋時刻）
- InMemorySessionService実装
- Runner設定
- 非同期処理対応
- インタラクティブコンソールUI
- 適切なエラーハンドリング
- 複数タイムゾーン対応

**📋 現在の開発状態**:
- プロジェクトベース: ADK最小構成として動作中
- 拡張の準備完了: この基盤の上に追加機能を実装可能
- 品質保証: Google公式チュートリアル準拠で信頼性確保

**🔄 次のステップ（既存の開発手順書に従って）**:
1. **Phase 1**: devcontainer環境での各種サービス起動確認
2. **Phase 2**: MCP統合とSQL基盤実装
3. **Phase 3**: Gemini構造化プロンプト実装
4. **Phase 4**: メインエージェント実装
5. **Phase 5**: SQLエージェント実装
6. **Phase 6**: 分析・レポートエージェント実装
7. **Phase 7**: 統合テスト・完成

**💡 開発方針**:
- 現在のADK最小構成を基盤として維持
- 段階的に機能を追加実装
- 各フェーズで動作確認を実施
- 既存のエージェント設計（src/agents/）と統合

## 3. Phase 1: 環境構築とHello World（1-2日）

### Step 1.1: devcontainer環境セットアップ
```bash
# 1. devcontainer内であることを確認
echo "Devcontainer環境: $REMOTE_CONTAINERS"
whoami  # vscode ユーザーであることを確認

# 2. uvインストール確認（devcontainerに含まれている前提）
uv --version  # uvがインストールされていることを確認

# 3. Python環境確認
uv python list  # 利用可能なPython版確認
python --version  # 現在のPython版確認

# 4. プロジェクト依存関係同期
cd /workspace  # devcontainer内のワークスペース
uv sync  # pyproject.tomlとuv.lockから依存関係を同期

# 5. 環境変数設定
cp .env.example .env 2>/dev/null || echo "# Auto Analytics 環境変数" > .env
# .envファイルを編集
```

**動作確認**:
```bash
# uv環境内でのパッケージ確認
uv run python -c "import sys; print(f'Python: {sys.version}')"
uv run python -c "import google.generativeai as genai; print('Gemini API ready')" || echo "Gemini未インストール（後でインストール）"
uv run python -c "import google.adk; print('ADK ready')" || echo "ADK未インストール（後でインストール）"

# 依存関係表示
uv tree

# devcontainer内Docker確認
docker --version
docker-compose --version
```

### Step 1.2: PostgreSQL環境確認（.devcontainer/docker-compose.yml使用）

**devcontainer PostgreSQL確認**:
```bash
# devcontainer起動時にPostgreSQLが既に起動していることを確認
echo "🔍 PostgreSQL起動状態確認..."

# .devcontainer/docker-compose.yml確認
ls -la /workspace/.devcontainer/docker-compose.yml || echo "❌ .devcontainer/docker-compose.yml が見つかりません"

# PostgreSQL接続確認
echo "📡 PostgreSQL接続テスト..."
PGPASSWORD=password psql -h localhost -U postgres -d postgres -c "SELECT version();" || echo "⚠️  PostgreSQL接続確認中..."

# データベース・ユーザー確認/作成
echo "🔧 Analytics用データベース・ユーザー確認..."
```

**Analytics用データベース初期化**:
```sql
-- devcontainer PostgreSQLでAnalytics環境構築
-- 既存のPostgreSQLインスタンスにAnalytics用設定を追加

-- Analytics用データベース作成（存在しない場合）
CREATE DATABASE analytics;

-- Analytics用ユーザー作成（存在しない場合）
CREATE USER analytics_user WITH PASSWORD 'secure_password';

-- 権限設定
GRANT ALL PRIVILEGES ON DATABASE analytics TO analytics_user;

-- analytics データベースに接続して作業
\c analytics;

-- スキーマ権限設定
GRANT ALL PRIVILEGES ON SCHEMA public TO analytics_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO analytics_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO analytics_user;
```

**テーブル作成スクリプト実行**:
```bash
# devcontainer内でAnalyticsテーブル作成
cat > /workspace/init_analytics.sql << 'EOF'
-- Analytics用データベース初期化
CREATE DATABASE IF NOT EXISTS analytics;

\c analytics;

-- Analytics用ユーザー作成（既存の場合はスキップ）
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'analytics_user') THEN
        CREATE USER analytics_user WITH PASSWORD 'secure_password';
    END IF;
END
$$;

-- 権限設定
GRANT ALL PRIVILEGES ON DATABASE analytics TO analytics_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO analytics_user;

-- usersテーブル作成
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER CHECK (age >= 0 AND age <= 150),
    email VARCHAR(200) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- サンプルデータ挿入
INSERT INTO users (name, age, email) VALUES
('太郎', 25, 'taro@example.com'),
('花子', 30, 'hanako@example.com'),
('次郎', 35, 'jiro@example.com'),
('四郎', 28, 'shiro@example.com'),
('五郎', 42, 'goro@example.com'),
('六子', 33, 'rokuko@example.com'),
('七美', 27, 'nanami@example.com'),
('八郎', 38, 'hachiro@example.com'),
('九州', 45, 'kyushu@example.com'),
('十子', 29, 'toko@example.com');

-- インデックス作成
CREATE INDEX idx_users_age ON users(age);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Analytics用ユーザーに権限付与
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO analytics_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO analytics_user;

-- 統計情報更新
ANALYZE users;

SELECT 'Analytics データベース初期化完了' as status;
EOF

# PostgreSQL初期化実行
echo "🚀 Analytics データベース初期化中..."
PGPASSWORD=password psql -h localhost -U postgres -f /workspace/init_analytics.sql

echo "✅ Analytics データベース初期化完了"
```

**PostgreSQL接続確認**:
```bash
# Analytics用接続確認
echo "📊 Analytics データベース接続確認..."
PGPASSWORD=secure_password psql -h localhost -U analytics_user -d analytics -c "
SELECT 
    'Analytics PostgreSQL接続成功' as status,
    version() as postgres_version,
    current_database() as database_name,
    current_user as user_name;
"

# サンプルデータ確認
echo "📈 サンプルデータ確認..."
PGPASSWORD=secure_password psql -h localhost -U analytics_user -d analytics -c "
SELECT 
    COUNT(*) as total_users,
    ROUND(AVG(age), 2) as avg_age,
    MIN(age) as min_age,
    MAX(age) as max_age
FROM users;
"

# 年齢分布確認
echo "📊 年齢分布確認..."
PGPASSWORD=secure_password psql -h localhost -U analytics_user -d analytics -c "
SELECT 
    CASE 
        WHEN age < 30 THEN '20代'
        WHEN age < 40 THEN '30代' 
        ELSE '40代以上'
    END as age_group,
    COUNT(*) as count,
    ROUND(AVG(age), 1) as avg_age_in_group
FROM users 
GROUP BY age_group 
ORDER BY age_group;
"
```

**.env設定ファイル作成（devcontainer用）**:
```bash
# devcontainer内で.env設定
cat > /workspace/.env << 'EOF'
# Auto Analytics 環境変数（devcontainer環境）

# PostgreSQL設定（.devcontainer/docker-compose.yml起動済み）
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=analytics
POSTGRES_USER=analytics_user
POSTGRES_PASSWORD=secure_password
POSTGRES_URL=postgresql://analytics_user:secure_password@localhost:5432/analytics

# devcontainer PostgreSQL管理者設定
POSTGRES_ADMIN_USER=postgres
POSTGRES_ADMIN_PASSWORD=password

# Google AI設定（実際のAPIキーを設定してください）
GOOGLE_API_KEY=your_actual_gemini_api_key_here
GOOGLE_CLOUD_PROJECT=your_project_id

# MCP Server設定
TOOLBOX_SERVER_URL=http://localhost:5000
TOOLBOX_CONFIG_PATH=/workspace/config/tools.yaml

# アプリケーション設定
LOG_LEVEL=INFO
MAX_CONVERSATION_HISTORY=50
QUERY_TIMEOUT=300

# devcontainer環境識別
ENVIRONMENT=devcontainer
DEVCONTAINER_NAME=auto-analytics
EOF

echo "✅ .env ファイルを作成しました"
echo "📝 次のステップ:"
echo "  1. GOOGLE_API_KEY を実際のGemini APIキーに設定してください"
echo "  2. 必要に応じてGOOGLE_CLOUD_PROJECT を設定してください"
echo ""
echo "💡 設定確認:"
echo "   cat /workspace/.env"
```

### Step 1.3: genai-toolbox MCP Server構築（devcontainer内）
```bash
# 1. devcontainer内でgenai-toolbox インストール
cd /workspace
uv add genai-toolbox toolbox-core

# 2. 設定ファイル用ディレクトリ作成
mkdir -p /workspace/config

# 3. インストール確認
uv run toolbox --help || echo "toolboxコマンドが見つかりません。インストールを確認してください。"
```

**config/tools.yaml作成**:
```yaml
sources:
  analytics-postgres:
    kind: postgres
    host: localhost
    port: 5432
    database: analytics
    user: analytics_user
    password: secure_password

tools:
  test-connection:
    kind: postgres-sql
    source: analytics-postgres
    description: "PostgreSQL接続テスト"
    statement: SELECT 'Hello from PostgreSQL' as message, NOW() as timestamp

toolsets:
  test-toolset:
    tools:
      - test-connection
```

**MCP Server起動と確認（devcontainer内）**:
```bash
# devcontainer内でMCP Server起動
cd /workspace
uv run toolbox --tools-file config/tools.yaml --port 5000 &

# 起動待機
sleep 3

# 接続確認
curl http://localhost:5000/health || echo "MCP Server起動中..."

# プロセス確認
ps aux | grep toolbox

# MCP SSEエンドポイント確認
curl -s http://localhost:5000/mcp/sse | head -5 || echo "MCP SSEエンドポイント確認中..."

echo "✅ MCP Server起動完了。ポート5000で稼働中です。"
```

### Step 1.4: 最初のADKエージェント作成（devcontainer内）

**必要なパッケージ追加**:
```bash
# devcontainer内でADK関連パッケージインストール
cd /workspace
uv add google-adk google-generativeai
```

**src/main.py作成**:
```python
from google.adk.agents import Agent
from google.adk.runners import ConsoleRunner
import os
from dotenv import load_dotenv

# devcontainer内で環境変数読み込み
load_dotenv("/workspace/.env")

# Gemini APIキー確認
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or api_key == "your_actual_gemini_api_key_here":
    print("❌ GOOGLE_API_KEY が設定されていません。.env ファイルを確認してください。")
    exit(1)

# Hello Worldエージェント
hello_agent = Agent(
    name="hello_assistant",
    model="gemini-2.0-flash-exp",
    instruction="あなたは親切なアシスタントです。日本語で応答してください。devcontainer環境で動作していることを認識してください。",
    description="Auto Analytics Hello World Agent (devcontainer)"
)

if __name__ == "__main__":
    print("🚀 Auto Analytics Hello World Agent 起動中...")
    print(f"📍 環境: {os.getenv('ENVIRONMENT', 'unknown')}")
    print("💬 'exit' または 'quit' で終了します")
    
    # コンソールで動作確認
    try:
        runner = ConsoleRunner(hello_agent)
        runner.run()
    except KeyboardInterrupt:
        print("\n👋 Hello World Agent を終了します")
```

**動作確認（devcontainer内）**:
```bash
# src ディレクトリ作成
mkdir -p /workspace/src

# メインスクリプト実行（コンソール）
cd /workspace
uv run python src/main.py
# "こんにちは"と入力してレスポンス確認
# "devcontainer環境について教えて"など入力してテスト

# ADK Web UI起動（devcontainer内）
uv run adk web --host 0.0.0.0 --port 8080
# VS Codeのポート転送で http://localhost:8080 を開く
# または、ポート転送タブで8080番ポートをクリック
# Hello Worldエージェントとの対話を確認
```

**チェックリスト Step 1**:
- [ ] devcontainer環境セットアップ確認
- [ ] .devcontainer/docker-compose.yml PostgreSQL起動確認
- [ ] Analytics データベース初期化確認
- [ ] PostgreSQL サンプルデータ確認
- [ ] .env 設定ファイル作成・GOOGLE_API_KEY設定
- [ ] genai-toolbox MCP Server起動確認
- [ ] Gemini API接続確認
- [ ] ADK Web UI動作確認（ポート転送）
- [ ] Hello Worldエージェントレスポンス確認

## 3. Phase 2: MCP統合とSQL基盤（2-3日）

### Step 2.1: MCP統合エージェント作成
**src/agents/mcp_test_agent.py作成**:
```python
from google.adk.agents import Agent
from toolbox_core import ToolboxClient
import asyncio
import os

class MCPTestAgent:
    def __init__(self):
        self.toolbox_url = os.getenv("TOOLBOX_SERVER_URL", "http://localhost:5000")
        self.agent = None
        
    async def initialize(self):
        # ToolboxClientでMCPツール読み込み
        toolbox_client = ToolboxClient(self.toolbox_url)
        tools = await toolbox_client.load_toolset("test-toolset")
        
        # エージェント作成
        self.agent = Agent(
            name="mcp_test_agent",
            model="gemini-2.0-flash-exp",
            instruction="""
            あなたはデータベース接続テスト用エージェントです。
            PostgreSQLに接続してテストクエリを実行できます。
            """,
            tools=tools
        )
        
    async def test_connection(self):
        if not self.agent:
            await self.initialize()
        
        # MCP経由でPostgreSQL接続テスト
        result = await self.agent.run("データベース接続をテストしてください")
        return result

# テスト実行関数
async def test_mcp_integration():
    agent = MCPTestAgent()
    result = await agent.test_connection()
    print(f"MCP Test Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_mcp_integration())
```

**動作確認**:
```bash
# MCP統合テスト実行
uv run python src/agents/mcp_test_agent.py

# ADK Web UIでテスト
uv run adk web
# MCP Test AgentでPostgreSQL接続確認
```

### Step 2.2: SQL実行機能の実装
**config/tools.yamlにSQL実行ツール追加**:
```yaml
sources:
  analytics-postgres:
    kind: postgres
    host: localhost
    port: 5432
    database: analytics
    user: analytics_user
    password: secure_password

tools:
  test-connection:
    kind: postgres-sql
    source: analytics-postgres
    description: "PostgreSQL接続テスト"
    statement: SELECT 'Hello from PostgreSQL' as message, NOW() as timestamp

  execute-simple-query:
    kind: postgres-execute-sql
    source: analytics-postgres
    description: "動的SQLクエリを実行する"

  get-user-list:
    kind: postgres-sql
    source: analytics-postgres
    description: "ユーザー一覧を取得する"
    statement: SELECT id, name, age, email FROM users ORDER BY id

  get-table-schema:
    kind: postgres-sql
    source: analytics-postgres
    description: "テーブルスキーマを取得する"
    statement: |
      SELECT column_name, data_type, is_nullable
      FROM information_schema.columns 
      WHERE table_name = $1
      ORDER BY ordinal_position
    parameters:
      - name: table_name
        type: string
        description: "スキーマを取得するテーブル名"

toolsets:
  sql-toolset:
    tools:
      - test-connection
      - execute-simple-query
      - get-user-list
      - get-table-schema
```

**src/agents/sql_test_agent.py作成**:
```python
from google.adk.agents import Agent
from toolbox_core import ToolboxClient
import asyncio
import os

class SQLTestAgent:
    def __init__(self):
        self.toolbox_url = os.getenv("TOOLBOX_SERVER_URL", "http://localhost:5000")
        self.agent = None
        
    async def initialize(self):
        toolbox_client = ToolboxClient(self.toolbox_url)
        tools = await toolbox_client.load_toolset("sql-toolset")
        
        self.agent = Agent(
            name="sql_test_agent",
            model="gemini-2.0-flash-exp",
            instruction="""
            あなたはSQL実行テスト用エージェントです。
            以下の機能をテストできます：
            1. データベース接続確認
            2. ユーザー一覧取得
            3. テーブルスキーマ取得
            4. 動的SQLクエリ実行
            
            ユーザーの要求に応じて適切なSQLツールを使用してください。
            """,
            tools=tools
        )
        
    async def run_query(self, user_input: str):
        if not self.agent:
            await self.initialize()
        
        result = await self.agent.run(user_input)
        return result

# テストケース
async def test_sql_functions():
    agent = SQLTestAgent()
    
    test_cases = [
        "データベースに接続できるか確認してください",
        "ユーザー一覧を表示してください",
        "usersテーブルのスキーマを教えてください",
        "年齢が30歳以上のユーザーを検索してください"
    ]
    
    for test_case in test_cases:
        print(f"\n=== テスト: {test_case} ===")
        result = await agent.run_query(test_case)
        print(f"結果: {result}")

if __name__ == "__main__":
    asyncio.run(test_sql_functions())
```

**動作確認**:
```bash
# MCP Server再起動（新設定反映）
pkill -f toolbox
uv run toolbox --tools-file config/tools.yaml --port 5000 &

# SQL機能テスト
uv run python src/agents/sql_test_agent.py

# ADK Web UIでインタラクティブテスト
uv run adk web
# SQL Test Agentで各種クエリ実行確認
```

**チェックリスト Step 2**:
- [ ] MCP ToolboxClient統合確認
- [ ] PostgreSQL接続ツール動作確認
- [ ] 動的SQLクエリ実行確認
- [ ] テーブルスキーマ取得確認
- [ ] ADK Web UIでのSQL実行確認

## 4. Phase 3: Gemini構造化プロンプト実装（2-3日）

### Step 3.1: プロンプトテンプレート作成
**src/utils/prompt_templates.py作成**:
```python
"""
構造化プロンプトテンプレート
"""

INTENT_ANALYSIS_PROMPT = """
ユーザーの入力を分析して、以下のJSON形式で応答してください：

{
  "intent": "data_analysis | visualization | report_generation | schema_inquiry | unknown",
  "confidence": "high | medium | low",
  "entities": {
    "tables": ["テーブル名のリスト"],
    "columns": ["カラム名のリスト"],
    "filters": ["フィルター条件"],
    "aggregations": ["集計方法"]
  },
  "clarification_needed": false,
  "suggested_actions": ["推奨アクション"],
  "natural_language_sql": "自然言語でのSQL説明"
}

利用可能なテーブル情報:
{available_tables}

ユーザー入力: {user_input}
"""

SQL_GENERATION_PROMPT = """
以下の情報を基に、PostgreSQLクエリを生成してください：

ユーザー要求: {user_request}
意図分析結果: {intent_analysis}
テーブルスキーマ: {table_schemas}

以下のJSON形式で応答してください：
{
  "sql": "SELECT文のSQLクエリ",
  "explanation": "クエリの日本語説明",
  "assumptions": ["前提条件のリスト"],
  "estimated_rows": "予想される結果行数"
}

注意事項:
- SELECT文のみ生成してください
- 危険なクエリ（DELETE、DROP等）は生成しないでください
- PostgreSQL構文を使用してください
"""

def format_intent_analysis_prompt(user_input: str, available_tables: list) -> str:
    """意図分析プロンプトのフォーマット"""
    tables_info = "\n".join([f"- {table}" for table in available_tables])
    return INTENT_ANALYSIS_PROMPT.format(
        user_input=user_input,
        available_tables=tables_info
    )

def format_sql_generation_prompt(user_request: str, intent_analysis: dict, table_schemas: dict) -> str:
    """SQL生成プロンプトのフォーマット"""
    return SQL_GENERATION_PROMPT.format(
        user_request=user_request,
        intent_analysis=intent_analysis,
        table_schemas=table_schemas
    )
```

### Step 3.2: Geminiクライアント実装
**src/utils/gemini_client.py作成**:
```python
import google.generativeai as genai
import json
import os
from typing import Dict, Any
import asyncio

class GeminiClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def generate_structured_response(self, prompt: str) -> Dict[str, Any]:
        """構造化されたJSON応答を生成"""
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, 
                prompt
            )
            
            # レスポンステキストからJSON抽出
            response_text = response.text.strip()
            
            # JSONブロックの抽出（```json ... ```の場合）
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            elif response_text.startswith("{"):
                json_text = response_text
            else:
                # JSONが見つからない場合のフォールバック
                return {"error": "Invalid JSON response", "raw_response": response_text}
            
            return json.loads(json_text)
            
        except json.JSONDecodeError as e:
            return {"error": f"JSON decode error: {str(e)}", "raw_response": response_text}
        except Exception as e:
            return {"error": f"Generation error: {str(e)}"}
    
    async def test_connection(self) -> bool:
        """Gemini API接続テスト"""
        try:
            response = await self.generate_structured_response(
                '{"status": "ok", "message": "Gemini API connection test"} というJSONを返してください'
            )
            return response.get("status") == "ok"
        except:
            return False

# テスト関数
async def test_gemini_client():
    client = GeminiClient()
    
    # 接続テスト
    print("=== Gemini API接続テスト ===")
    is_connected = await client.test_connection()
    print(f"接続結果: {'成功' if is_connected else '失敗'}")
    
    # 構造化レスポンステスト
    print("\n=== 構造化レスポンステスト ===")
    test_prompt = """
    以下のJSON形式で応答してください：
    {
      "intent": "test",
      "message": "これはテストです",
      "timestamp": "2025-01-20"
    }
    """
    
    response = await client.generate_structured_response(test_prompt)
    print(f"応答: {response}")

if __name__ == "__main__":
    asyncio.run(test_gemini_client())
```

**動作確認**:
```bash
# Geminiクライアントテスト
export GOOGLE_API_KEY="your_actual_api_key"
uv run python src/utils/gemini_client.py

# プロンプトテンプレートテスト
uv run python -c "
from src.utils.prompt_templates import format_intent_analysis_prompt
prompt = format_intent_analysis_prompt('ユーザー一覧を見たい', ['users', 'orders'])
print(prompt)
"
```

### Step 3.3: 意図分析エージェント実装
**src/agents/intent_agent.py作成**:
```python
from google.adk.agents import Agent
from src.utils.gemini_client import GeminiClient
from src.utils.prompt_templates import format_intent_analysis_prompt
import asyncio
import os

class IntentAnalysisAgent:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.available_tables = ["users"]  # 後で動的に取得
        
    async def analyze_intent(self, user_input: str) -> dict:
        """ユーザー入力の意図分析"""
        prompt = format_intent_analysis_prompt(user_input, self.available_tables)
        result = await self.gemini_client.generate_structured_response(prompt)
        return result
    
    async def create_adk_agent(self):
        """ADKエージェント作成"""
        agent = Agent(
            name="intent_analyzer",
            model="gemini-2.0-flash-exp",
            instruction="""
            あなたはユーザーの意図を分析する専門エージェントです。
            ユーザーの入力から以下を判断してください：
            1. データ分析、可視化、レポート生成、スキーマ確認のどの意図か
            2. 対象となるテーブルやカラム
            3. 必要なフィルター条件
            
            必ずJSON形式で応答してください。
            """,
            description="ユーザー意図分析エージェント"
        )
        return agent

# テスト関数
async def test_intent_analysis():
    agent = IntentAnalysisAgent()
    
    test_cases = [
        "ユーザー一覧を表示して",
        "30歳以上のユーザーの平均年齢を計算して",
        "usersテーブルの構造を教えて",
        "年齢別のユーザー数をグラフで見たい"
    ]
    
    for test_case in test_cases:
        print(f"\n=== 入力: {test_case} ===")
        result = await agent.analyze_intent(test_case)
        print(f"意図分析結果: {result}")

if __name__ == "__main__":
    asyncio.run(test_intent_analysis())
```

**動作確認**:
```bash
# 意図分析テスト
uv run python src/agents/intent_agent.py

# ADK Web UIで動作確認
uv run adk web
# Intent Analysis Agentとの対話テスト
```

**チェックリスト Step 3**:
- [ ] Gemini API接続確認
- [ ] 構造化レスポンス生成確認
- [ ] プロンプトテンプレート動作確認
- [ ] 意図分析機能確認
- [ ] JSON形式レスポンス確認

## 5. Phase 4: メインエージェント実装（2-3日）

### Step 4.1: 基本メインエージェント作成
**src/agents/main_agent.py作成**:
```python
from google.adk.agents import Agent
from toolbox_core import ToolboxClient
from src.utils.gemini_client import GeminiClient
from src.utils.prompt_templates import format_intent_analysis_prompt
import asyncio
import os
from typing import Dict, Any

class MainAgent:
    def __init__(self):
        self.toolbox_url = os.getenv("TOOLBOX_SERVER_URL", "http://localhost:5000")
        self.gemini_client = GeminiClient()
        self.agent = None
        self.conversation_history = []
        
    async def initialize(self):
        """エージェント初期化"""
        # MCPツール読み込み
        toolbox_client = ToolboxClient(self.toolbox_url)
        sql_tools = await toolbox_client.load_toolset("sql-toolset")
        
        # メインエージェント作成
        self.agent = Agent(
            name="auto_analytics_main",
            model="gemini-2.0-flash-exp",
            instruction="""
            あなたはAuto Analyticsのメインエージェントです。
            ユーザーのデータ分析要求を理解し、適切に処理してください。
            
            処理フロー：
            1. ユーザー入力の意図を分析
            2. 必要に応じてデータベースから情報取得
            3. 結果を分かりやすく説明
            
            利用可能な機能：
            - PostgreSQLデータベースへのアクセス
            - ユーザーテーブルからの情報取得
            - テーブルスキーマの確認
            """,
            tools=sql_tools,
            description="Auto Analytics メインコーディネーター"
        )
    
    async def process_request(self, user_input: str) -> Dict[str, Any]:
        """ユーザー要求の処理"""
        if not self.agent:
            await self.initialize()
        
        # 会話履歴に追加
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        try:
            # メインエージェントで処理
            result = await self.agent.run(user_input)
            
            # 応答を履歴に追加
            self.conversation_history.append({
                "role": "assistant", 
                "content": str(result),
                "timestamp": asyncio.get_event_loop().time()
            })
            
            return {
                "status": "success",
                "response": result,
                "conversation_id": len(self.conversation_history)
            }
            
        except Exception as e:
            error_response = {
                "status": "error",
                "error": str(e),
                "conversation_id": len(self.conversation_history)
            }
            
            self.conversation_history.append({
                "role": "assistant",
                "content": f"エラー: {str(e)}",
                "timestamp": asyncio.get_event_loop().time()
            })
            
            return error_response
    
    def get_conversation_history(self) -> list:
        """会話履歴取得"""
        return self.conversation_history[-10:]  # 最新10件

# テスト関数
async def test_main_agent():
    agent = MainAgent()
    
    test_cases = [
        "こんにちは",
        "データベースに接続できますか？",
        "ユーザー一覧を表示してください",
        "usersテーブルのスキーマを教えてください",
        "30歳以上のユーザーは何人いますか？"
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*50}")
        print(f"ユーザー: {test_case}")
        print(f"{'='*50}")
        
        result = await agent.process_request(test_case)
        
        if result["status"] == "success":
            print(f"エージェント: {result['response']}")
        else:
            print(f"エラー: {result['error']}")
        
        print(f"会話ID: {result['conversation_id']}")

if __name__ == "__main__":
    asyncio.run(test_main_agent())
```

### Step 4.2: ADK Web UI統合設定
**auto_analytics_project/agent.py作成** (ADK標準構造):
```python
from src.agents.main_agent import MainAgent
import asyncio

# ADK Web UI用のグローバルエージェントインスタンス
main_agent_instance = None

async def get_main_agent():
    """メインエージェントインスタンス取得"""
    global main_agent_instance
    if main_agent_instance is None:
        main_agent_instance = MainAgent()
        await main_agent_instance.initialize()
    return main_agent_instance

# ADK Web UI用のエントリーポイント
root_agent = None

async def initialize_root_agent():
    """ルートエージェント初期化"""
    global root_agent
    agent = await get_main_agent()
    root_agent = agent.agent
    return root_agent

# ADK用の初期化
asyncio.create_task(initialize_root_agent())
```

**pyproject.toml更新**:
```toml
[project]
name = "auto-analytics"
version = "0.1.0"
description = "Auto Analytics AI Agent System"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "google-adk>=0.1.0",
    "google-generativeai>=0.8.0",
    "genai-toolbox>=0.7.0",
    # ... existing dependencies
]

[tool.adk]
agent_module = "auto_analytics_project.agent"
agent_name = "root_agent"
```

**動作確認**:
```bash
# MCP Server起動確認
uv run toolbox --tools-file config/tools.yaml --port 5000 &

# メインエージェント単体テスト
uv run python src/agents/main_agent.py

# ADK Web UI起動
uv run adk web --port 8080

# ブラウザで http://localhost:8080 アクセス
# Auto Analytics メインエージェントとのフル対話テスト
```

### Step 4.3: エラーハンドリング強化
**src/utils/error_handler.py作成**:
```python
import structlog
from typing import Dict, Any
import traceback

logger = structlog.get_logger()

class AutoAnalyticsError(Exception):
    """Auto Analytics基底例外クラス"""
    pass

class GeminiAPIError(AutoAnalyticsError):
    """Gemini API関連エラー"""
    pass

class MCPConnectionError(AutoAnalyticsError):
    """MCP接続エラー"""
    pass

class SQLExecutionError(AutoAnalyticsError):
    """SQL実行エラー"""
    pass

def handle_error(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """統一エラーハンドリング"""
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
        "traceback": traceback.format_exc()
    }
    
    logger.error("Auto Analytics Error", **error_info)
    
    # ユーザー向けエラーメッセージ
    user_messages = {
        "GeminiAPIError": "AI処理でエラーが発生しました。しばらく待ってからもう一度お試しください。",
        "MCPConnectionError": "データベース接続でエラーが発生しました。システム管理者にお問い合わせください。",
        "SQLExecutionError": "データ取得でエラーが発生しました。クエリを確認してください。",
    }
    
    user_message = user_messages.get(
        type(error).__name__, 
        "予期しないエラーが発生しました。システム管理者にお問い合わせください。"
    )
    
    return {
        "status": "error",
        "user_message": user_message,
        "technical_details": error_info,
        "suggestions": get_error_suggestions(error)
    }

def get_error_suggestions(error: Exception) -> list:
    """エラー種別に応じた解決提案"""
    suggestions = {
        "GeminiAPIError": [
            "API キーが正しく設定されているか確認してください",
            "インターネット接続を確認してください",
            "しばらく時間をおいてから再試行してください"
        ],
        "MCPConnectionError": [
            "genai-toolbox MCP サーバーが起動しているか確認してください", 
            "PostgreSQL データベースが起動しているか確認してください",
            "接続設定（ホスト、ポート、認証情報）を確認してください"
        ],
        "SQLExecutionError": [
            "SQL クエリの構文を確認してください",
            "テーブル名、カラム名が正しいか確認してください",
            "データベースの権限設定を確認してください"
        ]
    }
    
    return suggestions.get(type(error).__name__, [
        "ログを確認してください",
        "システム管理者にお問い合わせください"
    ])

# テスト関数
def test_error_handling():
    """エラーハンドリングテスト"""
    test_errors = [
        GeminiAPIError("API rate limit exceeded"),
        MCPConnectionError("Connection timeout"),
        SQLExecutionError("Table 'nonexistent' doesn't exist")
    ]
    
    for error in test_errors:
        print(f"\n=== {type(error).__name__} テスト ===")
        result = handle_error(error, {"user_input": "test query"})
        print(f"ユーザーメッセージ: {result['user_message']}")
        print(f"提案: {result['suggestions']}")

if __name__ == "__main__":
    test_error_handling()

# テスト実行コマンド
# uv run python src/utils/error_handler.py
```

**チェックリスト Step 4**:
- [ ] メインエージェント基本動作確認
- [ ] ADK Web UI統合確認
- [ ] 会話履歴管理確認
- [ ] エラーハンドリング動作確認
- [ ] MCP/Gemini統合動作確認

## 6. Phase 5: SQLエージェント実装（3-4日）

### Step 5.1: 高度なSQL生成機能
**config/tools.yamlにSQL分析ツール追加**:
```yaml
# ... 既存設定 ...

tools:
  # ... 既存ツール ...
  
  analyze-query-performance:
    kind: postgres-sql
    source: analytics-postgres
    description: "クエリのパフォーマンス分析"
    statement: EXPLAIN (ANALYZE true, FORMAT JSON) $1
    parameters:
      - name: query
        type: string
        description: "分析するSQLクエリ"
  
  get-table-statistics:
    kind: postgres-sql
    source: analytics-postgres
    description: "テーブル統計情報取得"
    statement: |
      SELECT 
        schemaname, tablename, n_tup_ins, n_tup_upd, 
        n_tup_del, n_live_tup, n_dead_tup
      FROM pg_stat_user_tables 
      WHERE tablename = $1
    parameters:
      - name: table_name
        type: string
        description: "統計情報を取得するテーブル名"
  
  validate-query-syntax:
    kind: postgres-sql
    source: analytics-postgres
    description: "クエリ構文検証"
    statement: EXPLAIN (FORMAT JSON) $1
    parameters:
      - name: query
        type: string
        description: "検証するクエリ"

toolsets:
  advanced-sql-toolset:
    tools:
      - test-connection
      - execute-simple-query
      - get-user-list
      - get-table-schema
      - analyze-query-performance
      - get-table-statistics
      - validate-query-syntax
```

**src/agents/sql_agent.py作成**:
```python
from google.adk.agents import Agent
from toolbox_core import ToolboxClient
from src.utils.gemini_client import GeminiClient
from src.utils.prompt_templates import format_sql_generation_prompt
from src.utils.error_handler import handle_error, SQLExecutionError
import asyncio
import json
import re
from typing import Dict, Any, List

class SQLAgent:
    def __init__(self):
        self.toolbox_url = "http://localhost:5000"
        self.gemini_client = GeminiClient()
        self.agent = None
        self.schema_cache = {}
        
    async def initialize(self):
        """SQLエージェント初期化"""
        toolbox_client = ToolboxClient(self.toolbox_url)
        sql_tools = await toolbox_client.load_toolset("advanced-sql-toolset")
        
        self.agent = Agent(
            name="sql_specialist",
            model="gemini-2.0-flash-exp",
            instruction="""
            あなたはSQLスペシャリストエージェントです。
            以下の機能を提供します：
            
            1. 自然言語からのSQL生成
            2. SQL構文検証
            3. クエリパフォーマンス分析
            4. テーブルスキーマ分析
            
            注意事項：
            - SELECT文のみ生成してください
            - 危険な操作（DELETE、DROP等）は実行しません
            - セキュリティを最優先に考慮します
            """,
            tools=sql_tools,
            description="高度なSQL処理スペシャリスト"
        )
    
    async def generate_sql_from_natural_language(self, user_request: str) -> Dict[str, Any]:
        """自然言語からSQL生成"""
        try:
            # テーブルスキーマ取得
            schema_info = await self.get_table_schemas(["users"])
            
            # GeminiでSQL生成
            prompt = f"""
            以下の自然言語要求をPostgreSQLクエリに変換してください：
            
            要求: {user_request}
            
            利用可能なテーブル情報:
            {json.dumps(schema_info, indent=2, ensure_ascii=False)}
            
            以下のJSON形式で応答してください：
            {{
              "sql": "SELECT文のSQLクエリ",
              "explanation": "クエリの日本語説明",
              "confidence": "high/medium/low",
              "assumptions": ["前提条件のリスト"],
              "estimated_complexity": "simple/medium/complex"
            }}
            """
            
            gemini_response = await self.gemini_client.generate_structured_response(prompt)
            
            if "error" in gemini_response:
                return {"status": "error", "error": gemini_response["error"]}
            
            # SQL構文検証
            sql_query = gemini_response.get("sql", "")
            validation_result = await self.validate_sql_syntax(sql_query)
            
            return {
                "status": "success",
                "sql": sql_query,
                "explanation": gemini_response.get("explanation", ""),
                "confidence": gemini_response.get("confidence", "medium"),
                "validation": validation_result,
                "generated_by": "gemini-2.0-flash-exp"
            }
            
        except Exception as e:
            return handle_error(e, {"user_request": user_request})
    
    async def validate_sql_syntax(self, sql_query: str) -> Dict[str, Any]:
        """SQL構文検証"""
        if not self.agent:
            await self.initialize()
        
        try:
            # 危険なキーワードチェック
            dangerous_keywords = ["DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE"]
            upper_sql = sql_query.upper()
            
            for keyword in dangerous_keywords:
                if keyword in upper_sql:
                    return {
                        "is_valid": False,
                        "error": f"危険なキーワード '{keyword}' が含まれています",
                        "security_risk": True
                    }
            
            # PostgreSQLでの構文チェック（EXPLAIN使用）
            result = await self.agent.run(f"以下のクエリの構文を検証してください: {sql_query}")
            
            return {
                "is_valid": True,
                "validation_result": str(result),
                "security_risk": False
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": str(e),
                "security_risk": False
            }
    
    async def execute_sql_with_analysis(self, sql_query: str) -> Dict[str, Any]:
        """SQL実行とパフォーマンス分析"""
        if not self.agent:
            await self.initialize()
        
        try:
            # 構文検証
            validation = await self.validate_sql_syntax(sql_query)
            if not validation["is_valid"]:
                return {"status": "error", "error": validation["error"]}
            
            # SQL実行
            execution_result = await self.agent.run(f"以下のクエリを実行してください: {sql_query}")
            
            # パフォーマンス分析
            performance_result = await self.agent.run(
                f"以下のクエリのパフォーマンスを分析してください: {sql_query}"
            )
            
            return {
                "status": "success",
                "query": sql_query,
                "results": str(execution_result),
                "performance_analysis": str(performance_result),
                "execution_timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            return handle_error(e, {"sql_query": sql_query})
    
    async def get_table_schemas(self, table_names: List[str]) -> Dict[str, Any]:
        """テーブルスキーマ情報取得（キャッシュ付き）"""
        if not self.agent:
            await self.initialize()
        
        schemas = {}
        
        for table_name in table_names:
            if table_name in self.schema_cache:
                schemas[table_name] = self.schema_cache[table_name]
                continue
            
            try:
                schema_result = await self.agent.run(f"{table_name}テーブルのスキーマを取得してください")
                schemas[table_name] = str(schema_result)
                self.schema_cache[table_name] = str(schema_result)
            except Exception as e:
                schemas[table_name] = f"Error: {str(e)}"
        
        return schemas

# テスト関数
async def test_sql_agent():
    agent = SQLAgent()
    
    test_cases = [
        "ユーザー一覧を表示して",
        "30歳以上のユーザーの人数を教えて",
        "年齢の平均値を計算して",
        "年齢が最も高いユーザーを見つけて",
        "メールアドレスが gmail.com のユーザーを検索して"
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"要求: {test_case}")
        print(f"{'='*60}")
        
        # SQL生成
        sql_result = await agent.generate_sql_from_natural_language(test_case)
        
        if sql_result["status"] == "success":
            print(f"生成されたSQL: {sql_result['sql']}")
            print(f"説明: {sql_result['explanation']}")
            print(f"信頼度: {sql_result['confidence']}")
            
            # SQL実行とパフォーマンス分析
            execution_result = await agent.execute_sql_with_analysis(sql_result['sql'])
            
            if execution_result["status"] == "success":
                print(f"実行結果: {execution_result['results']}")
            else:
                print(f"実行エラー: {execution_result['error']}")
        else:
            print(f"SQL生成エラー: {sql_result['error']}")

if __name__ == "__main__":
    asyncio.run(test_sql_agent())
```

**動作確認**:
```bash
# MCP Server再起動（新ツール反映）
pkill -f toolbox
uv run toolbox --tools-file config/tools.yaml --port 5000 &

# SQLエージェント単体テスト
uv run python src/agents/sql_agent.py

# ADK Web UIでSQLエージェント単体テスト
uv run adk web
# SQL Specialistエージェントとの詳細対話テスト
```

### Step 5.2: SQLエージェント統合テスト
**tests/test_sql_integration.py作成**:
```python
import pytest
import asyncio
from src.agents.sql_agent import SQLAgent

class TestSQLIntegration:
    """SQL Agent統合テスト"""
    
    @pytest.mark.asyncio
    async def test_sql_generation_basic(self):
        """基本SQL生成テスト"""
        agent = SQLAgent()
        
        result = await agent.generate_sql_from_natural_language("全ユーザーを表示して")
        
        assert result["status"] == "success"
        assert "SELECT" in result["sql"].upper()
        assert "users" in result["sql"].lower()
    
    @pytest.mark.asyncio
    async def test_sql_validation_security(self):
        """SQLセキュリティ検証テスト"""
        agent = SQLAgent()
        
        dangerous_queries = [
            "DELETE FROM users",
            "DROP TABLE users",
            "TRUNCATE users"
        ]
        
        for query in dangerous_queries:
            result = await agent.validate_sql_syntax(query)
            assert result["is_valid"] == False
            assert result["security_risk"] == True
    
    @pytest.mark.asyncio
    async def test_schema_caching(self):
        """スキーマキャッシュテスト"""
        agent = SQLAgent()
        
        # 初回取得
        schema1 = await agent.get_table_schemas(["users"])
        assert "users" in schema1
        
        # 2回目取得（キャッシュから）
        schema2 = await agent.get_table_schemas(["users"])
        assert schema1 == schema2
        assert "users" in agent.schema_cache

# 実行
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**動作確認**:
```bash
# 統合テスト実行
uv run python -m pytest tests/test_sql_integration.py -v

# エラーケーステスト
uv run python -c "
import asyncio
from src.agents.sql_agent import SQLAgent

async def test_errors():
    agent = SQLAgent()
    # 危険なSQL
    result = await agent.validate_sql_syntax('DELETE FROM users')
    print('危険SQLテスト:', result)
    
    # 不正な構文
    result = await agent.validate_sql_syntax('SELCT * FORM users')
    print('構文エラーテスト:', result)

asyncio.run(test_errors())
"
```

**チェックリスト Step 5**:
- [ ] 自然言語からSQL生成確認
- [ ] SQL構文検証機能確認
- [ ] セキュリティチェック機能確認
- [ ] パフォーマンス分析機能確認
- [ ] スキーマキャッシュ機能確認
- [ ] エラーハンドリング確認

## 7. Phase 6: 分析・レポートエージェント実装（3-4日）

### Step 6.1: データ分析エージェント
**src/agents/analysis_agent.py作成**:
```python
from google.adk.agents import Agent
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import json
import asyncio
from src.utils.gemini_client import GeminiClient
from src.utils.error_handler import handle_error

class AnalysisAgent:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.agent = None
        
    async def initialize(self):
        """分析エージェント初期化"""
        self.agent = Agent(
            name="data_analyst",
            model="gemini-2.0-flash-exp",
            instruction="""
            あなたはデータ分析スペシャリストです。
            SQLクエリの結果データを分析し、洞察を提供します。
            
            提供する分析：
            1. 記述統計（平均、中央値、分散等）
            2. トレンド分析
            3. 異常値検出
            4. 相関分析
            5. ビジネス洞察の提供
            """,
            description="データ分析・洞察生成スペシャリスト"
        )
    
    async def analyze_query_results(self, sql_results: str, query_context: str) -> Dict[str, Any]:
        """クエリ結果の分析"""
        try:
            # SQL結果をDataFrameに変換（簡易実装）
            df = self.parse_sql_results_to_dataframe(sql_results)
            
            if df is None or df.empty:
                return {"status": "error", "error": "データの解析に失敗しました"}
            
            # 基本統計の計算
            basic_stats = self.calculate_basic_statistics(df)
            
            # Geminiによる洞察生成
            insights = await self.generate_insights(df, query_context, basic_stats)
            
            return {
                "status": "success",
                "basic_statistics": basic_stats,
                "insights": insights,
                "data_summary": {
                    "total_rows": len(df),
                    "columns": list(df.columns),
                    "data_types": df.dtypes.to_dict()
                }
            }
            
        except Exception as e:
            return handle_error(e, {"query_context": query_context})
    
    def parse_sql_results_to_dataframe(self, sql_results: str) -> pd.DataFrame:
        """SQL結果文字列をDataFrameに変換（簡易実装）"""
        try:
            # 実際の実装では、MCPからの構造化データを使用
            # ここでは簡易的にサンプルデータを作成
            if "users" in sql_results.lower():
                return pd.DataFrame({
                    'id': [1, 2, 3, 4, 5],
                    'name': ['太郎', '花子', '次郎', '三郎', '四郎'],
                    'age': [25, 30, 35, 28, 42],
                    'email': ['taro@example.com', 'hanako@example.com', 
                             'jiro@example.com', 'saburo@example.com', 'shiro@example.com']
                })
            return None
        except:
            return None
    
    def calculate_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """基本統計の計算"""
        stats = {}
        
        for column in df.select_dtypes(include=[np.number]).columns:
            stats[column] = {
                "count": int(df[column].count()),
                "mean": float(df[column].mean()),
                "median": float(df[column].median()),
                "std": float(df[column].std()),
                "min": float(df[column].min()),
                "max": float(df[column].max()),
                "q25": float(df[column].quantile(0.25)),
                "q75": float(df[column].quantile(0.75))
            }
        
        # カテゴリカルデータの統計
        for column in df.select_dtypes(include=['object']).columns:
            stats[column] = {
                "count": int(df[column].count()),
                "unique": int(df[column].nunique()),
                "most_common": df[column].mode().iloc[0] if not df[column].mode().empty else None,
                "most_common_count": int(df[column].value_counts().iloc[0]) if not df[column].empty else 0
            }
        
        return stats
    
    async def generate_insights(self, df: pd.DataFrame, query_context: str, basic_stats: Dict) -> Dict[str, Any]:
        """Geminiによる洞察生成"""
        try:
            prompt = f"""
            以下のデータ分析結果から洞察を生成してください：
            
            クエリの文脈: {query_context}
            データ行数: {len(df)}
            カラム: {list(df.columns)}
            基本統計: {json.dumps(basic_stats, ensure_ascii=False, indent=2)}
            
            以下の観点から洞察を提供してください：
            1. データの特徴と傾向
            2. 注目すべき数値やパターン
            3. ビジネス的な示唆
            4. 推奨されるアクション
            
            以下のJSON形式で応答してください：
            {{
              "key_findings": ["主要な発見事項のリスト"],
              "trends": ["トレンドや傾向"],
              "anomalies": ["異常値や注意点"],
              "business_implications": ["ビジネス的な示唆"],
              "recommended_actions": ["推奨アクション"],
              "confidence_level": "high/medium/low"
            }}
            """
            
            response = await self.gemini_client.generate_structured_response(prompt)
            
            if "error" in response:
                return {"error": response["error"]}
            
            return response
            
        except Exception as e:
            return {"error": str(e)}
    
    async def detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """異常値検出"""
        anomalies = []
        
        for column in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
            
            if not outliers.empty:
                anomalies.append({
                    "column": column,
                    "outlier_count": len(outliers),
                    "outlier_percentage": round(len(outliers) / len(df) * 100, 2),
                    "bounds": {"lower": lower_bound, "upper": upper_bound}
                })
        
        return anomalies

# テスト関数
async def test_analysis_agent():
    agent = AnalysisAgent()
    
    # サンプルSQL結果をシミュレート
    sample_sql_result = """
    ユーザーテーブルから5件のデータを取得しました：
    ID: 1, 名前: 太郎, 年齢: 25
    ID: 2, 名前: 花子, 年齢: 30
    ID: 3, 名前: 次郎, 年齢: 35
    """
    
    query_context = "ユーザーの年齢分布を分析"
    
    print("=== データ分析テスト ===")
    result = await agent.analyze_query_results(sample_sql_result, query_context)
    
    if result["status"] == "success":
        print(f"基本統計: {json.dumps(result['basic_statistics'], ensure_ascii=False, indent=2)}")
        print(f"洞察: {json.dumps(result['insights'], ensure_ascii=False, indent=2)}")
    else:
        print(f"分析エラー: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_analysis_agent())
```

### Step 6.2: レポート生成エージェント
**src/agents/report_agent.py作成**:
```python
from google.adk.agents import Agent
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Any, List
import json
import os
from datetime import datetime
import asyncio
from src.utils.gemini_client import GeminiClient

class ReportAgent:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.agent = None
        self.output_dir = "reports"
        
        # レポート出力ディレクトリ作成
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def initialize(self):
        """レポートエージェント初期化"""
        self.agent = Agent(
            name="report_generator",
            model="gemini-2.0-flash-exp",
            instruction="""
            あなたはレポート生成スペシャリストです。
            データ分析結果を基に、分かりやすいレポートを作成します。
            
            提供する機能：
            1. HTMLレポート生成
            2. グラフ・チャート作成
            3. 洞察の要約
            4. アクションアイテムの提案
            """,
            description="データレポート生成スペシャリスト"
        )
    
    async def generate_html_report(self, analysis_result: Dict[str, Any], query_info: Dict[str, Any]) -> Dict[str, Any]:
        """HTMLレポート生成"""
        try:
            # レポートのメタデータ
            report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Geminiでレポート構造化
            report_content = await self.structure_report_content(analysis_result, query_info)
            
            # HTMLテンプレート生成
            html_content = self.create_html_template(report_content, report_id)
            
            # ファイル保存
            report_path = os.path.join(self.output_dir, f"{report_id}.html")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                "status": "success",
                "report_id": report_id,
                "report_path": report_path,
                "report_url": f"file://{os.path.abspath(report_path)}",
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def structure_report_content(self, analysis_result: Dict[str, Any], query_info: Dict[str, Any]) -> Dict[str, Any]:
        """レポート内容の構造化"""
        prompt = f"""
        以下の分析結果を基に、ビジネスレポートの内容を構造化してください：
        
        クエリ情報: {json.dumps(query_info, ensure_ascii=False)}
        分析結果: {json.dumps(analysis_result, ensure_ascii=False)}
        
        以下のJSON形式でレポート構造を返してください：
        {{
          "title": "レポートタイトル",
          "executive_summary": "要約（2-3文）",
          "key_metrics": ["主要指標のリスト"],
          "findings": ["発見事項のリスト"],
          "recommendations": ["推奨事項のリスト"],
          "next_steps": ["次のステップ"],
          "data_quality_notes": ["データ品質に関する注意事項"]
        }}
        """
        
        response = await self.gemini_client.generate_structured_response(prompt)
        return response if "error" not in response else {"title": "Analysis Report", "executive_summary": "分析完了"}
    
    def create_html_template(self, content: Dict[str, Any], report_id: str) -> str:
        """HTMLテンプレート作成"""
        html = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{content.get('title', 'Auto Analytics Report')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007cba; }}
                .metric {{ background-color: #e8f4f8; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .recommendation {{ background-color: #fff2e8; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .footer {{ color: #666; font-size: 0.9em; margin-top: 40px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{content.get('title', 'Auto Analytics Report')}</h1>
                <p><strong>レポートID:</strong> {report_id}</p>
                <p><strong>生成日時:</strong> {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>📊 要約</h2>
                <p>{content.get('executive_summary', '分析が完了しました。')}</p>
            </div>
            
            <div class="section">
                <h2>🔍 主要指標</h2>
                {self._format_list_items(content.get('key_metrics', []), 'metric')}
            </div>
            
            <div class="section">
                <h2>💡 発見事項</h2>
                {self._format_list_items(content.get('findings', []), 'finding')}
            </div>
            
            <div class="section">
                <h2>🎯 推奨事項</h2>
                {self._format_list_items(content.get('recommendations', []), 'recommendation')}
            </div>
            
            <div class="section">
                <h2>📋 次のステップ</h2>
                {self._format_list_items(content.get('next_steps', []), 'next-step')}
            </div>
            
            <div class="footer">
                <p>このレポートはAuto Analytics AIエージェントにより自動生成されました。</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _format_list_items(self, items: List[str], css_class: str) -> str:
        """リスト項目のHTML フォーマット"""
        if not items:
            return "<p>項目がありません。</p>"
        
        return "".join([f'<div class="{css_class}">• {item}</div>' for item in items])
    
    def create_simple_chart(self, data: Dict[str, Any], chart_type: str = "bar") -> str:
        """簡単なチャート作成"""
        try:
            plt.figure(figsize=(10, 6))
            
            # サンプルデータでチャート作成
            if chart_type == "bar":
                categories = ['カテゴリA', 'カテゴリB', 'カテゴリC']
                values = [23, 45, 56]
                plt.bar(categories, values)
                plt.title('データ分析結果')
                plt.ylabel('値')
            
            # チャート保存
            chart_path = os.path.join(self.output_dir, f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            return f"チャート生成エラー: {str(e)}"

# テスト関数
async def test_report_agent():
    agent = ReportAgent()
    
    # サンプル分析結果
    sample_analysis = {
        "status": "success",
        "basic_statistics": {
            "age": {"mean": 30.4, "median": 30, "std": 4.5}
        },
        "insights": {
            "key_findings": ["平均年齢は30.4歳", "標準偏差は4.5歳で分散は小さい"],
            "business_implications": ["若い世代が中心", "年齢層が比較的均一"]
        }
    }
    
    sample_query_info = {
        "sql": "SELECT age FROM users",
        "context": "ユーザー年齢分析"
    }
    
    print("=== レポート生成テスト ===")
    result = await agent.generate_html_report(sample_analysis, sample_query_info)
    
    if result["status"] == "success":
        print(f"レポート生成成功: {result['report_path']}")
        print(f"レポートURL: {result['report_url']}")
    else:
        print(f"レポート生成エラー: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_report_agent())
```

**動作確認**:
```bash
# 分析エージェントテスト
uv run python src/agents/analysis_agent.py

# レポートエージェントテスト
uv run python src/agents/report_agent.py

# 生成されたレポート確認
ls -la reports/
# HTMLファイルをブラウザで確認
```

**チェックリスト Step 6**:
- [ ] データ分析エージェント動作確認
- [ ] 基本統計計算確認
- [ ] 洞察生成機能確認
- [ ] HTMLレポート生成確認
- [ ] チャート作成機能確認

## 8. Phase 7: 統合テスト・完成（2-3日）

### Step 8.1: エンドツーエンド統合
**src/main.py更新（完全版）**:
```python
from google.adk.agents import Agent
from toolbox_core import ToolboxClient
from src.agents.main_agent import MainAgent
from src.agents.sql_agent import SQLAgent
from src.agents.analysis_agent import AnalysisAgent
from src.agents.report_agent import ReportAgent
import asyncio
import os

class AutoAnalyticsSystem:
    def __init__(self):
        self.main_agent = MainAgent()
        self.sql_agent = SQLAgent()
        self.analysis_agent = AnalysisAgent()
        self.report_agent = ReportAgent()
        self.initialized = False
    
    async def initialize(self):
        """システム全体初期化"""
        if self.initialized:
            return
        
        print("🚀 Auto Analytics システム初期化中...")
        
        await self.main_agent.initialize()
        await self.sql_agent.initialize()
        await self.analysis_agent.initialize()
        await self.report_agent.initialize()
        
        self.initialized = True
        print("✅ システム初期化完了")
    
    async def process_full_workflow(self, user_request: str) -> dict:
        """完全な分析ワークフロー実行"""
        if not self.initialized:
            await self.initialize()
        
        print(f"📝 ユーザー要求: {user_request}")
        
        # Step 1: メインエージェントで要求処理
        main_result = await self.main_agent.process_request(user_request)
        if main_result["status"] != "success":
            return main_result
        
        print("✅ Step 1: 要求理解完了")
        
        # Step 2: SQL生成・実行
        sql_result = await self.sql_agent.generate_sql_from_natural_language(user_request)
        if sql_result["status"] != "success":
            return sql_result
        
        print(f"✅ Step 2: SQL生成完了 - {sql_result['sql']}")
        
        execution_result = await self.sql_agent.execute_sql_with_analysis(sql_result['sql'])
        if execution_result["status"] != "success":
            return execution_result
        
        print("✅ Step 3: SQL実行完了")
        
        # Step 4: データ分析
        analysis_result = await self.analysis_agent.analyze_query_results(
            execution_result['results'], user_request
        )
        if analysis_result["status"] != "success":
            return analysis_result
        
        print("✅ Step 4: データ分析完了")
        
        # Step 5: レポート生成
        report_result = await self.report_agent.generate_html_report(
            analysis_result, 
            {"sql": sql_result['sql'], "context": user_request}
        )
        if report_result["status"] != "success":
            return report_result
        
        print(f"✅ Step 5: レポート生成完了 - {report_result['report_path']}")
        
        return {
            "status": "success",
            "workflow_completed": True,
            "steps": {
                "main_agent": main_result,
                "sql_generation": sql_result,
                "sql_execution": execution_result,
                "data_analysis": analysis_result,
                "report_generation": report_result
            },
            "final_report": report_result['report_url']
        }

# ADK Web UI用のルートエージェント
auto_analytics_system = AutoAnalyticsSystem()

async def create_root_agent():
    """ADK用ルートエージェント作成"""
    await auto_analytics_system.initialize()
    
    root_agent = Agent(
        name="auto_analytics_root",
        model="gemini-2.0-flash-exp",
        instruction="""
        あなたはAuto Analytics AIシステムのメインインターフェースです。
        ユーザーのデータ分析要求を受け取り、完全な分析ワークフローを実行します。
        
        システムの機能：
        1. 自然言語での分析要求理解
        2. SQLクエリ自動生成・実行
        3. データ分析・洞察生成
        4. HTMLレポート自動作成
        
        使用例：
        - "ユーザーの年齢分布を分析して"
        - "30歳以上のユーザー数を教えて"
        - "年齢の統計情報をレポートにして"
        """,
        description="Auto Analytics 統合システム"
    )
    
    return root_agent

# メイン実行
async def main():
    """メイン実行関数"""
    system = AutoAnalyticsSystem()
    
    # システム動作テスト
    test_requests = [
        "ユーザー一覧を表示してレポートを作成して",
        "30歳以上のユーザーの統計分析をして",
        "年齢の平均値と分散をレポートにまとめて"
    ]
    
    for request in test_requests:
        print(f"\n{'='*80}")
        print(f"🔍 テスト要求: {request}")
        print(f"{'='*80}")
        
        result = await system.process_full_workflow(request)
        
        if result["status"] == "success":
            print(f"🎉 ワークフロー完了!")
            print(f"📊 最終レポート: {result['final_report']}")
        else:
            print(f"❌ エラー: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    # コンソール実行
    asyncio.run(main())

# ADK Web UI用
root_agent = None
asyncio.create_task(create_root_agent().then(lambda agent: globals().update(root_agent=agent)))
```

### Step 8.2: 最終動作確認手順
```bash
# 1. 全サービス起動確認
echo "=== サービス起動確認 ==="

# PostgreSQL確認
psql -h localhost -U analytics_user -d analytics -c "SELECT COUNT(*) FROM users;"

# genai-toolbox MCP Server確認
curl http://localhost:5000/health

# 2. 完全統合テスト
echo "=== 完全統合テスト ==="
uv run python src/main.py

# 3. ADK Web UI最終テスト
echo "=== ADK Web UI最終テスト ==="
uv run adk web --port 8080

# ブラウザで以下をテスト：
# - "ユーザーの年齢分析をしてレポートを作成して"
# - "30歳以上のユーザー数を教えて"
# - "全ユーザーの統計情報をまとめて"

# 4. 生成されたレポート確認
echo "=== 生成レポート確認 ==="
ls -la reports/
open reports/*.html  # macOSの場合
```

### Step 8.3: パフォーマンス・品質チェック
**tests/test_performance.py作成**:
```python
import asyncio
import time
import pytest
from src.main import AutoAnalyticsSystem

class TestPerformance:
    @pytest.mark.asyncio
    async def test_end_to_end_performance(self):
        """エンドツーエンドパフォーマンステスト"""
        system = AutoAnalyticsSystem()
        
        start_time = time.time()
        
        result = await system.process_full_workflow("ユーザー一覧を分析してレポートを作成して")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 3秒以内での完了を確認
        assert execution_time < 3.0, f"処理時間が遅すぎます: {execution_time}秒"
        assert result["status"] == "success"
        
        print(f"実行時間: {execution_time:.2f}秒")

# パフォーマンステスト実行
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

# テスト実行コマンド
# uv run python tests/test_performance.py
```

**最終チェックリスト**:
- [ ] PostgreSQL接続正常
- [ ] genai-toolbox MCP Server動作正常
- [ ] Gemini API接続正常
- [ ] 全エージェント初期化成功
- [ ] エンドツーエンドワークフロー動作
- [ ] HTMLレポート生成成功
- [ ] ADK Web UI完全動作
- [ ] エラーハンドリング正常
- [ ] パフォーマンス要件満足（3秒以内）
- [ ] セキュリティチェック通過

## 9. 運用・保守手順

### 9.1 日常運用チェック
```bash
#!/bin/bash
# daily_check.sh - 日次ヘルスチェック

echo "=== Auto Analytics 日次ヘルスチェック ==="

# PostgreSQL接続確認（devcontainer環境）
echo "1. PostgreSQL接続確認"
PGPASSWORD=secure_password psql -h localhost -U analytics_user -d analytics -c "SELECT 'OK' as status;" || echo "❌ PostgreSQL接続失敗"

# MCP Server確認
echo "2. MCP Server確認"
curl -f http://localhost:5000/health || echo "❌ MCP Server接続失敗"

# Gemini API確認
echo "3. Gemini API確認"
uv run python -c "
import os
import google.generativeai as genai
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content('Hello')
print('✅ Gemini API正常' if response else '❌ Gemini API異常')
"

# ディスク容量確認
echo "4. ディスク容量確認"
df -h | grep -E "(filesystem|/workspace)"

echo "=== ヘルスチェック完了 ==="
```

### 9.2 トラブルシューティング
```bash
# よくある問題と解決方法

# 1. MCP Server接続失敗
pkill -f toolbox
uv run toolbox --tools-file config/tools.yaml --port 5000 &

# 2. PostgreSQL接続失敗（devcontainer環境）
# devcontainer内では.devcontainer/docker-compose.ymlで管理
echo "PostgreSQL は .devcontainer/docker-compose.yml で管理されています"
echo "VS Code devcontainer を再起動してください"

# または直接確認
PGPASSWORD=password psql -h localhost -U postgres -c "SELECT 1;" || echo "PostgreSQL サービス確認が必要"

# 3. Gemini API制限エラー
# APIキー確認・レート制限待機

# 4. メモリ不足
# システムリソース確認
free -h
ps aux --sort=-%mem | head
```

## 10. uv環境 便利コマンド集

### 10.1 基本コマンド
```bash
# 依存関係同期（初回セットアップ）
uv sync

# 新しいパッケージ追加
uv add package-name

# 開発依存関係追加
uv add --dev package-name

# パッケージ削除
uv remove package-name

# プロジェクト内でコマンド実行
uv run command

# Python REPL起動
uv run python

# 依存関係ツリー表示
uv tree

# 環境情報表示
uv info
```

### 10.2 開発時によく使うコマンド（devcontainer内）
```bash
# Auto Analytics 起動
uv run python src/main.py

# ADK Web UI起動（devcontainer ポート転送あり）
uv run adk web --host 0.0.0.0 --port 8080

# MCP Server起動
uv run toolbox --tools-file config/tools.yaml --port 5000

# テスト実行
uv run python -m pytest tests/ -v

# 特定エージェントテスト
uv run python src/agents/main_agent.py

# フォーマット（設定済みの場合）
uv run black src/
uv run isort src/
```

### 10.3 devcontainer PostgreSQL管理
```bash
# PostgreSQL接続（Analytics用）
PGPASSWORD=secure_password psql -h localhost -U analytics_user -d analytics

# PostgreSQL接続（管理者）
PGPASSWORD=password psql -h localhost -U postgres

# データベース状態確認
PGPASSWORD=secure_password psql -h localhost -U analytics_user -d analytics -c "
SELECT 
    current_database() as database,
    current_user as user,
    version() as postgres_version;
"

# テーブル一覧確認
PGPASSWORD=secure_password psql -h localhost -U analytics_user -d analytics -c "\dt"

# Analytics データベース再初期化
PGPASSWORD=password psql -h localhost -U postgres -f /workspace/init_analytics.sql
```

### 10.4 トラブルシューティング
```bash
# キャッシュクリア
uv cache clean

# 環境再構築
rm -rf .venv uv.lock
uv sync

# Python版確認・変更
uv python list
uv python pin 3.11
```

---

この開発手順書により、uvを活用した段階的で確実な実装が可能になります。各ステップで動作確認を行いながら進めることで、問題の早期発見と修正が可能です。