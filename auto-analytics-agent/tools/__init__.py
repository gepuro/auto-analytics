"""
Auto Analytics Agent Tools

This package contains HTML report generation tools for the Auto Analytics system.
It provides functionality to create professional, formatted reports from data analysis results.
"""

from .report_templates import ReportType, TemplateConfig
from .report_utils import (
    DataProcessor,
    TextFormatter,
    FileUtils,
    ValidationUtils
)
from .simple_link_generator import SimpleReportLinkGenerator, create_simple_report_link, get_simple_file_url
from .adk_report_tool import ADKHTMLReportTool, create_adk_report_tool, generate_html_report_from_workflow

__version__ = "1.0.0"

__all__ = [
    # Main classes
    'ReportType',
    'TemplateConfig',
    'DataProcessor',
    'TextFormatter',
    'FileUtils',
    'ValidationUtils',
    'SimpleReportLinkGenerator',
    'ADKHTMLReportTool',
    
    # Convenience functions
    'create_simple_report_link',
    'get_simple_file_url',
    'create_adk_report_tool',
    'generate_html_report_from_workflow'
]