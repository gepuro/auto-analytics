import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

# ワークフロー制御システムをインポート
try:
    from .workflow_controller import (
        workflow_controller,
        check_information_completeness_v2,
        generate_user_questions,
        integrate_user_feedback
    )
except ImportError:
    # パッケージとしてではなく直接実行される場合の対応
    import workflow_controller as wc_module
    workflow_controller = wc_module.workflow_controller
    check_information_completeness_v2 = wc_module.check_information_completeness_v2
    generate_user_questions = wc_module.generate_user_questions
    integrate_user_feedback = wc_module.integrate_user_feedback

# シンプルなHTMLレポート生成関数を直接実装
def generate_html_report_from_workflow(
    workflow_context: str,
    report_title: Optional[str] = None
) -> str:
    """
    ワークフローからHTMLレポートを生成する関数（自己完結版）
    
    Args:
        workflow_context: ワークフロー結果（JSON文字列）
        report_title: レポートタイトル
        
    Returns:
        レポート生成結果（JSON文字列）
    """
    try:
        # JSONパース
        if isinstance(workflow_context, str):
            context = json.loads(workflow_context)
        else:
            context = workflow_context
        
        # ワークフローの各ステップの結果を抽出
        analysis_data = {}
        step_mappings = {
            'interpreted_request': ['interpreted_request', 'request_interpretation', 'user_request'],
            'schema_info': ['schema_info', 'database_schema', 'table_info'],
            'sample_analysis': ['sample_analysis', 'data_sample', 'sample_data'],
            'sql_query_info': ['sql_query_info', 'sql_query', 'generated_sql'],
            'query_execution_result': ['query_execution_result', 'execution_result', 'query_result'],
            'analysis_results': ['analysis_results', 'data_analysis', 'insights']
        }
        
        for target_key, source_keys in step_mappings.items():
            for source_key in source_keys:
                if source_key in context:
                    analysis_data[target_key] = context[source_key]
                    break
        
        # HTMLテンプレート（シンプル版）
        html_template = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f8f9fa; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; margin: -40px -40px 30px -40px; border-radius: 12px 12px 0 0; }}
        .section {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea; }}
        .section h3 {{ margin-top: 0; color: #495057; }}
        .sql-code {{ background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 6px; font-family: 'Monaco', 'Consolas', monospace; overflow-x: auto; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        .data-table th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
        .data-table td {{ padding: 10px; border-bottom: 1px solid #dee2e6; }}
        .insights {{ background: #e8f5e8; border-left-color: #28a745; }}
        .metadata {{ font-size: 0.9em; color: #6c757d; margin-top: 30px; padding: 15px; background: #f1f3f4; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {title}</h1>
            <p>生成日時: {generation_time}</p>
        </div>
        
        {request_section}
        {schema_section}
        {sql_section}
        {data_section}
        {insights_section}
        
        <div class="metadata">
            <strong>📝 レポート情報:</strong><br>
            生成システム: Auto Analytics AI Agent<br>
            エンジン: Google ADK + Gemini 2.5 Flash<br>
            レポート形式: HTML
        </div>
    </div>
</body>
</html>"""

        # セクション生成
        sections = []
        
        if analysis_data.get('interpreted_request'):
            sections.append(f"""
        <div class="section">
            <h3>🎯 分析リクエスト</h3>
            <p>{analysis_data['interpreted_request']}</p>
        </div>""")
        
        if analysis_data.get('schema_info'):
            sections.append(f"""
        <div class="section">
            <h3>🗄️ データベース情報</h3>
            <p>{analysis_data['schema_info']}</p>
        </div>""")
        
        if analysis_data.get('sql_query_info'):
            sql_query = analysis_data['sql_query_info']
            if isinstance(sql_query, dict):
                sql_query = sql_query.get('query', str(sql_query))
            sections.append(f"""
        <div class="section">
            <h3>🔍 実行SQLクエリ</h3>
            <div class="sql-code">{sql_query}</div>
        </div>""")
        
        if analysis_data.get('query_execution_result'):
            result_data = analysis_data['query_execution_result']
            if isinstance(result_data, dict) and 'data' in result_data:
                data = result_data['data']
                if data and len(data) > 0:
                    # テーブル作成
                    headers = list(data[0].keys()) if isinstance(data[0], dict) else [f'Column {i+1}' for i in range(len(data[0]))]
                    table_html = '<table class="data-table"><thead><tr>'
                    for header in headers:
                        table_html += f'<th>{header}</th>'
                    table_html += '</tr></thead><tbody>'
                    
                    for row in data[:10]:  # 最初の10行のみ表示
                        table_html += '<tr>'
                        for header in headers:
                            value = row.get(header, '') if isinstance(row, dict) else row[headers.index(header)]
                            table_html += f'<td>{value}</td>'
                        table_html += '</tr>'
                    table_html += '</tbody></table>'
                    
                    sections.append(f"""
        <div class="section">
            <h3>📈 クエリ実行結果</h3>
            <p>データ件数: {len(data)} 件 {('(最初の10件を表示)' if len(data) > 10 else '')}</p>
            {table_html}
        </div>""")
        
        if analysis_data.get('analysis_results'):
            sections.append(f"""
        <div class="section insights">
            <h3>💡 分析結果・洞察</h3>
            <p>{analysis_data['analysis_results']}</p>
        </div>""")
        
        # ファイル名とパス生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analytics_report_{timestamp}.html"
        
        # 保存先ディレクトリ確保（より確実な方法）
        try:
            current_dir = Path(__file__).parent
            workspace_root = current_dir.parent
            reports_dir = workspace_root / "reports"
        except:
            # フォールバック: 絶対パスで指定
            reports_dir = Path("/workspace/reports")
        
        # ディレクトリ作成と権限確認
        reports_dir.mkdir(exist_ok=True)
        if not reports_dir.exists():
            raise Exception(f"レポートディレクトリの作成に失敗: {reports_dir}")
        
        file_path = reports_dir / filename
        
        # HTML生成
        html_content = html_template.format(
            title=report_title or "データ分析レポート",
            generation_time=datetime.now().strftime("%Y年%m月%d日 %H:%M:%S"),
            request_section=sections[0] if len(sections) > 0 else "",
            schema_section=sections[1] if len(sections) > 1 else "",
            sql_section=sections[2] if len(sections) > 2 else "",
            data_section=sections[3] if len(sections) > 3 else "",
            insights_section=sections[4] if len(sections) > 4 else ""
        )
        
        # ファイル保存（エラーハンドリング強化）
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # ファイル作成確認
            if not file_path.exists():
                raise Exception("ファイルの書き込みに失敗しました")
            
            actual_file_size = file_path.stat().st_size
            
        except PermissionError:
            raise Exception(f"ファイル書き込み権限がありません: {file_path}")
        except OSError as e:
            raise Exception(f"ファイル書き込み中にOSエラー: {e}")
        except Exception as e:
            raise Exception(f"ファイル保存中にエラー: {e}")
        
        # 成功レスポンス
        response = {
            "success": True,
            "message": "✅ HTMLレポートが正常に生成されました！",
            "file_path": str(file_path),
            "filename": filename,
            "report_title": report_title or "データ分析レポート",
            "generation_time": datetime.now().strftime("%Y年%m月%d日 %H:%M:%S"),
            "report_url": f"http://127.0.0.1:9000/reports/{filename}",
            "report_list_url": "http://127.0.0.1:9000/",
            "fastapi_instructions": "FastAPIサーバー (port 9000) を起動してアクセス: cd fastapi-server && python main.py",
            "file_size": f"{actual_file_size / 1024:.1f} KB",
            "content_length": len(html_content)
        }
        
        return json.dumps(response, ensure_ascii=False, indent=2)
        
    except Exception as e:
        # エラーレスポンス
        error_response = {
            "success": False,
            "error": str(e),
            "message": f"❌ HTMLレポート生成中にエラーが発生しました: {str(e)}"
        }
        return json.dumps(error_response, ensure_ascii=False, indent=2)

# PostgreSQL MCP Server接続設定
postgres_toolset = MCPToolset(
    connection_params=SseConnectionParams(url="http://localhost:5000/mcp/sse")
)

# 1. Request Interpreter Agent - ユーザーリクエストの解釈
request_interpreter = Agent(
    name="request_interpreter",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="自然言語の分析リクエストを構造化された形式に変換する専門エージェント",
    instruction=(
        "あなたは親しみやすいデータ分析アシスタントです。\n"
        "ユーザーの分析リクエストを理解し、分かりやすい言葉で分析計画を説明してください。\n\n"
        "**あなたの役割:**\n"
        "ユーザーが何を知りたがっているのかを理解し、次のような内容を自然な文章で説明してください：\n"
        "- どのような種類の分析が必要か（売上分析、顧客分析、トレンド分析など）\n"
        "- どのようなデータが必要になりそうか\n"
        "- 分析を行う上での条件や期間があるか\n"
        "- もし不明な点があれば、確認したい内容を優しく質問\n\n"
        "**コミュニケーションスタイル:**\n"
        "- 専門用語は避け、分かりやすい言葉を使用\n"
        "- 親しみやすく、丁寧な口調\n"
        "- ユーザーの意図を確認し、必要に応じて詳細を質問\n"
        "- 日本語と英語の両方に対応\n\n"
        "例：「ご依頼の内容を拝見すると、〇〇についての分析をお求めのようですね。\n"
        "この分析を行うためには、△△のデータが必要になります。\n"
        "もしよろしければ、□□についてもう少し詳しく教えていただけますでしょうか？」"
    ),
    output_key="interpreted_request",
)

# 1.5 Information Gap Detector Agent - 情報不足検出エージェント
information_gap_detector = Agent(
    name="information_gap_detector",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="分析リクエストの情報の完全性を評価し、追加情報が必要かどうかを判断する専門エージェント",
    instruction=(
        "あなたは分析リクエストの完全性チェック専門家です。\n"
        "ユーザーからの分析リクエストを詳しく分析し、分析を実行するのに十分な情報があるかを判断してください。\n\n"
        "**あなたの評価基準:**\n"
        "以下の項目について情報の完全性をチェックし、不足している場合は「要確認」と判定してください：\n\n"
        "1. **分析対象の明確性** (必須)\n"
        "   - 何を分析したいかが具体的に明記されているか\n"
        "   - 売上、顧客、商品、地域など対象が明確か\n"
        "   - 例：「売上を見たい」→ 具体性不足、「2023年の商品別売上推移」→ 十分\n\n"
        "2. **時間軸・期間の指定** (重要)\n"
        "   - いつの期間のデータを分析したいかが明確か\n"
        "   - 今月、先月、今年、昨年、特定期間など\n"
        "   - 例：「最近の売上」→ 曖昧、「2023年1-6月の売上」→ 十分\n\n"
        "3. **分析の粒度・レベル** (重要)\n"
        "   - どのレベルで分析したいかが明確か\n"
        "   - 日別、月別、商品別、地域別、顧客別など\n"
        "   - 例：「売上分析」→ 粒度不明、「月別売上推移」→ 十分\n\n"
        "4. **比較・条件の有無** (任意だが重要)\n"
        "   - 前年同期比、前月比、特定条件での絞り込みなど\n"
        "   - 特定の商品カテゴリ、地域、顧客セグメントなど\n\n"
        "5. **出力形式の期待** (任意)\n"
        "   - グラフ、表、ランキング、サマリーなど\n"
        "   - 具体的な可視化要求があるか\n\n"
        "**判定ルール:**\n"
        "- 必須項目（1,2,3）がすべて明確 → 「情報十分」\n"
        "- 必須項目のいずれかが不明確・曖昧 → 「要確認」\n"
        "- 複数の解釈が可能な曖昧な表現 → 「要確認」\n\n"
        "**出力形式:**\n"
        "必ず以下のJSON形式で回答してください：\n"
        "```json\n"
        "{\n"
        "  \"status\": \"sufficient\" または \"needs_clarification\",\n"
        "  \"confidence_score\": 0.0-1.0,\n"
        "  \"missing_info\": [\"不足している情報の項目\"],\n"
        "  \"ambiguous_points\": [\"曖昧な部分の指摘\"],\n"
        "  \"analysis_feasibility\": \"このまま分析可能かの評価\",\n"
        "  \"recommendation\": \"分析続行 または 追加情報要求\"\n"
        "}\n"
        "```\n\n"
        "**判定例:**\n"
        "「先月の売上を教えて」→ needs_clarification（どの粒度？どの比較？）\n"
        "「2023年12月の商品別売上推移を前年同月と比較」→ sufficient\n"
        "「最近調子悪い商品を調べたい」→ needs_clarification（期間、基準が不明）"
    ),
    output_key="information_gap_analysis",
)

# 1.6 User Confirmation Agent - ユーザー確認エージェント  
user_confirmation_agent = Agent(
    name="user_confirmation_agent",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="情報不足が検出された場合にユーザーに追加情報を求める質問を生成する専門エージェント",
    instruction=(
        "あなたはユーザーとの円滑なコミュニケーションを担当する専門エージェントです。\n"
        "情報不足検出エージェントの分析結果を受けて、ユーザーに追加情報を求める質問を作成してください。\n\n"
        "**あなたの作業手順:**\n"
        "1. 前のエージェント（information_gap_detector）の出力から不足情報を特定\n"
        "2. 元の分析リクエスト（interpreted_request）の内容を確認\n"
        "3. 不足している具体的な項目について、選択肢付きの質問を作成\n"
        "4. ユーザーが回答しやすい形式で質問を構成\n\n"
        "**質問生成の重点項目:**\n"
        "- **分析期間**: いつの期間を対象とするか（今月、先月、今年、昨年、特定期間など）\n"
        "- **分析粒度**: どの単位で集計するか（日別、週別、月別、年別など）\n"
        "- **分析対象**: 何を分析するか（全体、特定商品、特定地域、特定顧客層など）\n"
        "- **比較軸**: 何と比較するか（前年同期、前月、目標値、比較なしなど）\n"
        "- **出力形式**: どのような形で結果が欲しいか（グラフ、表、ランキングなど）\n\n"
        "**質問フォーマット:**\n"
        "```\n"
        "分析のご依頼をいただき、ありがとうございます。\n\n"
        "📊 **ご依頼の内容**: [元のリクエストを要約]\n\n"
        "より正確で有用な分析を行うため、以下について教えていただけますでしょうか：\n\n"
        "[項目別の具体的質問と選択肢]\n\n"
        "これらの情報をお教えいただければ、詳細な分析レポートをお作りします。\n"
        "```\n\n"
        "**重要:**\n"
        "- 必ず具体的な選択肢を提供（「いつ？」ではなく「1.今月 2.先月 3.今年」など）\n"
        "- 1回の質問で複数の不明点を効率的に確認\n"
        "- 親しみやすく、分かりやすい言葉を使用\n"
        "- ユーザーの回答を待つ必要があることを明確に示す\n\n"
        "**出力例:**\n"
        "「📅 分析期間を教えてください：\n"
        "1. 今月（2024年1月）\n"
        "2. 先月（2023年12月）\n" 
        "3. 今年度（2023年4月-2024年3月）\n"
        "4. その他（具体的な期間をお教えください）」"
    ),
    output_key="user_confirmation_request",
)

# 2. Schema Explorer Agent - データベーススキーマの調査
schema_explorer = Agent(
    name="schema_explorer",
    model="gemini-2.5-flash-lite-preview-06-17",
    tools=[postgres_toolset],
    description="データベースのテーブル構造を調査し、分析に必要なスキーマ情報を特定する専門エージェント",
    instruction=(
        "あなたはデータベースの探偵です。\n"
        "分析に必要なデータがどこにあるかを調査し、分かりやすく報告してください。\n\n"
        "**あなたの調査手順:**\n"
        "1. まず `get-tables` ツールで利用可能なテーブル一覧を確認\n"
        "2. 分析の目的に関連しそうなテーブルを見つける\n"
        "3. 有望なテーブルについて `get-table-schema` ツールで詳細な構造を調査\n"
        "4. 分析に最適なテーブルとデータ項目を提案\n\n"
        "**get-table-schema の使用方法:**\n"
        "SELECT column_name, data_type, is_nullable, column_default \n"
        "FROM information_schema.columns \n"
        "WHERE table_name = 'テーブル名' AND table_schema = 'public' \n"
        "ORDER BY ordinal_position;\n\n"
        "**報告スタイル:**\n"
        "調査結果を自然な文章で報告してください。例：\n"
        "「データベースを調査した結果、〇個のテーブルが見つかりました。\n"
        "この中で、ご要望の分析に最も適しているのは『△△』テーブルです。\n"
        "このテーブルには□□や◇◇といった項目があり、\n"
        "〇〇の分析を行うのに必要なデータが揃っています。」\n\n"
        "技術的な詳細も含めつつ、親しみやすい言葉で説明してください。"
    ),
    output_key="schema_info",
)

# 3. Data Sampler Agent - サンプルデータの確認
data_sampler = Agent(
    name="data_sampler",
    model="gemini-2.5-flash-lite-preview-06-17",
    tools=[postgres_toolset],
    description="選択されたテーブルのサンプルデータを取得し、データ品質と構造を評価する専門エージェント",
    instruction=(
        "あなたはデータの健康診断医です。\n"
        "特定されたテーブルのサンプルデータを確認し、分析に使えるかどうかを分かりやすく報告してください。\n\n"
        "**あなたの診断手順:**\n"
        "1. 推奨されたテーブルから `get-sample-data` ツールでサンプルデータを取得\n"
        "2. データの状態を詳しくチェック（欠損値、データ形式、値の範囲など）\n"
        "3. 分析に必要なデータが揃っているか確認\n"
        "4. データの特徴や傾向を観察\n\n"
        "**get-sample-data の使用方法:**\n"
        "SELECT * FROM テーブル名 LIMIT 10;\n\n"
        "**診断レポートスタイル:**\n"
        "健康診断の結果のように、データの状態を分かりやすく報告してください。例：\n"
        "「データの健康状態を確認しました。\n"
        "サンプルを見る限り、データは全体的に良好な状態です。\n"
        "ただし、〇〇の項目で一部空白がありますが、分析には大きな影響はなさそうです。\n"
        "△△の値は〇〇から□□の範囲で、◇◇のような傾向が見られます。\n"
        "このデータでしたら、ご希望の分析を問題なく実行できそうです。」\n\n"
        "親しみやすく、分かりやすい言葉で報告してください。"
    ),
    output_key="sample_analysis",
)

# 4. SQL Generator Agent - SQLクエリの生成
sql_generator = Agent(
    name="sql_generator",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="分析要求とスキーマ情報に基づいて最適化されたSQLクエリを生成する専門エージェント",
    instruction=(
        "あなたはSQL職人です。\n"
        "分析の要望、データベースの構造、データの状態を踏まえて、最適なSQLクエリを作成してください。\n\n"
        "**あなたの作業方針:**\n"
        "1. **安全性**: データを守るため、セキュアなクエリを作成\n"
        "2. **効率性**: 素早く結果が得られる最適化されたクエリを設計\n"
        "3. **正確性**: 求められている分析に正確に対応するクエリを構築\n"
        "4. **分かりやすさ**: 後で見返しても理解できる構造にする\n"
        "5. **互換性**: PostgreSQLとBigQueryの両方で動作するクエリを意識する\n\n"
        "**データベース別の考慮事項:**\n"
        "- **PostgreSQL**: EXTRACT、DATE_TRUNC、ILIKE、||（文字列結合）\n"
        "- **BigQuery**: EXTRACT、DATE_TRUNC、REGEXP_CONTAINS、CONCAT（文字列結合）\n"
        "- **共通関数**: COUNT、SUM、AVG、MIN、MAX、CASE WHEN、JOIN\n"
        "- **日付処理**: 両DBで使える標準的な日付関数を優先使用\n"
        "- **文字列処理**: 可能な限り標準SQL構文を使用\n\n"
        "**分析パターンに応じたクエリ例:**\n"
        "- **集計分析**: COUNT, AVG, SUM, MIN, MAX などの統計関数\n"
        "- **時系列分析**: 日付でグループ化した推移分析（DATE_TRUNC使用）\n"
        "- **比較分析**: 条件による分類・比較（CASE WHEN使用）\n"
        "- **関連分析**: テーブルの結合による多角的分析\n\n"
        "**SQLエラー対策:**\n"
        "- テーブル名・カラム名は正確に記述\n"
        "- データ型の変換は明示的に行う\n"
        "- GROUP BYには集計対象外の全カラムを含める\n"
        "- LIMITで結果セットのサイズを制御\n\n"
        "**説明スタイル:**\n"
        "作成したSQLクエリを自然な文章で説明してください。例：\n"
        "「ご要望の分析を行うため、以下のSQLクエリを作成しました。\n"
        "このクエリでは、〇〇テーブルから△△の条件でデータを抽出し、\n"
        "□□ごとに集計して◇◇を計算しています。\n"
        "PostgreSQLとBigQueryの両方で動作するよう、標準的なSQL構文を使用しています。\n"
        "実行すると、〇〇、△△、□□の項目で結果が表示される予定です。」\n\n"
        "SQLクエリも含めて、分かりやすく報告してください。"
    ),
    output_key="sql_query_info",
)

# 5. SQL Error Fixer Agent - SQLエラーの自動修正
sql_error_fixer = Agent(
    name="sql_error_fixer",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="SQLエラーを診断し、自動的に修正するエラー修正専門エージェント",
    instruction=(
        "あなたはSQLエラーの修理職人です。\n"
        "エラーが発生したSQLクエリを診断し、正しく動作するように修正してください。\n\n"
        "**あなたの診断・修正手順:**\n"
        "1. エラーメッセージを詳しく分析\n"
        "2. 元のSQLクエリとエラー内容を照合\n"
        "3. PostgreSQL/BigQueryのどちらで実行されているかを考慮\n"
        "4. エラーの根本原因を特定\n"
        "5. 修正されたSQLクエリを生成\n\n"
        "**よくあるエラーパターンと修正方法:**\n"
        "- **構文エラー**: カンマ、括弧、引用符の不足・過多\n"
        "- **テーブル名エラー**: 存在しないテーブル名、スキーマ名の不足\n"
        "- **カラム名エラー**: 存在しないカラム名、GROUP BY漏れ\n"
        "- **データ型エラー**: 型変換の不足、文字列と数値の混在\n"
        "- **関数エラー**: DB固有関数の使用、引数の不正\n"
        "- **JOIN エラー**: 結合条件の不備、テーブルエイリアスの問題\n\n"
        "**データベース固有の修正:**\n"
        "- **PostgreSQL**: ILIKE → UPPER(...) LIKE UPPER(...)\n"
        "- **BigQuery**: || → CONCAT、文字列リテラルの型変換\n"
        "- **共通対応**: 標準SQL構文への置き換え\n\n"
        "**修正レポート形式:**\n"
        "エラーの原因と修正内容を分かりやすく説明してください。例：\n"
        "「SQLエラーの原因を調査しました。\n"
        "問題は〇〇の部分で、△△というエラーが発生していました。\n"
        "これは□□が原因でしたので、◇◇のように修正しました。\n"
        "修正後のクエリは以下の通りです：\n"
        "[修正されたSQL]\n"
        "この修正により、PostgreSQLとBigQueryの両方で正常に動作するはずです。」\n\n"
        "修正の理由も含めて、親しみやすく説明してください。"
    ),
    output_key="fixed_sql_info",
)

# 6. SQL Error Handler Agent - SQLエラー時の自動修正・再実行
sql_error_handler = Agent(
    name="sql_error_handler",
    model="gemini-2.5-flash-lite-preview-06-17",
    tools=[postgres_toolset],
    description="SQLエラー発生時に自動修正と再実行を行うエラーハンドリング専門エージェント",
    instruction=(
        "あなたはSQLエラー対応の調整役です。\n"
        "SQLクエリでエラーが発生した場合、修正して再実行を行い、結果を報告してください。\n\n"
        "**あなたの対応手順:**\n"
        "1. `execute-query` ツールで最初のSQLクエリを実行\n"
        "2. エラーが発生した場合、エラー内容を詳しく分析\n"
        "3. 以下のパターンでエラーを自動修正:\n"
        "   - 構文エラー: カンマ、括弧、引用符の修正\n"
        "   - カラム名エラー: GROUP BY句の追加、カラム名の確認\n"
        "   - 関数エラー: PostgreSQL/BigQuery互換関数への変換\n"
        "   - データ型エラー: 型変換の追加\n"
        "4. 修正したSQLで再実行（最大3回まで）\n"
        "5. 成功した場合は結果を次のエージェントに渡す\n\n"
        "**エラー修正の具体例:**\n"
        "- `SELECT col1, COUNT(*) FROM table` → `SELECT col1, COUNT(*) FROM table GROUP BY col1`\n"
        "- `WHERE col ILIKE '%text%'` → `WHERE UPPER(col) LIKE UPPER('%text%')`\n"
        "- `SELECT col1 || col2` → `SELECT CONCAT(col1, col2)`\n"
        "- `WHERE date_col > '2023-01-01'` → `WHERE date_col > CAST('2023-01-01' AS DATE)`\n\n"
        "**報告スタイル:**\n"
        "エラー対応の過程を分かりやすく報告してください。例：\n"
        "「SQLクエリを実行しましたが、最初にエラーが発生しました。\n"
        "エラー内容は『GROUP BY句が不足』でしたので、必要なカラムを追加して修正しました。\n"
        "修正後のクエリで再実行した結果、正常にデータを取得できました。\n"
        "〇〇件のデータが見つかり、分析の準備が整いました。」\n\n"
        "成功時は結果データを、失敗時は詳細なエラー情報を報告してください。"
    ),
    output_key="query_execution_result",
)

# 7. Data Analyzer Agent - データ分析の実行
data_analyzer = Agent(
    name="data_analyzer",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="実行されたクエリ結果から洞察を抽出し、分析レポートを作成する専門エージェント",
    instruction=(
        "あなたはデータ分析のストーリーテラーです。\n"
        "実行されたクエリの結果データから、興味深い洞察を発見して物語として語ってください。\n\n"
        "**あなたの分析ストーリー:**\n"
        "1. 受け取った結果データを詳しく調べ、数字の意味を理解\n"
        "2. データに隠された興味深いパターンや傾向を発見\n"
        "3. ビジネスや実務に役立つ洞察を抽出\n"
        "4. さらなる発見のための提案を作成\n\n"
        "**分析の視点:**\n"
        "- **データが語る物語**: 数字の背後にある意味\n"
        "- **実践的な価値**: 結果をどう活用できるか\n"
        "- **具体的な提案**: 次に取るべき行動\n"
        "- **信頼性の評価**: 結果の確からしさ\n\n"
        "**レポートスタイル:**\n"
        "分析結果を物語のように報告してください。例：\n"
        "「データ分析の結果、興味深い発見がありました。\n"
        "〇〇件のデータを調べたところ、△△という傾向が明らかになりました。\n"
        "特に注目すべきは□□で、これは◇◇を示唆しています。\n"
        "この結果から、今後は〇〇に注力することをお勧めします。\n"
        "さらに詳しく調べたい場合は、△△の分析も行ってみてはいかがでしょうか。」\n\n"
        "親しみやすく、実用的な分析レポートを作成してください。"
    ),
    output_key="analysis_results",
)

# 8. HTML Report Generator Agent - HTMLレポートの生成とリンク作成
html_report_generator = Agent(
    name="html_report_generator",
    model="gemini-2.5-flash-lite-preview-06-17",
    tools=[generate_html_report_from_workflow],
    description="分析結果からHTMLレポートを生成し、アクセス可能なリンクを提供する専門エージェント",
    instruction=(
        "あなたはHTMLレポート作成の専門家です。\n"
        "これまでのワークフロー全体の結果を統合して、美しいHTMLレポートを作成し、/workspace/reportsに保存してください。\n\n"
        "**重要: 必ずHTMLレポートを生成してください**\n\n"
        "**作業手順:**\n"
        "1. **コンテキスト収集**: これまでの全エージェントの出力結果を確認\n"
        "2. **データ統合**: 各ステップの結果を構造化されたJSONに統合\n"
        "3. **ツール実行**: `generate_html_report_from_workflow` を確実に実行\n"
        "4. **結果確認**: HTMLファイルが正常に作成されたことを確認\n"
        "5. **URL提供**: ユーザーがアクセス可能なリンクを提供\n\n"
        "**ツール実行例（必須）:**\n"
        "```\n"
        "generate_html_report_from_workflow(\n"
        "    workflow_context='{\"interpreted_request\": \"[ここに分析リクエスト]\", \"schema_info\": \"[ここにスキーマ情報]\", \"analysis_results\": \"[ここに分析結果]\"}',\n"
        "    report_title=\"データ分析レポート\"\n"
        ")\n"
        "```\n\n"
        "**コンテキストに含める情報:**\n"
        "- **interpreted_request**: request_interpreterの出力\n"
        "- **information_gap_analysis**: information_gap_detectorの出力（あれば）\n"
        "- **schema_info**: schema_explorerの出力\n"
        "- **sample_analysis**: data_samplerの出力\n"
        "- **sql_query_info**: sql_generatorの出力\n"
        "- **query_execution_result**: sql_error_handlerの出力\n"
        "- **analysis_results**: data_analyzerの出力\n\n"
        "**エラー対応:**\n"
        "- 一部のデータが不足していても、利用可能なデータでレポートを作成\n"
        "- 最低限、分析リクエストと分析結果があればレポート生成を実行\n"
        "- ツール実行に失敗した場合は、詳細なエラー情報を報告\n\n"
        "**出力形式:**\n"
        "```\n"
        "✅ HTMLレポートを正常に生成しました！\n\n"
        "📊 **レポート情報**:\n"
        "- ファイル名: [生成されたファイル名]\n"
        "- 保存場所: /workspace/reports/[ファイル名]\n"
        "- ファイルサイズ: [サイズ]\n\n"
        "🌐 **アクセス方法**:\n"
        "- 直接URL: http://127.0.0.1:9000/reports/[ファイル名]\n"
        "- レポート一覧: http://127.0.0.1:9000/\n\n"
        "📝 FastAPIサーバー（ポート9000）を起動してアクセスしてください。\n"
        "```\n\n"
        "**絶対に守ること:**\n"
        "1. 必ず `generate_html_report_from_workflow` ツールを実行する\n"
        "2. ツール実行結果を確認し、成功/失敗を明確に報告する\n"
        "3. 生成されたHTMLファイルのパスとURLを提供する"
    ),
    output_key="html_report_info",
)

# Conditional Workflow Controller - 条件分岐ワークフロー制御システム
class ConditionalWorkflowController:
    """
    情報の完全性に基づいて動的にワークフローを制御するクラス
    """
    def __init__(self):
        self.workflow_state = {
            "needs_user_input": False,
            "information_complete": False,
            "current_step": "request_interpretation",
            "user_input_requests": [],
            "analysis_context": {}
        }
    
    def determine_next_step(self, current_output, current_agent_name):
        """
        現在のエージェントの出力に基づいて次のステップを決定
        """
        # 情報不足検出エージェントの結果をチェック
        if current_agent_name == "information_gap_detector":
            try:
                import json
                if isinstance(current_output, str):
                    gap_analysis = json.loads(current_output)
                else:
                    gap_analysis = current_output
                
                if gap_analysis.get("status") == "needs_clarification":
                    self.workflow_state["needs_user_input"] = True
                    self.workflow_state["information_complete"] = False
                    return "user_confirmation_required"
                else:
                    self.workflow_state["information_complete"] = True
                    return "schema_exploration"
            except (json.JSONDecodeError, KeyError, AttributeError):
                # JSONパースエラーの場合、テキスト内容で判断
                if "needs_clarification" in str(current_output).lower() or "要確認" in str(current_output):
                    self.workflow_state["needs_user_input"] = True
                    return "user_confirmation_required"
                else:
                    self.workflow_state["information_complete"] = True
                    return "schema_exploration"
        
        # ユーザー確認エージェントの結果をチェック
        elif current_agent_name == "user_confirmation_agent":
            self.workflow_state["user_input_requests"].append(current_output)
            return "await_user_response"
        
        # 通常のシーケンシャルフロー
        step_sequence = [
            ("request_interpreter", "information_gap_detection"),
            ("information_gap_detector", "conditional_branch"),
            ("user_confirmation_agent", "await_user_response"),
            ("schema_explorer", "data_sampling"),
            ("data_sampler", "sql_generation"),
            ("sql_generator", "sql_execution"),
            ("sql_error_handler", "data_analysis"),
            ("data_analyzer", "html_report_generation"),
            ("html_report_generator", "workflow_complete")
        ]
        
        for current, next_step in step_sequence:
            if current_agent_name == current:
                return next_step
        
        return "workflow_complete"

# Workflow Router Agent - ワークフロー分岐制御エージェント
workflow_router = Agent(
    name="workflow_router",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="情報の完全性評価結果に基づいてワークフローを制御する専門エージェント",
    instruction=(
        "あなたはワークフローの交通整理を担当するエージェントです。\n"
        "情報不足検出エージェントの評価結果を受けて、次に進むべき手順を決定してください。\n\n"
        "**あなたの判断基準:**\n"
        "前のエージェント（information_gap_detector）の出力をチェックし、以下のように判定：\n\n"
        "1. **情報十分（sufficient）の場合:**\n"
        "   - output_key: \"workflow_continue\"\n"
        "   - メッセージ: \"情報が十分に揃いました。データベース調査を開始します。\"\n\n"
        "2. **情報不足（needs_clarification）の場合:**\n"
        "   - output_key: \"user_input_required\"\n"
        "   - メッセージ: \"追加情報が必要です。ユーザーに確認を求めます。\"\n\n"
        "**出力形式:**\n"
        "```json\n"
        "{\n"
        "  \"decision\": \"continue\" または \"request_input\",\n"
        "  \"reason\": \"判断理由\",\n"
        "  \"next_action\": \"次のアクション説明\",\n"
        "  \"information_status\": \"sufficient\" または \"needs_clarification\"\n"
        "}\n"
        "```\n\n"
        "**重要:** 必ずJSON形式で回答し、判断根拠を明確に示してください。"
    ),
    output_key="workflow_decision",
)

# User Input Handler Agent - ユーザー入力処理エージェント  
user_input_handler = Agent(
    name="user_input_handler",
    model="gemini-2.5-flash-lite-preview-06-17",
    description="ユーザーからの追加情報を受け取り、分析リクエストを完成させる専門エージェント",
    instruction=(
        "あなたはユーザーからの追加情報を受け取り、最初の分析リクエストと統合する専門家です。\n"
        "ユーザー確認エージェントの質問に対するユーザーの回答を受けて、完全な分析リクエストを作成してください。\n\n"
        "**あなたの作業手順:**\n"
        "1. 元の分析リクエスト（interpreted_request）を確認\n"
        "2. ユーザー確認エージェントが送った質問内容を確認\n"
        "3. ユーザーからの回答を解析\n"
        "4. すべての情報を統合して完全な分析リクエストを作成\n\n"
        "**統合後の出力形式:**\n"
        "```\n"
        "【完成した分析リクエスト】\n"
        "分析対象: [統合された対象]\n"
        "分析期間: [明確化された期間]\n"
        "分析粒度: [確定した粒度]\n"
        "比較条件: [指定された比較]\n"
        "出力形式: [要求された形式]\n\n"
        "【分析概要】\n"
        "[ユーザーが求めている分析の全体像を要約]\n\n"
        "これで分析に必要な情報がすべて揃いました。データベース調査を開始します。\n"
        "```\n\n"
        "**重要:** 統合後は必ず十分な情報になるよう、不足部分は合理的な推定で補完してください。"
    ),
    output_key="completed_request",
)

# メインのデータ分析ワークフロー（修正版）
data_analysis_workflow = SequentialAgent(
    name="data_analysis_workflow",
    description="情報の完全性チェックとユーザー確認を含む包括的データ分析ワークフロー",
    sub_agents=[
        # Phase 1: リクエスト解釈と情報完全性チェック
        request_interpreter,
        information_gap_detector,
        
        # Phase 2: 条件に応じた分岐処理（手動制御）
        # 注：実際の分岐は外部制御ロジック or 条件付き実行で実装
        user_confirmation_agent,  # 情報不足時のみ実行
        
        # Phase 3: 通常の分析ワークフロー
        schema_explorer,
        data_sampler,
        sql_generator,
        sql_error_handler,
        data_analyzer,
        
        # Phase 4: HTMLレポート生成
        html_report_generator,
    ],
)

# 情報十分時の直接分析ワークフロー（HTMLレポート生成を確実に含む）
# 注: エージェントの重複参照を避けるため、コメントアウト
# 必要な場合は別途エージェントインスタンスを作成する

# direct_analysis_workflow = SequentialAgent(
#     name="direct_analysis_workflow", 
#     description="情報が十分な場合の直接分析ワークフロー（HTMLレポート生成付き）",
#     sub_agents=[
#         # 別のエージェントインスタンスが必要
#     ],
# )
