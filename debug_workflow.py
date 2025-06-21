#!/usr/bin/env python3
"""
ワークフロー実行とHTMLレポート生成のデバッグスクリプト
"""

import sys
import os
import json
from datetime import datetime

sys.path.append('/workspace/auto-analytics-agent')

def debug_workflow_execution():
    """ワークフロー実行のデバッグ"""
    print("=== ワークフロー実行デバッグ ===")
    
    try:
        from workflow import (
            data_analysis_workflow,
            html_report_generator,
            generate_html_report_from_workflow
        )
        
        print("✅ ワークフロー要素のインポートが成功しました")
        print(f"📊 メインワークフロー: {data_analysis_workflow.name}")
        print(f"📄 HTMLジェネレーター: {html_report_generator.name}")
        
        # エージェントリスト確認
        agent_names = [a.name for a in data_analysis_workflow.sub_agents]
        print(f"📋 エージェント構成: {', '.join(agent_names)}")
        
        # HTMLレポートジェネレーターの位置確認
        html_gen_index = agent_names.index('html_report_generator') if 'html_report_generator' in agent_names else -1
        print(f"📍 HTMLジェネレーターの位置: {html_gen_index + 1}/{len(agent_names)}")
        
        # HTMLレポートジェネレーターの設定確認
        print(f"🔧 HTMLジェネレーターのツール: {html_report_generator.tools}")
        print(f"📝 HTMLジェネレーターの出力キー: {html_report_generator.output_key}")
        
        # HTMLレポート生成関数の動作確認
        print("\n=== HTMLレポート生成関数テスト ===")
        
        # 簡単なテストコンテキスト
        test_context = {
            "interpreted_request": "売上データの分析",
            "analysis_results": "売上が好調です"
        }
        
        result = generate_html_report_from_workflow(
            workflow_context=json.dumps(test_context),
            report_title="デバッグテストレポート"
        )
        
        print("✅ HTMLレポート生成関数が正常に動作")
        
        # 結果解析
        result_data = json.loads(result)
        if result_data.get("success"):
            print(f"📁 生成されたファイル: {result_data.get('filename')}")
            print(f"🌐 アクセスURL: {result_data.get('report_url')}")
        else:
            print(f"❌ エラー: {result_data.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ デバッグ中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_report_generation_conditions():
    """HTMLレポート生成の前提条件チェック"""
    print("\n=== HTMLレポート生成前提条件チェック ===")
    
    # 1. reportsディレクトリの存在確認
    reports_dir = "/workspace/reports"
    if os.path.exists(reports_dir) and os.path.isdir(reports_dir):
        print(f"✅ reportsディレクトリ存在: {reports_dir}")
        
        # 書き込み権限確認
        if os.access(reports_dir, os.W_OK):
            print("✅ reportsディレクトリの書き込み権限あり")
        else:
            print("❌ reportsディレクトリの書き込み権限なし")
            return False
    else:
        print(f"❌ reportsディレクトリが存在しません: {reports_dir}")
        return False
    
    # 2. 関数の存在確認
    try:
        sys.path.append('/workspace/auto-analytics-agent')
        from workflow import generate_html_report_from_workflow
        print("✅ HTMLレポート生成関数が利用可能")
    except ImportError as e:
        print(f"❌ HTMLレポート生成関数のインポートに失敗: {e}")
        return False
    
    # 3. 依存ライブラリの確認
    try:
        import json
        from pathlib import Path
        from datetime import datetime
        print("✅ 必要なライブラリが利用可能")
    except ImportError as e:
        print(f"❌ 必要なライブラリが見つかりません: {e}")
        return False
    
    return True

def test_complete_workflow_simulation():
    """完全なワークフロー実行シミュレーション"""
    print("\n=== 完全ワークフロー実行シミュレーション ===")
    
    # シミュレーション用の各ステップの結果
    workflow_results = {
        "interpreted_request": "2023年12月の商品別売上分析をお願いします",
        "information_gap_analysis": {
            "status": "sufficient",
            "confidence_score": 0.9
        },
        "schema_info": "salesテーブル（商品ID、売上日、売上金額）を使用",
        "sample_analysis": "データ品質良好、1000件のサンプルを確認",
        "sql_query_info": "SELECT product_id, SUM(amount) FROM sales WHERE sale_date >= '2023-12-01' GROUP BY product_id",
        "query_execution_result": {
            "data": [
                {"product_id": "A001", "sum": 150000},
                {"product_id": "A002", "sum": 120000},
                {"product_id": "A003", "sum": 180000}
            ]
        },
        "analysis_results": "商品A003が最も売上が高く、全体として好調な売上を記録しています。"
    }
    
    print("📊 シミュレーション用ワークフロー結果を準備")
    
    # HTMLレポート生成を実行
    try:
        from workflow import generate_html_report_from_workflow
        
        result = generate_html_report_from_workflow(
            workflow_context=json.dumps(workflow_results),
            report_title="完全ワークフローシミュレーションレポート"
        )
        
        result_data = json.loads(result)
        
        if result_data.get("success"):
            print("✅ 完全ワークフローシミュレーションでHTMLレポート生成成功")
            print(f"📁 ファイル: {result_data.get('filename')}")
            print(f"🌐 URL: {result_data.get('report_url')}")
            
            # ファイルの実際の存在確認
            file_path = result_data.get('file_path')
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"📊 ファイルサイズ: {file_size} bytes")
                return True
            else:
                print(f"❌ ファイルが作成されませんでした: {file_path}")
                return False
        else:
            print(f"❌ HTMLレポート生成に失敗: {result_data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ シミュレーション中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("ワークフロー実行とHTMLレポート生成のデバッグ開始\n")
    
    # 前提条件チェック
    conditions_ok = check_report_generation_conditions()
    
    if conditions_ok:
        # ワークフロー実行デバッグ
        workflow_ok = debug_workflow_execution()
        
        if workflow_ok:
            # 完全ワークフロー実行シミュレーション
            simulation_ok = test_complete_workflow_simulation()
            
            if simulation_ok:
                print("\n🎉 すべてのデバッグテストが成功しました")
                print("HTMLレポート生成機能は正常に動作しています")
            else:
                print("\n❌ 完全ワークフローシミュレーションが失敗しました")
        else:
            print("\n❌ ワークフロー実行デバッグが失敗しました")
    else:
        print("\n❌ 前提条件チェックが失敗しました")