"""
Auto Analytics Agent Tools

This package contains HTML report generation tools for the Auto Analytics system.
It provides functionality to create professional, formatted reports from data analysis results.
"""

from .adk_report_tool import (
    ADKHTMLReportTool,
    create_adk_report_tool,
    generate_html_report_from_workflow,
)
from .simple_link_generator import SimpleReportLinkGenerator

__version__ = "1.0.0"

__all__ = [
    # Main classes
    "SimpleReportLinkGenerator",
    "ADKHTMLReportTool",
    # Convenience functions
    "create_adk_report_tool",
    "generate_html_report_from_workflow",
]
