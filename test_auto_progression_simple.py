#!/usr/bin/env python3
"""
自動進行機能の簡易テストスクリプト
ADK依存を除いた単体テスト
"""

import sys
import os
import json
from datetime import datetime

# パスを追加
sys.path.append('/workspace/auto-analytics-agent')

# ワークフロー制御モジュールをインポート
from workflow_controller import workflow_controller, check_information_completeness_v2
from workflow_resumption import workflow_resumption_handler


def print_test_header(test_name: str):
    """テストヘッダーを表示"""
    print("\n" + "="*60)
    print(f"🧪 テスト: {test_name}")
    print("="*60)


def test_auto_progression_logic():
    """自動進行ロジックのテスト"""
    print_test_header("自動進行判定ロジック")
    
    # テストケース1: 情報が十分（JSON形式）
    print("\n✅ ケース1: 情報十分（高信頼度）")
    sufficient_json = '''
    {
        "status": "sufficient",
        "confidence_score": 0.9,
        "missing_info": [],
        "ambiguous_points": [],
        "analysis_feasibility": "分析可能",
        "recommendation": "分析続行"
    }
    '''
    
    is_sufficient, result = check_information_completeness_v2(sufficient_json)
    print(f"判定: {'自動進行可能' if is_sufficient else '確認が必要'}")
    print(f"アクション: {result['action']}")
    print(f"信頼度: {result.get('confidence', 'N/A')}")
    print(f"メッセージ: {result['message']}")
    
    # テストケース2: 情報不足（JSON形式）
    print("\n❌ ケース2: 情報不足（低信頼度）")
    insufficient_json = '''
    {
        "status": "needs_clarification",
        "confidence_score": 0.3,
        "missing_info": ["分析期間", "集計単位"],
        "ambiguous_points": ["売上の定義"],
        "analysis_feasibility": "追加情報が必要",
        "recommendation": "追加情報要求"
    }
    '''
    
    is_sufficient, result = check_information_completeness_v2(insufficient_json)
    print(f"判定: {'自動進行可能' if is_sufficient else '確認が必要'}")
    print(f"アクション: {result['action']}")
    print(f"不足情報: {result.get('missing_info', [])}")
    print(f"メッセージ: {result['message']}")
    
    # テストケース3: 境界値（信頼度0.7）
    print("\n⚡ ケース3: 境界値テスト（信頼度0.7）")
    borderline_json = '''
    {
        "status": "sufficient",
        "confidence_score": 0.7,
        "missing_info": [],
        "analysis_feasibility": "分析可能"
    }
    '''
    
    is_sufficient, result = check_information_completeness_v2(borderline_json)
    print(f"判定: {'自動進行可能' if is_sufficient else '確認が必要'}")
    print(f"アクション: {result['action']}")
    print(f"信頼度: {result.get('confidence', 'N/A')}")
    
    # テストケース4: テキスト形式
    print("\n📝 ケース4: テキスト形式での判定")
    text_sufficient = "分析に必要な情報は十分に揃っています。問題なく分析を実行できます。"
    
    is_sufficient, result = check_information_completeness_v2(text_sufficient)
    print(f"判定: {'自動進行可能' if is_sufficient else '確認が必要'}")
    print(f"アクション: {result['action']}")
    
    text_insufficient = "分析期間が曖昧で、集計単位も不明確です。要確認。"
    
    is_sufficient, result = check_information_completeness_v2(text_insufficient)
    print(f"判定: {'自動進行可能' if is_sufficient else '確認が必要'}")
    print(f"アクション: {result['action']}")


def test_workflow_resumption():
    """ワークフロー自動再開のテスト"""
    print_test_header("ワークフロー自動再開機能")
    
    # ステップ1: 初期状態の確認
    print("\n📊 初期状態")
    status = workflow_resumption_handler.get_resumption_status()
    print(f"元リクエスト: {status['has_original_request']}")
    print(f"ユーザー回答: {status['has_user_response']}")
    print(f"再開済み: {status['workflow_resumed']}")
    
    # ステップ2: 再開準備
    print("\n📝 ステップ1: 再開準備")
    original_request = "売上データを分析してください"
    questions = """
    分析期間を教えてください：
    1. 今月（2024年1月）
    2. 先月（2023年12月）
    3. 今年度（2023年4月-2024年3月）
    """
    
    prep_result = workflow_resumption_handler.prepare_for_resumption(
        original_request, questions
    )
    print(f"状態: {prep_result['status']}")
    print(f"メッセージ: {prep_result['message']}")
    
    # ステップ3: ユーザー入力後の自動再開
    print("\n🚀 ステップ2: ユーザー入力後の自動再開")
    user_response = "今月の売上を日別で分析してください。前年同期との比較もお願いします。"
    
    resume_result = workflow_resumption_handler.resume_after_user_input(user_response)
    print(f"状態: {resume_result['status']}")
    print(f"次のアクション: {resume_result['action']}")
    print(f"自動進行: {'有効' if resume_result['auto_proceed'] else '無効'}")
    print(f"次のフェーズ: {resume_result['next_phase']}")
    
    # 完成したリクエストの確認
    print("\n📄 統合されたリクエスト（抜粋）:")
    completed = resume_result['completed_request']
    lines = completed.split('\n')[:10]  # 最初の10行のみ表示
    for line in lines:
        if line.strip():
            print(f"  {line}")
    
    # ステップ4: 再開状態の最終確認
    print("\n✅ 最終状態")
    final_status = workflow_resumption_handler.get_resumption_status()
    print(f"ワークフロー再開: {final_status['workflow_resumed']}")
    print(f"完成リクエスト: {'あり' if final_status['completed_request'] else 'なし'}")


def test_integration_scenario():
    """統合シナリオテスト"""
    print_test_header("統合シナリオ: 完全な自動進行フロー")
    
    # シナリオ1: 明確なリクエスト → 自動進行
    print("\n🎯 シナリオ1: 明確なリクエスト")
    clear_request = "2024年1月の商品別売上を月別で集計して、前年同月と比較してください"
    
    print(f"リクエスト: {clear_request}")
    
    # 情報完全性チェック（明確な情報）
    gap_analysis = '''
    {
        "status": "sufficient",
        "confidence_score": 0.95,
        "missing_info": [],
        "analysis_feasibility": "すべての必要情報が揃っています",
        "recommendation": "分析続行"
    }
    '''
    
    is_sufficient, result = check_information_completeness_v2(gap_analysis)
    print(f"\n情報完全性チェック結果:")
    print(f"  - 判定: {'✅ 自動進行' if is_sufficient else '❌ 確認必要'}")
    print(f"  - 信頼度: {result.get('confidence', 0) * 100:.0f}%")
    print(f"  - 次のステップ: {result.get('next_phase', 'N/A')}")
    
    # シナリオ2: 曖昧なリクエスト → 確認 → 自動再開
    print("\n\n🎯 シナリオ2: 曖昧なリクエスト → 自動再開")
    vague_request = "売上を見たい"
    
    print(f"リクエスト: {vague_request}")
    
    # 情報完全性チェック（曖昧な情報）
    gap_analysis_vague = '''
    {
        "status": "needs_clarification",
        "confidence_score": 0.2,
        "missing_info": ["分析期間", "集計単位", "対象範囲"],
        "ambiguous_points": ["どの売上データか不明"],
        "recommendation": "追加情報要求"
    }
    '''
    
    is_sufficient, result = check_information_completeness_v2(gap_analysis_vague)
    print(f"\n情報完全性チェック結果:")
    print(f"  - 判定: {'✅ 自動進行' if is_sufficient else '❌ 確認必要'}")
    print(f"  - 不足情報: {result.get('missing_info', [])}")
    
    # ユーザー確認と自動再開
    print(f"\n👤 ユーザーへの確認...")
    workflow_resumption_handler.reset()  # リセット
    workflow_resumption_handler.prepare_for_resumption(vague_request, "期間と対象を教えてください")
    
    user_clarification = "今月の全店舗の売上を日別で見たいです"
    resume_result = workflow_resumption_handler.resume_after_user_input(user_clarification)
    
    print(f"\n🚀 自動再開結果:")
    print(f"  - 状態: {resume_result['status']}")
    print(f"  - 自動進行: {'有効' if resume_result['auto_proceed'] else '無効'}")
    print(f"  - 次のフェーズ: {resume_result['next_phase']}")


def main():
    """メインテスト実行"""
    print("\n" + "🔥"*30)
    print("🚀 Auto Analytics 自動進行機能テスト")
    print("🔥"*30)
    
    # 各テストを実行
    test_auto_progression_logic()
    test_workflow_resumption()
    test_integration_scenario()
    
    print("\n\n" + "="*60)
    print("✅ すべてのテストが完了しました")
    print("="*60)
    
    print("\n📌 実装のポイント:")
    print("1. 情報が十分（信頼度≥0.7）の場合、自動的に分析を開始")
    print("2. 情報が不足している場合のみ、ユーザーに確認を要求")
    print("3. ユーザー回答後は自動的にワークフローを再開")
    print("4. 各フェーズで進捗状況を適切に報告")


if __name__ == "__main__":
    main()