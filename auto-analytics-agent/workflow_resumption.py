"""
ワークフロー再開ハンドラー
ユーザー入力後の自動的なワークフロー再開を管理
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime


class WorkflowResumptionHandler:
    """
    ユーザー入力後のワークフロー自動再開ハンドラー
    
    このハンドラーは以下の機能を提供：
    1. ユーザー入力の受け取りと検証
    2. 元のリクエストとの統合
    3. ワークフローの自動再開
    4. 進捗状況の追跡
    """
    
    def __init__(self):
        """ハンドラーの初期化"""
        self.resumption_state = {
            "original_request": None,
            "user_questions": None,
            "user_response": None,
            "completed_request": None,
            "resumption_timestamp": None,
            "workflow_resumed": False
        }
    
    def prepare_for_resumption(self, 
                              original_request: str,
                              user_questions: str) -> Dict[str, Any]:
        """
        ワークフロー再開の準備
        
        Args:
            original_request: 元の分析リクエスト
            user_questions: ユーザーに送信した質問
            
        Returns:
            準備状態の情報
        """
        self.resumption_state.update({
            "original_request": original_request,
            "user_questions": user_questions,
            "workflow_resumed": False,
            "preparation_timestamp": datetime.now().isoformat()
        })
        
        return {
            "status": "prepared",
            "message": "ユーザー入力を待機しています",
            "original_request": original_request,
            "questions_sent": user_questions
        }
    
    def resume_after_user_input(self, 
                               user_response: str,
                               ctx: Optional[Any] = None) -> Dict[str, Any]:
        """
        ユーザー入力を受けて自動的にワークフローを再開
        
        Args:
            user_response: ユーザーからの追加情報
            ctx: 実行コンテキスト（オプション）
            
        Returns:
            再開情報
        """
        
        # ユーザー入力を記録
        self.resumption_state["user_response"] = user_response
        self.resumption_state["resumption_timestamp"] = datetime.now().isoformat()
        
        # 情報を統合
        completed_request = self.integrate_user_feedback(
            self.resumption_state["original_request"],
            user_response
        )
        
        self.resumption_state["completed_request"] = completed_request
        
        # コンテキストを更新（提供されている場合）
        if ctx:
            ctx.session.state["interpreted_request"] = completed_request
            ctx.session.state["information_complete"] = True
            ctx.session.state["user_response_received"] = True
        
        # ワークフロー再開フラグを設定
        self.resumption_state["workflow_resumed"] = True
        
        return {
            "status": "resumed",
            "action": "continue_to_schema_exploration",
            "completed_request": completed_request,
            "next_phase": "schema_exploration",
            "message": "追加情報を受け取りました。データ分析を自動的に再開します。",
            "auto_proceed": True  # 自動進行フラグ
        }
    
    def integrate_user_feedback(self, 
                               original_request: str,
                               user_response: str) -> str:
        """
        元のリクエストとユーザーの追加情報を統合
        
        Args:
            original_request: 元の分析リクエスト
            user_response: ユーザーからの追加情報
            
        Returns:
            統合された完全なリクエスト
        """
        
        # ユーザー回答から具体的な情報を抽出
        extracted_info = self._extract_user_selections(user_response)
        
        completed_request = f"""
【完成した分析リクエスト】

📝 **元のリクエスト**: {original_request}

➕ **追加情報**:
{user_response}

🎯 **統合された分析要件**:
• 分析内容: {original_request}
{self._format_extracted_info(extracted_info)}

✅ これらの情報を基に、包括的なデータ分析を自動的に実行します。

生成日時: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
"""
        
        return completed_request.strip()
    
    def _extract_user_selections(self, user_response: str) -> Dict[str, str]:
        """
        ユーザー回答から選択された項目を抽出
        
        Args:
            user_response: ユーザーの回答テキスト
            
        Returns:
            抽出された情報の辞書
        """
        extracted = {}
        
        # 期間の抽出
        period_keywords = {
            "今月": "current_month",
            "先月": "last_month", 
            "今年": "current_year",
            "昨年": "last_year",
            "今年度": "current_fiscal_year",
            "昨年度": "last_fiscal_year"
        }
        
        for keyword, value in period_keywords.items():
            if keyword in user_response:
                extracted["period"] = keyword
                break
        
        # 粒度の抽出
        granularity_keywords = ["日別", "週別", "月別", "年別", "時間別"]
        for keyword in granularity_keywords:
            if keyword in user_response:
                extracted["granularity"] = keyword
                break
        
        # 比較条件の抽出
        if "前年同期" in user_response:
            extracted["comparison"] = "前年同期比較"
        elif "前月" in user_response:
            extracted["comparison"] = "前月比較"
        elif "目標" in user_response:
            extracted["comparison"] = "目標値比較"
        
        return extracted
    
    def _format_extracted_info(self, extracted_info: Dict[str, str]) -> str:
        """
        抽出された情報をフォーマット
        
        Args:
            extracted_info: 抽出された情報
            
        Returns:
            フォーマットされた文字列
        """
        lines = []
        
        if "period" in extracted_info:
            lines.append(f"• 分析期間: {extracted_info['period']}")
        
        if "granularity" in extracted_info:
            lines.append(f"• 集計単位: {extracted_info['granularity']}")
            
        if "comparison" in extracted_info:
            lines.append(f"• 比較方法: {extracted_info['comparison']}")
            
        return "\n".join(lines) if lines else "• 詳細条件: ユーザー指定の条件に従う"
    
    def get_resumption_status(self) -> Dict[str, Any]:
        """
        現在の再開状態を取得
        
        Returns:
            再開状態の情報
        """
        return {
            "has_original_request": bool(self.resumption_state["original_request"]),
            "has_user_response": bool(self.resumption_state["user_response"]),
            "workflow_resumed": self.resumption_state["workflow_resumed"],
            "completed_request": self.resumption_state["completed_request"],
            "timestamps": {
                "preparation": self.resumption_state.get("preparation_timestamp"),
                "resumption": self.resumption_state.get("resumption_timestamp")
            }
        }
    
    def reset(self):
        """再開ハンドラーの状態をリセット"""
        self.resumption_state = {
            "original_request": None,
            "user_questions": None,
            "user_response": None,
            "completed_request": None,
            "resumption_timestamp": None,
            "workflow_resumed": False
        }


# グローバルインスタンス
workflow_resumption_handler = WorkflowResumptionHandler()