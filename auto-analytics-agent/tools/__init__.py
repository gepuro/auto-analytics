"""
Auto Analytics Agent Tools

This package contains HTML report generation tools for the Auto Analytics system.
It provides functionality to create professional, formatted reports from data analysis results.
"""

from .html_report_generator import HTMLReportGenerator, create_html_report
from .report_templates import ReportTemplateManager, list_available_templates, recommend_template
from .report_utils import (
    DataProcessor,
    TextFormatter,
    FileUtils,
    ValidationUtils,
    create_sample_report_data
)
from .simple_link_generator import SimpleReportLinkGenerator, create_simple_report_link, get_simple_file_url
from .report_agent_tool import generate_html_report_tool, create_workflow_report, format_report_link_message
from .adk_report_tool import ADKHTMLReportTool, create_adk_report_tool, generate_html_report_from_workflow

__version__ = "1.0.0"

__all__ = [
    # Main classes
    'HTMLReportGenerator',
    'ReportTemplateManager',
    'DataProcessor',
    'TextFormatter',
    'FileUtils',
    'ValidationUtils',
    'SimpleReportLinkGenerator',
    'ADKHTMLReportTool',
    
    # Convenience functions
    'create_html_report',
    'list_available_templates',
    'recommend_template',
    'create_sample_report_data',
    'create_simple_report_link',
    'get_simple_file_url',
    'create_adk_report_tool',
    
    # ADK Agent Tools
    'generate_html_report_tool',
    'create_workflow_report',
    'format_report_link_message',
    'generate_html_report_from_workflow'
]