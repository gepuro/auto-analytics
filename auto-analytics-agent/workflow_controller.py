"""
ワークフロー制御システム
情報の完全性に基づいてユーザー対話と分析フローを動的に制御
"""

import json
import re
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

class WorkflowController:
    """
    分析ワークフローの動的制御を行うコントローラークラス
    """
    
    def __init__(self):
        self.state = {
            "workflow_phase": "request_interpretation",
            "information_status": "unknown",
            "user_input_required": False,
            "clarification_questions": [],
            "analysis_context": {},
            "workflow_history": []
        }
    
    def analyze_information_gap(self, gap_analysis_output: str) -> Dict[str, Any]:
        """
        情報不足検出エージェントの出力を分析して次のアクションを決定
        
        Args:
            gap_analysis_output: 情報不足検出エージェントの出力
            
        Returns:
            次のワークフローアクションの詳細
        """
        try:
            # JSON形式の出力をパース
            if gap_analysis_output.strip().startswith('{'):
                gap_data = json.loads(gap_analysis_output)
                status = gap_data.get("status", "needs_clarification")
                missing_info = gap_data.get("missing_info", [])
                ambiguous_points = gap_data.get("ambiguous_points", [])
                confidence = gap_data.get("confidence_score", 0.0)
            else:
                # テキスト形式の場合、キーワードで判定
                status = self._extract_status_from_text(gap_analysis_output)
                missing_info = self._extract_missing_info_from_text(gap_analysis_output)
                ambiguous_points = self._extract_ambiguous_points_from_text(gap_analysis_output)
                confidence = self._estimate_confidence_from_text(gap_analysis_output)
            
            # ワークフロー決定
            if status == "sufficient" and confidence > 0.7:
                return {
                    "action": "continue_analysis",
                    "next_phase": "schema_exploration",
                    "user_input_required": False,
                    "message": "情報が十分に揃いました。データ分析を開始します。",
                    "confidence": confidence
                }
            else:
                return {
                    "action": "request_clarification",
                    "next_phase": "user_confirmation",
                    "user_input_required": True,
                    "missing_info": missing_info,
                    "ambiguous_points": ambiguous_points,
                    "message": "追加情報が必要です。詳細をお聞かせください。",
                    "confidence": confidence
                }
                
        except Exception as e:
            # エラー時はデフォルトで確認を求める
            return {
                "action": "request_clarification",
                "next_phase": "user_confirmation", 
                "user_input_required": True,
                "error": str(e),
                "message": "分析を開始する前に、いくつか確認させてください。"
            }
    
    def _extract_status_from_text(self, text: str) -> str:
        """テキストから情報の完全性ステータスを抽出"""
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in ["sufficient", "十分", "完全", "問題なし"]):
            return "sufficient"
        elif any(keyword in text_lower for keyword in ["needs_clarification", "要確認", "不足", "曖昧"]):
            return "needs_clarification"
        else:
            return "needs_clarification"  # デフォルトは確認要求
    
    def _extract_missing_info_from_text(self, text: str) -> List[str]:
        """テキストから不足情報を抽出"""
        missing_patterns = [
            r"不足.*?情報[：:]?\s*([^。\n]*)",
            r"missing.*?info[：:]?\s*([^。\n]*)",
            r"必要.*?情報[：:]?\s*([^。\n]*)",
        ]
        
        missing_info = []
        for pattern in missing_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            missing_info.extend(matches)
        
        return [info.strip() for info in missing_info if info.strip()]
    
    def _extract_ambiguous_points_from_text(self, text: str) -> List[str]:
        """テキストから曖昧な点を抽出"""
        ambiguous_patterns = [
            r"曖昧.*?点[：:]?\s*([^。\n]*)",
            r"ambiguous.*?points?[：:]?\s*([^。\n]*)",
            r"不明確.*?部分[：:]?\s*([^。\n]*)",
        ]
        
        ambiguous_points = []
        for pattern in ambiguous_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            ambiguous_points.extend(matches)
        
        return [point.strip() for point in ambiguous_points if point.strip()]
    
    def _estimate_confidence_from_text(self, text: str) -> float:
        """テキストから信頼度を推定"""
        confidence_keywords = {
            "確実": 0.9, "十分": 0.8, "問題なし": 0.8, "明確": 0.7,
            "sufficient": 0.8, "clear": 0.7, "complete": 0.9,
            "曖昧": 0.3, "不足": 0.2, "不明": 0.2, "確認必要": 0.1,
            "ambiguous": 0.3, "missing": 0.2, "unclear": 0.2
        }
        
        text_lower = text.lower()
        confidence_scores = []
        
        for keyword, score in confidence_keywords.items():
            if keyword in text_lower:
                confidence_scores.append(score)
        
        return sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
    
    def generate_clarification_questions(self, 
                                       original_request: str,
                                       missing_info: List[str],
                                       ambiguous_points: List[str]) -> str:
        """
        不足情報に基づいて具体的な確認質問を生成
        
        Args:
            original_request: 元の分析リクエスト
            missing_info: 不足している情報
            ambiguous_points: 曖昧な点
            
        Returns:
            ユーザーへの確認質問テキスト
        """
        questions = []
        
        # 標準的な確認項目
        standard_questions = {
            "期間": "分析対象の期間を教えてください：\n"
                   "• 今月（現在の月）\n"
                   "• 先月\n" 
                   "• 今年度\n"
                   "• 昨年度\n"
                   "• 特定期間（具体的な開始日-終了日）",
                   
            "粒度": "データの集計レベルを教えてください：\n"
                   "• 日別\n"
                   "• 週別\n"
                   "• 月別\n"
                   "• 年別\n"
                   "• その他（具体的に）",
                   
            "対象": "分析対象の詳細を教えてください：\n"
                   "• 全体\n"
                   "• 特定商品・サービス\n"
                   "• 特定地域・店舗\n"
                   "• 特定顧客層\n"
                   "• その他（具体的に）",
                   
            "比較": "比較分析の要否を教えてください：\n"
                   "• 前年同期との比較\n"
                   "• 前月との比較\n"
                   "• 目標値との比較\n"
                   "• 比較不要\n"
                   "• その他（具体的に）"
        }
        
        # 不足情報に基づく質問生成
        for info in missing_info:
            for key, question in standard_questions.items():
                if key in info or any(keyword in info for keyword in ["時間", "期間", "いつ"]):
                    if key == "期間":
                        questions.append(f"📅 **{question}**")
                elif any(keyword in info for keyword in ["レベル", "粒度", "単位"]):
                    if key == "粒度":
                        questions.append(f"📊 **{question}**")
                elif any(keyword in info for keyword in ["対象", "何を", "どれを"]):
                    if key == "対象":
                        questions.append(f"🎯 **{question}**")
                elif any(keyword in info for keyword in ["比較", "対比"]):
                    if key == "比較":
                        questions.append(f"📈 **{question}**")
        
        # 曖昧な点に基づく質問生成
        for point in ambiguous_points:
            questions.append(f"❓ **{point}について詳しく教えてください**")
        
        # デフォルト質問（何も特定できない場合）
        if not questions:
            questions = [
                "📅 **分析期間**: いつの期間のデータを分析しますか？",
                "📊 **集計レベル**: どの単位で分析しますか？（日別、月別など）",
                "🎯 **分析対象**: 何を分析対象としますか？"
            ]
        
        # 質問をフォーマット
        question_text = f"""
分析のご依頼をいただき、ありがとうございます。

**📋 お聞かせいただきたい内容：**

{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(questions))}

これらの情報をお教えいただければ、より正確で有用な分析レポートをお作りできます。
"""
        
        return question_text.strip()
    
    def process_user_response(self, 
                            original_request: str,
                            clarification_questions: str,
                            user_response: str) -> str:
        """
        ユーザーの回答を処理して完成した分析リクエストを生成
        
        Args:
            original_request: 元の分析リクエスト
            clarification_questions: 送信した確認質問
            user_response: ユーザーからの回答
            
        Returns:
            統合された完全な分析リクエスト
        """
        completed_request = f"""
【完成した分析リクエスト】

**元のリクエスト**: {original_request}

**追加いただいた情報**: {user_response}

**統合された分析要件**:
{self._integrate_request_and_response(original_request, user_response)}

これで分析に必要な情報が揃いました。データベース調査を開始します。

生成日時: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
"""
        
        return completed_request.strip()
    
    def _integrate_request_and_response(self, original: str, response: str) -> str:
        """元のリクエストとユーザー回答を統合"""
        # シンプルな統合ロジック（実際にはより高度な自然言語処理が必要）
        integration = f"• 分析内容: {original}\n• 詳細条件: {response}"
        
        return integration
    
    def update_workflow_state(self, phase: str, data: Dict[str, Any]):
        """ワークフロー状態を更新"""
        self.state["workflow_phase"] = phase
        self.state["analysis_context"].update(data)
        self.state["workflow_history"].append({
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "data": data
        })
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """現在のワークフロー状態を取得"""
        return {
            "current_phase": self.state["workflow_phase"],
            "information_status": self.state["information_status"],
            "user_input_required": self.state["user_input_required"],
            "progress": len(self.state["workflow_history"]),
            "last_updated": datetime.now().isoformat()
        }


# グローバルワークフローコントローラーインスタンス
workflow_controller = WorkflowController()


def check_information_completeness_v2(gap_analysis_output: str) -> Tuple[bool, Dict[str, Any]]:
    """
    情報の完全性をチェックし、次のアクションを決定する関数
    
    Args:
        gap_analysis_output: 情報不足検出エージェントの出力
        
    Returns:
        (情報が十分かどうか, 詳細情報)
    """
    result = workflow_controller.analyze_information_gap(gap_analysis_output)
    return result["action"] == "continue_analysis", result


def generate_user_questions(original_request: str, gap_analysis: str) -> str:
    """
    ユーザーに送信する確認質問を生成する関数
    
    Args:
        original_request: 元の分析リクエスト
        gap_analysis: 情報不足分析結果
        
    Returns:
        ユーザーへの確認質問テキスト
    """
    _, analysis_result = check_information_completeness_v2(gap_analysis)
    
    return workflow_controller.generate_clarification_questions(
        original_request=original_request,
        missing_info=analysis_result.get("missing_info", []),
        ambiguous_points=analysis_result.get("ambiguous_points", [])
    )


def integrate_user_feedback(original_request: str, 
                          questions: str, 
                          user_response: str) -> str:
    """
    ユーザーのフィードバックを統合して完成したリクエストを生成
    
    Args:
        original_request: 元のリクエスト
        questions: 送信した質問
        user_response: ユーザーの回答
        
    Returns:
        統合された完成リクエスト
    """
    return workflow_controller.process_user_response(
        original_request=original_request,
        clarification_questions=questions,
        user_response=user_response
    )