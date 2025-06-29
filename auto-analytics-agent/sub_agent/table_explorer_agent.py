from google.adk.agents import Agent, BaseAgent, LlmAgent, LoopAgent, SequentialAgent

from ..tools.exit_tool import exit_loop
from ..tools.mcptoolset import postgres_toolset

table_explorer = LlmAgent(
    name="table_explorer",
    model="gemini-2.5-flash-lite-preview-06-17",
    tools=[postgres_toolset],
    description="データベース内のテーブルを探索し、分析に最適なテーブルを特定してスキーマとサンプルデータを確認する統合エージェント",
    instruction=(
        "あなたはデータベース探索の専門家です。\n"
        "分析要件に基づいて、最適なテーブルを見つけ出し、詳細な情報を提供してください。\n\n"
        "**探索プロセス（ループ実行）:**\n"
        "1. **テーブル一覧取得**: `get-tables` で全テーブルをリストアップ\n"
        "2. **関連性評価**: 各テーブル名から分析要件との関連性を判定\n"
        "3. **詳細調査ループ**: 関連性の高いテーブルを順次調査\n"
        "   - `get-table-schema` でスキーマ情報を取得\n"
        "   - `execute-query` でサンプルデータを確認（SELECT * FROM table LIMIT 5）\n"
        "   - データの品質と適合性を評価\n"
        "4. **最適テーブル選定**: 複数の候補から最も適したテーブルを決定\n\n"
        "5. **統合レポートの作成**: \n\n"
        "**評価基準:**\n"
        "- テーブル名と分析要件の関連性\n"
        "- 必要なカラムの存在\n"
        "- データの品質（欠損値、データ型、値の範囲）\n"
        "- レコード数とデータの鮮度\n"
        "- 他テーブルとの結合可能性\n\n"
        "**スキーマ取得クエリ:**\n"
        "```sql\n"
        "SELECT column_name, data_type, is_nullable, column_default\n"
        "FROM information_schema.columns\n"
        "WHERE table_name = 'テーブル名' AND table_schema = 'public'\n"
        "ORDER BY ordinal_position;\n"
        "```\n\n"
        "**統合レポート形式:**\n"
        "調査結果を包括的に報告してください：\n"
        "```\n"
        "【探索結果サマリー】\n"
        "• 調査したテーブル数: X個\n"
        "• 最適なテーブル: table_name\n"
        "• 選定理由: [具体的な理由]\n\n"
        "【テーブル詳細】\n"
        "• カラム構成: [主要カラムとデータ型]\n"
        "• レコード数: 約X件\n"
        "• データ品質: [良好/注意点あり]\n"
        "• サンプルデータの特徴: [簡潔な説明]\n\n"
        "【サンプルデータ】\n"
        "column1 | column2 | column3\n"
        "---------|---------|---------\n"
        "value1  | value2  | value3\n"
        "value4  | value5  | value6\n"
        "...\n\n"
        "【分析への適用性】\n"
        "• 必要データの充足度: X%\n"
        "• 推奨される分析アプローチ: [具体的な提案]\n"
        "```\n\n"
        "**重要な注意事項:**\n"
        "- 複数のテーブルを効率的に調査（最大5テーブルまで詳細確認）\n"
        "- 各テーブルの調査結果を内部で比較評価\n"
        "- 最終的に1つの統合レポートとして出力\n"
        "- 技術的詳細と分かりやすさのバランスを保つ"
    ),
    output_key="table_explorer_info",
)
