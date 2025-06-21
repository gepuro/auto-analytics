"""
Report Template Manager for Auto Analytics System

This module provides template management functionality for HTML report generation.
It handles template loading, customization, and provides different report layouts
for various analysis types.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound


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


class ReportTemplateManager:
    """
    Manager class for handling HTML report templates.
    
    This class provides functionality to:
    - Load and manage different report templates
    - Validate template requirements
    - Customize template rendering
    - Support multiple report layouts
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the template manager.
        
        Args:
            template_dir: Directory containing template files
        """
        if template_dir is None:
            current_dir = Path(__file__).parent
            template_dir = current_dir / "templates"
        
        self.template_dir = Path(template_dir)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters
        self._register_custom_filters()
        
        # Define available templates
        self.templates = self._initialize_templates()
    
    def _register_custom_filters(self):
        """Register custom Jinja2 filters for templates."""
        self.env.filters['format_percentage'] = self._format_percentage
        self.env.filters['format_currency'] = self._format_currency
        self.env.filters['format_large_number'] = self._format_large_number
        self.env.filters['truncate_text'] = self._truncate_text
        self.env.filters['highlight_keywords'] = self._highlight_keywords
        self.env.filters['format_sql'] = self._format_sql
    
    def _format_percentage(self, value: float, decimals: int = 1) -> str:
        """Format number as percentage."""
        try:
            return f"{float(value):.{decimals}f}%"
        except (ValueError, TypeError):
            return str(value)
    
    def _format_currency(self, value: float, currency: str = "¥") -> str:
        """Format number as currency."""
        try:
            return f"{currency}{float(value):,.0f}"
        except (ValueError, TypeError):
            return str(value)
    
    def _format_large_number(self, value: float) -> str:
        """Format large numbers with units (K, M, B)."""
        try:
            num = float(value)
            if num >= 1_000_000_000:
                return f"{num/1_000_000_000:.1f}B"
            elif num >= 1_000_000:
                return f"{num/1_000_000:.1f}M"
            elif num >= 1_000:
                return f"{num/1_000:.1f}K"
            else:
                return f"{num:.0f}"
        except (ValueError, TypeError):
            return str(value)
    
    def _truncate_text(self, text: str, length: int = 100) -> str:
        """Truncate text to specified length."""
        if len(text) <= length:
            return text
        return text[:length] + "..."
    
    def _highlight_keywords(self, text: str, keywords: List[str]) -> str:
        """Highlight specified keywords in text."""
        for keyword in keywords:
            text = text.replace(
                keyword, 
                f'<mark class="highlight">{keyword}</mark>'
            )
        return text
    
    def _format_sql(self, sql: str) -> str:
        """Format SQL query for better readability."""
        if not sql:
            return ""
        
        # Basic SQL formatting
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN',
            'INNER JOIN', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT',
            'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP'
        ]
        
        formatted = sql
        for keyword in keywords:
            formatted = formatted.replace(
                keyword, 
                f'<span class="sql-keyword">{keyword}</span>'
            )
        
        return formatted
    
    def _initialize_templates(self) -> Dict[str, TemplateConfig]:
        """Initialize available template configurations."""
        return {
            'basic': TemplateConfig(
                name="Basic Report",
                description="基本的な分析レポート用テンプレート",
                template_file="basic_report.html",
                required_fields=["report_title", "generation_time"],
                optional_fields=[
                    "request_summary", "schema_info", "sql_query",
                    "data_table", "summary_stats", "insights", "recommendations"
                ],
                supports_tables=True,
                supports_charts=False
            ),
            'detailed': TemplateConfig(
                name="Detailed Report",
                description="詳細分析レポート用テンプレート",
                template_file="detailed_report.html",
                required_fields=["report_title", "generation_time", "analysis_results"],
                optional_fields=[
                    "request_summary", "schema_info", "sql_query", "data_table",
                    "summary_stats", "insights", "recommendations", "methodology",
                    "data_quality", "limitations"
                ],
                supports_tables=True,
                supports_charts=True
            ),
            'summary': TemplateConfig(
                name="Summary Report",
                description="要約レポート用テンプレート",
                template_file="summary_report.html",
                required_fields=["report_title", "key_findings"],
                optional_fields=["summary_stats", "recommendations"],
                supports_tables=False,
                supports_charts=False
            )
        }
    
    def get_available_templates(self) -> Dict[str, TemplateConfig]:
        """Get list of available template configurations."""
        return self.templates.copy()
    
    def get_template_config(self, template_name: str) -> Optional[TemplateConfig]:
        """Get configuration for specific template."""
        return self.templates.get(template_name)
    
    def validate_data_for_template(
        self, 
        template_name: str, 
        data: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        Validate if data contains required fields for template.
        
        Args:
            template_name: Name of template to validate against
            data: Data dictionary to validate
            
        Returns:
            Tuple of (is_valid, missing_fields)
        """
        config = self.templates.get(template_name)
        if not config:
            return False, [f"Template '{template_name}' not found"]
        
        missing_fields = []
        for field in config.required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields
    
    def load_template(self, template_name: str) -> Template:
        """
        Load Jinja2 template by name.
        
        Args:
            template_name: Name of template (key from templates dict)
            
        Returns:
            Loaded Jinja2 template
            
        Raises:
            TemplateNotFound: If template file doesn't exist
        """
        config = self.templates.get(template_name)
        if not config:
            # Fallback to direct template file loading
            template_file = template_name if template_name.endswith('.html') else f"{template_name}.html"
        else:
            template_file = config.template_file
        
        try:
            return self.env.get_template(template_file)
        except TemplateNotFound:
            raise TemplateNotFound(f"Template file '{template_file}' not found in {self.template_dir}")
    
    def render_template(
        self, 
        template_name: str, 
        data: Dict[str, Any],
        validate: bool = True
    ) -> str:
        """
        Render template with provided data.
        
        Args:
            template_name: Name of template to render
            data: Data dictionary for template
            validate: Whether to validate data before rendering
            
        Returns:
            Rendered HTML content
            
        Raises:
            ValueError: If validation fails
            TemplateNotFound: If template doesn't exist
        """
        if validate:
            is_valid, missing_fields = self.validate_data_for_template(template_name, data)
            if not is_valid:
                raise ValueError(f"Missing required fields for template '{template_name}': {missing_fields}")
        
        template = self.load_template(template_name)
        return template.render(**data)
    
    def create_custom_template(
        self,
        template_name: str,
        template_content: str,
        config: Optional[TemplateConfig] = None
    ) -> None:
        """
        Create a custom template from string content.
        
        Args:
            template_name: Name for the new template
            template_content: HTML template content
            config: Optional template configuration
        """
        template_file = f"{template_name}.html"
        template_path = self.template_dir / template_file
        
        # Write template file
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        # Add to templates registry
        if config is None:
            config = TemplateConfig(
                name=template_name.title(),
                description=f"Custom template: {template_name}",
                template_file=template_file,
                required_fields=["report_title"],
                optional_fields=[],
                supports_tables=True,
                supports_charts=False
            )
        
        self.templates[template_name] = config
    
    def get_template_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """
        Recommend appropriate templates based on available data.
        
        Args:
            data: Analysis data dictionary
            
        Returns:
            List of recommended template names
        """
        recommendations = []
        
        for template_name, config in self.templates.items():
            is_valid, _ = self.validate_data_for_template(template_name, data)
            
            if is_valid:
                # Calculate fitness score based on available optional fields
                available_optional = sum(
                    1 for field in config.optional_fields 
                    if field in data and data[field] is not None
                )
                total_optional = len(config.optional_fields)
                
                fitness_score = available_optional / max(total_optional, 1)
                recommendations.append((template_name, fitness_score))
        
        # Sort by fitness score (descending)
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return [name for name, _ in recommendations]
    
    def list_template_files(self) -> List[str]:
        """List all HTML template files in the template directory."""
        if not self.template_dir.exists():
            return []
        
        return [
            f.name for f in self.template_dir.iterdir() 
            if f.is_file() and f.suffix == '.html'
        ]
    
    def get_template_preview(self, template_name: str) -> str:
        """
        Get a preview of template structure (first few lines).
        
        Args:
            template_name: Name of template
            
        Returns:
            Preview text of template
        """
        try:
            config = self.templates.get(template_name)
            template_file = config.template_file if config else f"{template_name}.html"
            template_path = self.template_dir / template_file
            
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:20]  # First 20 lines
                    return ''.join(lines)
            else:
                return "Template file not found"
        except Exception as e:
            return f"Error reading template: {str(e)}"


# Convenience functions
def get_template_manager(template_dir: Optional[str] = None) -> ReportTemplateManager:
    """Get a configured template manager instance."""
    return ReportTemplateManager(template_dir)


def list_available_templates(template_dir: Optional[str] = None) -> Dict[str, str]:
    """List available templates with descriptions."""
    manager = get_template_manager(template_dir)
    return {
        name: config.description 
        for name, config in manager.get_available_templates().items()
    }


def recommend_template(data: Dict[str, Any], template_dir: Optional[str] = None) -> Optional[str]:
    """Recommend the best template for given data."""
    manager = get_template_manager(template_dir)
    recommendations = manager.get_template_recommendations(data)
    return recommendations[0] if recommendations else None


# Example usage
if __name__ == "__main__":
    # Initialize template manager
    manager = ReportTemplateManager()
    
    # List available templates
    print("Available templates:")
    for name, config in manager.get_available_templates().items():
        print(f"  {name}: {config.description}")
    
    # Example data
    sample_data = {
        'report_title': 'Test Report',
        'generation_time': '2024-01-01 10:00:00',
        'data_table': {'headers': ['Column1'], 'rows': [['Value1']]},
        'insights': 'Test insights'
    }
    
    # Get recommendations
    recommendations = manager.get_template_recommendations(sample_data)
    print(f"\nRecommended templates: {recommendations}")
    
    # Validate data for specific template
    is_valid, missing = manager.validate_data_for_template('basic', sample_data)
    print(f"\nValidation for 'basic' template: Valid={is_valid}, Missing={missing}")