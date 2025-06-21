#!/usr/bin/env python3
"""
HTMLレポート生成関数のテストスクリプト
"""

import sys
import json
import os
from datetime import datetime

# ワークフローモジュールの読み込み
sys.path.append('/workspace/auto-analytics-agent')

def test_html_report_generation():
    """HTMLレポート生成のテスト"""
    print("=== HTMLレポート生成テスト ===")
    
    # ワークフロー関数をインポート
    try:
        from workflow import generate_html_report_from_workflow
        print("✅ HTMLレポート生成関数のインポートが成功しました")
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False
    
    # テスト用のワークフローコンテキスト
    test_context = {
        "interpreted_request": "2023年12月の売上分析をお求めです",
        "schema_info": "sales テーブルから売上データを取得しました", 
        "sample_analysis": "サンプルデータ10件を確認、データ品質は良好です",
        "sql_query_info": "SELECT date_trunc('day', sale_date) as day, SUM(amount) as total FROM sales WHERE sale_date >= '2023-12-01' AND sale_date < '2024-01-01' GROUP BY day ORDER BY day",
        "query_execution_result": {
            "data": [
                {"day": "2023-12-01", "total": 150000},
                {"day": "2023-12-02", "total": 180000},
                {"day": "2023-12-03", "total": 120000}
            ]
        },
        "analysis_results": "12月の売上は好調で、特に2日と3日にピークが見られます。前年同月比15%増となっています。"
    }
    
    # JSONに変換
    context_json = json.dumps(test_context, ensure_ascii=False)
    
    # HTMLレポート生成を実行
    try:
        result = generate_html_report_from_workflow(
            workflow_context=context_json,
            report_title="テスト用売上分析レポート"
        )
        
        print("✅ HTMLレポート生成が成功しました")
        
        # 結果をパース
        if isinstance(result, str):
            try:
                result_data = json.loads(result)
                if result_data.get("success"):
                    print(f"📁 保存場所: {result_data.get('file_path')}")
                    print(f"📊 ファイル名: {result_data.get('filename')}")
                    print(f"🌐 アクセスURL: {result_data.get('report_url')}")
                    print(f"📏 ファイルサイズ: {result_data.get('file_size')}")
                    
                    # ファイルが実際に作成されたかチェック
                    file_path = result_data.get('file_path')
                    if file_path and os.path.exists(file_path):
                        print(f"✅ ファイルが正常に作成されました: {file_path}")
                        
                        # ファイルサイズ確認
                        file_size = os.path.getsize(file_path)
                        print(f"📊 実際のファイルサイズ: {file_size} bytes")
                        
                        return True
                    else:
                        print(f"❌ ファイルが作成されていません: {file_path}")
                        return False
                else:
                    print(f"❌ レポート生成に失敗: {result_data.get('error')}")
                    return False
            except json.JSONDecodeError:
                print("❌ レスポンスのJSONパースに失敗")
                print(f"Raw result: {result}")
                return False
        else:
            print("❌ 予期しないレスポンス形式")
            print(f"Result type: {type(result)}")
            return False
            
    except Exception as e:
        print(f"❌ HTMLレポート生成中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reports_directory():
    """reportsディレクトリの状態確認"""
    print("\n=== reportsディレクトリ確認 ===")
    
    reports_dir = "/workspace/reports"
    
    if os.path.exists(reports_dir):
        print(f"✅ reportsディレクトリが存在します: {reports_dir}")
        
        # ディレクトリ内のファイル一覧
        files = os.listdir(reports_dir)
        print(f"📁 ディレクトリ内のファイル数: {len(files)}")
        
        # HTMLファイルのみを抽出
        html_files = [f for f in files if f.endswith('.html')]
        print(f"📊 HTMLファイル数: {len(html_files)}")
        
        if html_files:
            print("📋 最新のHTMLファイル:")
            # 最新のファイルを表示
            html_files.sort(reverse=True)
            for i, file in enumerate(html_files[:3]):  # 最新3件
                file_path = os.path.join(reports_dir, file)
                file_size = os.path.getsize(file_path)
                mtime = os.path.getmtime(file_path)
                mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                print(f"  {i+1}. {file} ({file_size} bytes, {mtime_str})")
        
        return True
    else:
        print(f"❌ reportsディレクトリが存在しません: {reports_dir}")
        return False

if __name__ == "__main__":
    print("HTMLレポート生成テスト開始\n")
    
    # ディレクトリ確認
    dir_ok = test_reports_directory()
    
    # HTMLレポート生成テスト
    if dir_ok:
        report_ok = test_html_report_generation()
        
        if report_ok:
            print("\n🎉 すべてのテストが成功しました")
        else:
            print("\n❌ HTMLレポート生成テストが失敗しました")
    else:
        print("\n❌ reportsディレクトリの問題により、テストを中止しました")