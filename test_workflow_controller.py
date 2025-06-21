#!/usr/bin/env python3
"""
ワークフロー制御システムのテストスクリプト
"""

import sys
import os
sys.path.append('/workspace/auto-analytics-agent')

from workflow_controller import WorkflowController, check_information_completeness_v2

def test_information_gap_detection():
    """情報不足検出のテスト"""
    print("=== 情報不足検出テスト ===")
    
    # テストケース1: 情報十分
    sufficient_output = """
    {
        "status": "sufficient",
        "confidence_score": 0.9,
        "missing_info": [],
        "ambiguous_points": [],
        "analysis_feasibility": "分析可能",
        "recommendation": "分析続行"
    }
    """
    
    print("テストケース1: 情報十分")
    is_sufficient, result = check_information_completeness_v2(sufficient_output)
    print(f"結果: {is_sufficient}")
    print(f"詳細: {result}")
    print()
    
    # テストケース2: 情報不足
    insufficient_output = """
    {
        "status": "needs_clarification",
        "confidence_score": 0.3,
        "missing_info": ["分析期間", "集計レベル"],
        "ambiguous_points": ["売上の定義が不明"],
        "analysis_feasibility": "追加情報が必要",
        "recommendation": "追加情報要求"
    }
    """
    
    print("テストケース2: 情報不足")
    is_sufficient, result = check_information_completeness_v2(insufficient_output)
    print(f"結果: {is_sufficient}")
    print(f"詳細: {result}")
    print()
    
    # テストケース3: テキスト形式（JSON以外）
    text_output = "このリクエストは曖昧で、分析期間と対象が不明確です。要確認が必要です。"
    
    print("テストケース3: テキスト形式")
    is_sufficient, result = check_information_completeness_v2(text_output)
    print(f"結果: {is_sufficient}")
    print(f"詳細: {result}")
    print()

def test_question_generation():
    """質問生成のテスト"""
    print("=== 質問生成テスト ===")
    
    from workflow_controller import generate_user_questions
    
    original_request = "売上を分析してほしい"
    gap_analysis = """
    {
        "status": "needs_clarification",
        "missing_info": ["分析期間", "集計レベル", "分析対象"],
        "ambiguous_points": ["売上の具体的定義"]
    }
    """
    
    questions = generate_user_questions(original_request, gap_analysis)
    print("生成された質問:")
    print(questions)
    print()

def test_workflow_controller():
    """ワークフローコントローラーのテスト"""
    print("=== ワークフローコントローラーテスト ===")
    
    controller = WorkflowController()
    
    # 初期状態
    print("初期状態:")
    print(controller.get_workflow_status())
    print()
    
    # 情報不足分析のテスト
    gap_output = """
    {
        "status": "needs_clarification",
        "confidence_score": 0.4,
        "missing_info": ["期間", "粒度"],
        "ambiguous_points": ["対象不明"]
    }
    """
    
    result = controller.analyze_information_gap(gap_output)
    print("情報不足分析結果:")
    print(result)
    print()
    
    # 状態更新
    controller.update_workflow_state("user_confirmation", {"gap_analysis": result})
    print("更新後の状態:")
    print(controller.get_workflow_status())
    print()

def test_user_feedback_integration():
    """ユーザーフィードバック統合のテスト"""
    print("=== ユーザーフィードバック統合テスト ===")
    
    from workflow_controller import integrate_user_feedback
    
    original_request = "売上データを見たい"
    questions = "期間と集計レベルを教えてください"
    user_response = "先月の日別売上でお願いします"
    
    completed_request = integrate_user_feedback(original_request, questions, user_response)
    print("統合結果:")
    print(completed_request)
    print()

if __name__ == "__main__":
    print("ワークフロー制御システム テスト開始\n")
    
    try:
        test_information_gap_detection()
        test_question_generation()
        test_workflow_controller()
        test_user_feedback_integration()
        
        print("✅ すべてのテストが完了しました")
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()