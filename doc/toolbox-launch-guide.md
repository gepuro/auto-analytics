# Toolbox起動ガイド

## 概要

このドキュメントでは、Auto Analytics AIエージェントプロジェクトで使用される「toolbox」の起動方法について説明します。

「toolbox」とは、genai-toolboxバイナリファイルのことで、MCPサーバーとして動作し、PostgreSQLデータベースへの接続機能を提供します。

## Toolboxについて

### 役割
- **MCPサーバー**: Model Context Protocol（MCP）サーバーとして動作
- **データベース接続**: PostgreSQLデータベースへの安全な接続を提供
- **ツール提供**: データ分析に必要な各種ツールを提供

### 提供ツール
1. **test-connection**: PostgreSQL接続テスト
2. **get-users**: ユーザー一覧取得
3. **get-table-schema**: テーブルスキーマ情報取得
4. **execute-query**: 動的SQLクエリ実行（SELECT文のみ）

## 前提条件

### 1. PostgreSQL環境
- PostgreSQLサーバーが起動済み
- データベース: `analytics_db`
- ユーザー: `analytics_user`
- パスワード: `analytics_password`

### 2. 設定ファイル
必要な設定ファイルが準備済み：
- `/workspace/config/tools.yaml`
- `/workspace/.env`

## 起動方法

### 1. 設定ファイル確認

#### config/tools.yaml
```yaml
sources:
  analytics-postgres:
    type: postgresql
    connection_string: "postgresql://analytics_user:analytics_password@postgres:5432/analytics_db"

tools:
  test-connection:
    description: "PostgreSQL接続をテストします"
    type: postgresql
    source: analytics-postgres
    query: "SELECT 1 as test"

  get-users:
    description: "ユーザー一覧を取得します"
    type: postgresql
    source: analytics-postgres
    query: "SELECT id, name, email, age FROM users LIMIT {{limit}}"
    parameters:
      limit:
        type: integer
        default: 10

  get-table-schema:
    description: "指定されたテーブルのスキーマ情報を取得します"
    type: postgresql
    source: analytics-postgres
    query: |
      SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default
      FROM information_schema.columns
      WHERE table_name = '{{table_name}}'
      ORDER BY ordinal_position
    parameters:
      table_name:
        type: string
        required: true

  execute-query:
    description: "動的SQLクエリを実行します（SELECT文のみ）"
    type: postgresql
    source: analytics-postgres
    query: "{{sql}}"
    parameters:
      sql:
        type: string
        required: true

toolsets:
  analytics-toolset:
    description: "Analytics用ツールセット"
    tools:
      - test-connection
      - get-users
      - get-table-schema
      - execute-query
```

#### .env
```env
# Google API
GOOGLE_API_KEY=your_actual_gemini_api_key_here

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=analytics_db
POSTGRES_USER=analytics_user
POSTGRES_PASSWORD=analytics_password

# MCP Server
TOOLBOX_SERVER_URL=http://127.0.0.1:5000
TOOLBOX_TIMEOUT=30
TOOLBOX_MAX_RETRIES=3
TOOLBOX_RETRY_DELAY=1.0
```

### 2. Toolbox起動

#### 基本起動コマンド
```bash
cd /workspace
./toolbox --tools-file config/tools.yaml --port 5000
```

#### バックグラウンド実行
```bash
nohup ./toolbox --tools-file config/tools.yaml --port 5000 > logs/toolbox.log 2>&1 &
```

### 3. 起動確認

#### プロセス確認
```bash
ps aux | grep toolbox
```

#### ヘルスチェック
```bash
curl http://localhost:5000/health
```

#### ログ確認
```bash
tail -f logs/toolbox.log
```

### 4. 正常起動時のメッセージ例
```
Hello, World!
genai-toolbox server started on port 5000
Initialized 1 source: analytics-postgres
Initialized 4 tools: test-connection, get-users, get-table-schema, execute-query
Initialized 2 toolsets: analytics-toolset
```

## 利用方法

### MCP Connectorからの接続
```python
from src.utils.mcp_connector import MCPConnector, MCPConfig

# 設定
config = MCPConfig(
    server_url="http://127.0.0.1:5000",
    timeout=30
)

# 接続して利用
async with MCPConnector(config) as mcp:
    # 接続テスト
    result = await mcp.test_connection()
    
    # ユーザー一覧取得
    users = await mcp.get_users(limit=5)
    
    # SQLクエリ実行
    query_result = await mcp.execute_query("SELECT COUNT(*) FROM users")
```

### curlでの直接テスト
```bash
# ツール一覧取得
curl http://localhost:5000/tools

# ツール実行例
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "test-connection",
    "parameters": {}
  }'
```

## トラブルシューティング

### 1. 起動に失敗する場合

#### PostgreSQL接続エラー
```
Error: Failed to connect to PostgreSQL
```
**対処法**:
- PostgreSQLサーバーが起動しているか確認
- 接続情報（ホスト、ポート、認証情報）を確認
- ネットワーク接続を確認

#### 設定ファイルエラー
```
Error: Invalid configuration file
```
**対処法**:
- `config/tools.yaml`の構文を確認
- 必要なパラメータが設定されているか確認

#### ポート使用中エラー
```
Error: Port 5000 already in use
```
**対処法**:
- 別のポートを指定: `--port 5001`
- 既存プロセスを停止: `pkill -f toolbox`

### 2. 実行時エラー

#### SQLエラー
- クエリ構文を確認
- テーブル名、カラム名の存在を確認
- 権限設定を確認

#### タイムアウトエラー
- クエリの複雑さを確認
- インデックスの設定を確認
- タイムアウト設定を調整

### 3. パフォーマンス問題

#### 接続数制限
- PostgreSQLの最大接続数設定を確認
- 接続プールの設定を検討

#### メモリ使用量
- 大きなデータセットの処理時は注意
- LIMIT句の使用を推奨

## 停止方法

### プロセスID確認
```bash
ps aux | grep toolbox
```

### 停止
```bash
# プロセスIDを指定して停止
kill <PID>

# 強制停止
kill -9 <PID>

# 名前で停止
pkill -f toolbox
```

## 設定カスタマイズ

### 新しいツール追加
`config/tools.yaml`にツール定義を追加:

```yaml
tools:
  custom-analysis:
    description: "カスタム分析クエリ"
    type: postgresql
    source: analytics-postgres
    query: |
      SELECT 
        category,
        COUNT(*) as count,
        AVG(price) as avg_price
      FROM products
      GROUP BY category
      ORDER BY count DESC
```

### 環境変数での設定上書き
- `TOOLBOX_SERVER_URL`: サーバーURL
- `TOOLBOX_TIMEOUT`: タイムアウト値
- `TOOLBOX_MAX_RETRIES`: リトライ回数

## 参考情報

### ログレベル設定
環境変数で設定可能:
```bash
export LOG_LEVEL=DEBUG
./toolbox --tools-file config/tools.yaml --port 5000
```

### 設定ファイルの検証
```bash
./toolbox validate --tools-file config/tools.yaml
```

### バージョン確認
```bash
./toolbox version
```

---

**注意**: このドキュメントは、Auto Analytics AIエージェントプロジェクトのPhase 1開発時の情報に基づいています。最新の情報については、開発ログや設定ファイルも合わせて確認してください。