"""
Report Agent Tool for ADK Integration

This module provides ADK-compatible tools for HTML report generation
that can be used by agents in the workflow.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path

from .html_report_generator import HTMLReportGenerator
from .simple_link_generator import create_simple_report_link


def generate_html_report_tool(
    analysis_data: str,
    report_title: Optional[str] = None,
    template_name: str = "basic_report.html"
) -> str:
    """
    ADK-compatible tool function for generating HTML reports.
    
    Args:
        analysis_data: JSON string containing analysis results
        report_title: Title for the report
        template_name: Template to use for generation
        
    Returns:
        JSON string containing report information and links
    """
    try:
        # Parse analysis data
        if isinstance(analysis_data, str):
            data = json.loads(analysis_data)
        else:
            data = analysis_data
        
        # Generate report
        generator = HTMLReportGenerator()
        result = generator.generate_report(
            analysis_data=data,
            title=report_title,
            template_name=template_name
        )
        
        # Format response
        response = {
            "success": True,
            "message": result.get("user_message", "HTMLレポートが生成されました"),
            "file_path": result["file_path"],
            "report_title": result["report_title"],
            "http_url": result.get("http_url", ""),
            "file_url": result.get("file_url", ""),
            "best_url": result.get("best_url", ""),
            "generation_time": result["generation_time"]
        }
        
        return json.dumps(response, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "message": f"HTMLレポート生成中にエラーが発生しました: {str(e)}"
        }
        return json.dumps(error_response, ensure_ascii=False, indent=2)


def create_workflow_report(
    workflow_context: str,
    report_title: Optional[str] = None
) -> str:
    """
    Create HTML report from complete workflow context.
    
    Args:
        workflow_context: JSON string containing all workflow results
        report_title: Custom title for the report
        
    Returns:
        JSON string with report information
    """
    try:
        # Parse workflow context
        if isinstance(workflow_context, str):
            context = json.loads(workflow_context)
        else:
            context = workflow_context
        
        # Extract analysis data from workflow context
        analysis_data = {}
        
        # Map context keys to analysis data structure
        for key, value in context.items():
            if 'interpreted_request' in key:
                analysis_data['interpreted_request'] = value
            elif 'schema_info' in key:
                analysis_data['schema_info'] = value
            elif 'sample_analysis' in key:
                analysis_data['sample_analysis'] = value
            elif 'sql_query_info' in key:
                analysis_data['sql_query_info'] = value
            elif 'query_execution_result' in key:
                analysis_data['query_execution_result'] = value
            elif 'analysis_results' in key:
                analysis_data['analysis_results'] = value
        
        # Generate report
        generator = HTMLReportGenerator()
        result = generator.create_from_workflow_result(
            workflow_output=analysis_data,
            title=report_title
        )
        
        # Format response
        response = {
            "success": True,
            "message": result.get("user_message", "ワークフローレポートが生成されました"),
            "file_path": result["file_path"],
            "report_title": result["report_title"],
            "http_url": result.get("http_url", ""),
            "file_url": result.get("file_url", ""),
            "best_url": result.get("best_url", ""),
            "generation_time": result["generation_time"],
            "workflow_summary": "全ワークフローステップの結果を含むレポートです"
        }
        
        return json.dumps(response, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "message": f"ワークフローレポート生成中にエラーが発生しました: {str(e)}"
        }
        return json.dumps(error_response, ensure_ascii=False, indent=2)


def format_report_link_message(
    file_path: str,
    report_title: Optional[str] = None,
    generation_time: Optional[str] = None
) -> str:
    """
    Format a user-friendly message with report links.
    
    Args:
        file_path: Path to the generated report file
        report_title: Title of the report
        generation_time: When the report was generated
        
    Returns:
        Formatted message string
    """
    try:
        return create_simple_report_link(
            file_path=file_path,
            report_title=report_title,
            generation_time=generation_time
        )
    except Exception as e:
        return f"レポートリンクの生成中にエラーが発生しました: {str(e)}"


# Tool registry for ADK agents
REPORT_TOOLS = {
    "generate_html_report": generate_html_report_tool,
    "create_workflow_report": create_workflow_report,
    "format_report_link": format_report_link_message
}


def get_report_tool_descriptions() -> Dict[str, str]:
    """Get descriptions of available report tools."""
    return {
        "generate_html_report": "分析データからHTMLレポートを生成し、アクセス用リンクを提供します",
        "create_workflow_report": "ワークフロー全体の結果からHTMLレポートを生成します", 
        "format_report_link": "レポートファイルのアクセス用リンクを整形して表示します"
    }


# Example usage for testing
if __name__ == "__main__":
    # Test data
    test_data = {
        "title": "テストレポート",
        "interpreted_request": "テスト分析リクエスト",
        "analysis_results": "テスト分析結果"
    }
    
    # Test report generation
    result = generate_html_report_tool(
        analysis_data=json.dumps(test_data),
        report_title="テスト用HTMLレポート"
    )
    
    print("=== HTMLレポート生成テスト ===")
    print(result)