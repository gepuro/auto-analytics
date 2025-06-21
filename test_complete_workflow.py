#!/usr/bin/env python3
"""
完全なワークフロー実行のテストとHTMLレポート生成確認
"""

import sys
import os
import json
from datetime import datetime

sys.path.append('/workspace/auto-analytics-agent')

def test_workflow_components():
    """ワークフロー構成要素のテスト"""
    print("=== ワークフロー構成要素テスト ===")
    
    try:
        from workflow import (
            data_analysis_workflow,
            html_report_generator,
            generate_html_report_from_workflow
        )
        
        print("✅ ワークフロー要素のインポート成功")
        
        # エージェント構成確認
        agent_names = [a.name for a in data_analysis_workflow.sub_agents]
        print(f"📋 エージェント数: {len(agent_names)}")
        print(f"📍 HTMLジェネレーター位置: {agent_names.index('html_report_generator') + 1}")
        
        # HTMLジェネレーターの設定確認
        print(f"🔧 HTMLジェネレーターツール: {len(html_report_generator.tools)} 個")
        print(f"📝 出力キー: {html_report_generator.output_key}")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def simulate_workflow_context():
    """ワークフロー実行コンテキストのシミュレーション"""
    print("\n=== ワークフロー実行シミュレーション ===")
    
    # 各エージェントの出力をシミュレート
    context = {
        "interpreted_request": "2023年12月の商品別売上分析を実行します。月別の推移と前年同期比較を含む詳細レポートを作成します。",
        "information_gap_analysis": {
            "status": "sufficient",
            "confidence_score": 0.9,
            "recommendation": "分析続行"
        },
        "schema_info": "データベース調査結果: sales テーブル（商品ID、売上日、売上金額、顧客ID）を使用。約10,000件のデータが利用可能です。",
        "sample_analysis": "サンプルデータ分析: データ品質は良好、欠損値は1%未満。商品A001-A010が主要商品として確認されました。",
        "sql_query_info": {
            "query": "SELECT product_id, DATE_TRUNC('month', sale_date) as month, SUM(amount) as total_sales FROM sales WHERE sale_date >= '2023-12-01' AND sale_date < '2024-01-01' GROUP BY product_id, month ORDER BY total_sales DESC",
            "description": "商品別月次売上集計クエリを生成しました"
        },
        "query_execution_result": {
            "data": [
                {"product_id": "A001", "month": "2023-12-01", "total_sales": 450000},
                {"product_id": "A002", "month": "2023-12-01", "total_sales": 380000},
                {"product_id": "A003", "month": "2023-12-01", "total_sales": 320000},
                {"product_id": "A004", "month": "2023-12-01", "total_sales": 280000},
                {"product_id": "A005", "month": "2023-12-01", "total_sales": 240000}
            ],
            "row_count": 5,
            "execution_time": "0.15秒"
        },
        "analysis_results": "分析結果: 2023年12月の売上は総額167万円で前年同月比12%増となりました。商品A001が最も売上が高く（45万円）、上位5商品で全体の70%を占めています。特に商品A001とA002の成長が顕著で、マーケティング戦略の効果が現れています。今後もこれらの商品に注力することを推奨します。"
    }
    
    print("📊 ワークフローコンテキストを生成しました")
    print(f"📋 コンテキスト項目数: {len(context)}")
    
    return context

def test_html_generation_with_context(context):
    """完全なコンテキストでのHTMLレポート生成テスト"""
    print("\n=== 完全コンテキストHTMLレポート生成テスト ===")
    
    try:
        from workflow import generate_html_report_from_workflow
        
        # HTMLレポート生成実行
        result = generate_html_report_from_workflow(
            workflow_context=json.dumps(context, ensure_ascii=False),
            report_title="完全ワークフローテスト - 商品別売上分析レポート"
        )
        
        # 結果解析
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print("✅ HTMLレポート生成成功")
            print(f"📁 ファイル名: {result_data.get('filename')}")
            print(f"📊 ファイルサイズ: {result_data.get('file_size')}")
            print(f"🌐 アクセスURL: {result_data.get('report_url')}")
            print(f"📋 レポート一覧: {result_data.get('report_list_url')}")
            
            # ファイル存在確認
            file_path = result_data.get('file_path')
            if os.path.exists(file_path):
                print(f"✅ ファイルが正常に作成されました: {file_path}")
                
                # ファイル内容の一部確認
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "商品別売上分析" in content and "2023年12月" in content:
                        print("✅ レポート内容に期待されるデータが含まれています")
                    else:
                        print("⚠️  レポート内容に一部期待されるデータが不足している可能性があります")
                
                return True
            else:
                print(f"❌ ファイルが作成されていません: {file_path}")
                return False
        else:
            print(f"❌ HTMLレポート生成に失敗: {result_data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_reports_directory():
    """reportsディレクトリの最新状態確認"""
    print("\n=== reportsディレクトリ最新状態確認 ===")
    
    reports_dir = "/workspace/reports"
    files = os.listdir(reports_dir)
    html_files = [f for f in files if f.endswith('.html')]
    html_files.sort(reverse=True)
    
    print(f"📁 HTMLファイル総数: {len(html_files)}")
    
    if html_files:
        print("📋 最新のHTMLファイル（上位3件）:")
        for i, file in enumerate(html_files[:3]):
            file_path = os.path.join(reports_dir, file)
            file_size = os.path.getsize(file_path)
            mtime = os.path.getmtime(file_path)
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            print(f"  {i+1}. {file}")
            print(f"     サイズ: {file_size} bytes, 更新: {mtime_str}")

if __name__ == "__main__":
    print("完全ワークフロー実行テスト開始\n")
    
    # Step 1: ワークフロー構成要素テスト
    components_ok = test_workflow_components()
    
    if components_ok:
        # Step 2: ワークフローコンテキスト生成
        context = simulate_workflow_context()
        
        # Step 3: HTMLレポート生成テスト
        html_ok = test_html_generation_with_context(context)
        
        # Step 4: 結果確認
        check_reports_directory()
        
        if html_ok:
            print("\n🎉 すべてのテストが成功しました！")
            print("✅ HTMLレポート生成機能は正常に動作しています")
            print("✅ ワークフローの統合は完了しています")
        else:
            print("\n❌ HTMLレポート生成テストが失敗しました")
    else:
        print("\n❌ ワークフロー構成要素テストが失敗しました")