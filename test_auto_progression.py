#!/usr/bin/env python3
"""
自動進行機能のテストスクリプト
情報が十分な場合と不足している場合の両方をテスト
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any

# パスを追加
sys.path.append('/workspace/auto-analytics-agent')

# モジュールをインポート
from custom_agent import AutoAnalyticsCustomAgent
from workflow_controller import workflow_controller
from workflow_resumption import workflow_resumption_handler


class MockContext:
    """テスト用のモックコンテキスト"""
    def __init__(self):
        self.session = MockSession()


class MockSession:
    """テスト用のモックセッション"""
    def __init__(self):
        self.state = {}


def print_test_header(test_name: str):
    """テストヘッダーを表示"""
    print("\n" + "="*60)
    print(f"🧪 テスト: {test_name}")
    print("="*60)


def print_result(result: Dict[str, Any]):
    """結果を整形して表示"""
    print(json.dumps(result, ensure_ascii=False, indent=2))


async def test_information_sufficient():
    """情報が十分な場合の自動進行テスト"""
    print_test_header("情報が十分な場合の自動進行")
    
    # テスト用のエージェント辞書（簡略版）
    mock_agents = {
        'request_interpreter': None,
        'information_gap_detector': None,
        'user_confirmation_agent': None,
        'schema_explorer': None,
        'data_sampler': None,
        'sql_generator': None,
        'sql_error_handler': None,
        'data_analyzer': None,
        'html_report_generator': None
    }
    
    # カスタムエージェントのインスタンス化
    agent = AutoAnalyticsCustomAgent(mock_agents)
    
    # 情報完全性の判定テスト（JSON形式）
    print("\n📋 ケース1: JSON形式で情報十分")
    gap_analysis_json = '''
    {
        "status": "sufficient",
        "confidence_score": 0.9,
        "missing_info": [],
        "ambiguous_points": [],
        "analysis_feasibility": "分析可能",
        "recommendation": "分析続行"
    }
    '''
    
    is_sufficient, confidence = agent._analyze_information_completeness(gap_analysis_json)
    print(f"判定結果: {'✅ 自動進行' if is_sufficient else '❌ 確認必要'}")
    print(f"信頼度: {confidence:.0%}")
    
    # テキスト形式のテスト
    print("\n📋 ケース2: テキスト形式で情報十分")
    gap_analysis_text = "分析に必要な情報は十分に揃っています。問題なく分析を実行できます。"
    
    is_sufficient, confidence = agent._analyze_information_completeness(gap_analysis_text)
    print(f"判定結果: {'✅ 自動進行' if is_sufficient else '❌ 確認必要'}")
    print(f"信頼度: {confidence:.0%}")


async def test_information_insufficient():
    """情報が不足している場合のテスト"""
    print_test_header("情報が不足している場合")
    
    # カスタムエージェントのインスタンス化
    mock_agents = {key: None for key in ['request_interpreter', 'information_gap_detector', 
                                         'user_confirmation_agent', 'schema_explorer',
                                         'data_sampler', 'sql_generator', 'sql_error_handler',
                                         'data_analyzer', 'html_report_generator']}
    agent = AutoAnalyticsCustomAgent(mock_agents)
    
    # 情報不足のケース（JSON）
    print("\n📋 ケース1: JSON形式で情報不足")
    gap_analysis_json = '''
    {
        "status": "needs_clarification",
        "confidence_score": 0.3,
        "missing_info": ["分析期間", "集計レベル"],
        "ambiguous_points": ["売上の定義が不明"],
        "analysis_feasibility": "追加情報が必要",
        "recommendation": "追加情報要求"
    }
    '''
    
    is_sufficient, confidence = agent._analyze_information_completeness(gap_analysis_json)
    print(f"判定結果: {'✅ 自動進行' if is_sufficient else '❌ 確認必要'}")
    print(f"信頼度: {confidence:.0%}")
    
    # テキスト形式のテスト
    print("\n📋 ケース2: テキスト形式で情報不足")
    gap_analysis_text = "分析期間が不明確で、どの粒度で集計すべきか曖昧です。要確認。"
    
    is_sufficient, confidence = agent._analyze_information_completeness(gap_analysis_text)
    print(f"判定結果: {'✅ 自動進行' if is_sufficient else '❌ 確認必要'}")
    print(f"信頼度: {confidence:.0%}")


def test_workflow_resumption():
    """ワークフロー再開ハンドラーのテスト"""
    print_test_header("ワークフロー再開ハンドラー")
    
    # 再開準備
    print("\n📋 ステップ1: 再開準備")
    original_request = "売上分析をしてください"
    user_questions = "分析期間を教えてください：1.今月 2.先月 3.今年度"
    
    prep_result = workflow_resumption_handler.prepare_for_resumption(
        original_request, user_questions
    )
    print_result(prep_result)
    
    # ユーザー入力後の再開
    print("\n📋 ステップ2: ユーザー入力後の自動再開")
    user_response = "今月の売上を日別で分析してください。前年同期と比較もお願いします。"
    
    ctx = MockContext()
    resume_result = workflow_resumption_handler.resume_after_user_input(
        user_response, ctx
    )
    print_result(resume_result)
    
    # 自動進行フラグの確認
    print(f"\n🚀 自動進行: {'有効' if resume_result.get('auto_proceed') else '無効'}")
    print(f"次のフェーズ: {resume_result.get('next_phase')}")
    
    # 統合されたリクエストの表示
    print("\n📄 統合されたリクエスト:")
    print(resume_result.get('completed_request'))


def test_workflow_controller_integration():
    """ワークフローコントローラーとの統合テスト"""
    print_test_header("ワークフローコントローラー統合")
    
    # 情報十分なケース
    print("\n📋 ケース1: 情報十分 → 自動進行")
    gap_output = '''
    {
        "status": "sufficient",
        "confidence_score": 0.85,
        "missing_info": [],
        "analysis_feasibility": "分析可能"
    }
    '''
    
    decision = workflow_controller.analyze_information_gap(gap_output)
    print_result(decision)
    print(f"アクション: {decision['action']}")
    print(f"ユーザー入力必要: {'はい' if decision['user_input_required'] else 'いいえ'}")
    
    # 情報不足のケース
    print("\n📋 ケース2: 情報不足 → 確認要求")
    gap_output_insufficient = '''
    {
        "status": "needs_clarification",
        "confidence_score": 0.4,
        "missing_info": ["期間", "粒度"],
        "ambiguous_points": ["対象範囲"]
    }
    '''
    
    decision = workflow_controller.analyze_information_gap(gap_output_insufficient)
    print_result(decision)
    print(f"アクション: {decision['action']}")
    print(f"ユーザー入力必要: {'はい' if decision['user_input_required'] else 'いいえ'}")


async def main():
    """メインテスト実行"""
    print("\n" + "🔥"*30)
    print("🚀 自動進行機能テストスイート")
    print("🔥"*30)
    
    # 各テストを実行
    await test_information_sufficient()
    await test_information_insufficient()
    test_workflow_resumption()
    test_workflow_controller_integration()
    
    print("\n" + "="*60)
    print("✅ すべてのテストが完了しました")
    print("="*60)


if __name__ == "__main__":
    # テストを実行
    asyncio.run(main())