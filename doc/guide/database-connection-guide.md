# Auto Analytics - データベース接続ガイド

## 📋 概要
このドキュメントでは、Auto Analytics プロジェクトでのPostgreSQLデータベースへの接続方法を説明します。

## 🔧 devcontainer環境での接続設定

### データベース基本情報
- **イメージ**: postgres:15-alpine
- **コンテナ名**: auto-analytics-postgres
- **ネットワーク**: auto-analytics-dev-network

### 接続パラメータ
```bash
ホスト名: postgres
ポート: 5432
データベース名: analytics_db
ユーザー名: analytics_user
パスワード: analytics_password
```

### 環境変数設定（.env）
```env
# PostgreSQL設定（.devcontainer/docker-compose.yml起動済み）
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=analytics_db
POSTGRES_USER=analytics_user
POSTGRES_PASSWORD=analytics_password
POSTGRES_URL=postgresql://analytics_user:analytics_password@postgres:5432/analytics_db
```

## 🚀 接続方法

### 1. psqlコマンドライン接続
```bash
# 基本接続
PGPASSWORD=analytics_password psql -h postgres -U analytics_user -d analytics_db

# ワンライナーでSQL実行
PGPASSWORD=analytics_password psql -h postgres -U analytics_user -d analytics_db -c "SELECT version();"
```

### 2. Python接続（psycopg2）
```python
import psycopg2
from urllib.parse import urlparse
import os

# 環境変数から接続情報取得
DATABASE_URL = os.getenv("POSTGRES_URL")

# 接続例1: URLから接続
conn = psycopg2.connect(DATABASE_URL)

# 接続例2: パラメータ指定
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"), 
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)
```

### 3. Python接続（asyncpg）
```python
import asyncpg
import os

async def connect_db():
    DATABASE_URL = os.getenv("POSTGRES_URL")
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

# 使用例
async def example():
    conn = await connect_db()
    result = await conn.fetch("SELECT * FROM users LIMIT 5")
    await conn.close()
    return result
```

## 📊 データベース構造

### 既存テーブル
1. **users テーブル**
   - 総レコード数: 10件
   - 主要カラム: id, name, email, age, created_at
   - 平均年齢: 32.4歳

2. **orders テーブル**
   - 注文情報

3. **products テーブル**
   - 商品情報

### サンプルクエリ
```sql
-- ユーザー統計
SELECT 
    COUNT(*) as total_users,
    ROUND(AVG(age), 2) as avg_age,
    MIN(age) as min_age,
    MAX(age) as max_age
FROM users;

-- 年齢分布
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
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. 接続エラー「Connection refused」
```bash
# 原因: 間違ったホスト名
❌ PGPASSWORD=analytics_password psql -h localhost -U analytics_user -d analytics_db

# 解決: 正しいホスト名（コンテナ名）を使用
✅ PGPASSWORD=analytics_password psql -h postgres -U analytics_user -d analytics_db
```

#### 2. 認証エラー「password authentication failed」
```bash
# 原因: 間違ったパスワード
❌ PGPASSWORD=wrong_password psql -h postgres -U analytics_user -d analytics_db

# 解決: 正しいパスワードを使用
✅ PGPASSWORD=analytics_password psql -h postgres -U analytics_user -d analytics_db
```

#### 3. psqlコマンドが見つからない
```bash
# PostgreSQLクライアントインストール
apt-get update
apt-get install -y postgresql-client
```

## 🎯 ベストプラクティス

### 1. 環境変数の活用
- ハードコードではなく環境変数を使用
- .envファイルで設定を統一管理

### 2. 接続プールの使用（本格運用時）
```python
# asyncpgでの接続プール例
import asyncpg

async def create_pool():
    return await asyncpg.create_pool(
        os.getenv("POSTGRES_URL"),
        min_size=1,
        max_size=10
    )
```

### 3. セキュリティ考慮事項
- パスワードをコードに直接記載しない
- 環境変数やシークレット管理システムを使用
- 本番環境では適切な権限設定を実施

---

**最終更新**: 2025-01-20  
**更新者**: Auto Analytics開発チーム