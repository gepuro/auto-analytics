"""
Report Template Manager for Auto Analytics System

This module provides template management functionality for HTML report generation.
Note: Currently using simplified HTML generation approach. This module is kept for
future template expansion but main classes have been removed as they were unused.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class ReportType(Enum):
    """Enumeration of available report types."""
    BASIC = "basic_report.html"
    DETAILED = "detailed_report.html"
    SUMMARY = "summary_report.html"
    DASHBOARD = "dashboard_report.html"


@dataclass
class TemplateConfig:
    """Configuration for report template."""
    name: str
    description: str
    template_file: str
    required_fields: List[str]
    optional_fields: List[str]
    supports_charts: bool = False
    supports_tables: bool = True


# This module has been simplified - main template management classes removed
# as they were not being used in the current implementation.
# The system currently uses the inline HTML generation in workflow.py
# and the HTMLReportGenerator class for report creation.