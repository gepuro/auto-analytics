"""
HTML Report Generator for Auto Analytics System

This module provides functionality to generate HTML reports from data analysis results.
It integrates with the existing ADK agent workflow to produce formatted, professional
reports that can be easily shared and viewed.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from jinja2 import Environment, FileSystemLoader, Template

from .simple_link_generator import SimpleReportLinkGenerator, create_simple_report_link


class HTMLReportGenerator:
    """
    HTML Report Generator for creating professional data analysis reports.

    This class handles the conversion of analysis results into formatted HTML reports
    using Jinja2 templates. It supports various data formats including query results,
    statistical summaries, and analysis insights.
    """

    def __init__(
        self, template_dir: Optional[str] = None, output_dir: Optional[str] = None
    ):
        """
        Initialize the HTML Report Generator.

        Args:
            template_dir: Directory containing HTML templates (defaults to tools/templates)
            output_dir: Directory for generated reports (defaults to reports/)
        """
        # Set default template directory
        if template_dir is None:
            current_dir = Path(__file__).parent
            template_dir = current_dir / "templates"

        self.template_dir = Path(template_dir)

        # Set default output directory to workspace reports
        if output_dir is None:
            # Use the shared reports directory at workspace root
            current_dir = Path(__file__).parent
            workspace_root = (
                current_dir.parent.parent
            )  # Go up from tools/ -> auto-analytics-agent/ -> workspace/
            output_dir = workspace_root / "reports"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self.env.filters["format_datetime"] = self._format_datetime
        self.env.filters["format_number"] = self._format_number
        self.env.filters["safe_html"] = self._safe_html

        # Initialize simple link generator
        self.link_generator = SimpleReportLinkGenerator()

    def _format_datetime(self, dt: Union[datetime, str]) -> str:
        """Format datetime for display."""
        if isinstance(dt, str):
            return dt
        if isinstance(dt, datetime):
            return dt.strftime("%Y年%m月%d日 %H:%M:%S")
        return str(dt)

    def _format_number(self, num: Union[int, float, str]) -> str:
        """Format numbers with thousand separators."""
        try:
            if isinstance(num, str):
                num = float(num)
            if isinstance(num, float) and num.is_integer():
                return f"{int(num):,}"
            return f"{float(num):,.2f}"
        except (ValueError, TypeError):
            return str(num)

    def _safe_html(self, text: str) -> str:
        """Mark text as safe HTML (for pre-formatted content)."""
        return text

    def generate_report(
        self,
        analysis_data: Dict[str, Any],
        template_name: str = "basic_report.html",
        output_filename: Optional[str] = None,
        title: Optional[str] = None,
        include_link: bool = True,
    ) -> Dict[str, str]:
        """
        Generate an HTML report from analysis data.

        Args:
            analysis_data: Dictionary containing analysis results and metadata
            template_name: Name of the template file to use
            output_filename: Custom filename for the output (auto-generated if None)
            title: Custom title for the report
            include_link: Whether to include clickable link information

        Returns:
            Dictionary containing file path, link information, and metadata

        Raises:
            FileNotFoundError: If template file doesn't exist
            Exception: If report generation fails
        """
        try:
            # Load template
            template = self.env.get_template(template_name)

            # Prepare data for template
            report_data = self._prepare_report_data(analysis_data, title)

            # Generate HTML content
            html_content = template.render(**report_data)

            # Generate output filename if not provided
            if output_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"analytics_report_{timestamp}.html"

            # Ensure output filename has .html extension
            if not output_filename.endswith(".html"):
                output_filename += ".html"

            # Write to file
            output_path = self.output_dir / output_filename
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Prepare return information
            result = {
                "file_path": str(output_path),
                "filename": output_filename,
                "report_title": report_data.get("report_title", "データ分析レポート"),
                "generation_time": report_data.get(
                    "generation_time", datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
                ),
            }

            # Add link information if requested
            if include_link:
                link_summary = self.link_generator.generate_report_summary(
                    output_path, result["report_title"], result["generation_time"]
                )
                result.update(link_summary)
                result["user_message"] = self.link_generator.format_user_message(
                    output_path, result["report_title"], result["generation_time"]
                )

            return result

        except Exception as e:
            raise Exception(f"Failed to generate HTML report: {str(e)}")

    def _prepare_report_data(
        self, analysis_data: Dict[str, Any], custom_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Prepare and format data for template rendering.

        Args:
            analysis_data: Raw analysis data from agents
            custom_title: Custom report title

        Returns:
            Formatted data dictionary for template
        """
        report_data = {
            "generation_time": datetime.now().strftime("%Y年%m月%d日 %H:%M:%S"),
            "report_title": custom_title
            or analysis_data.get("title", "データ分析レポート"),
            "analysis_target": analysis_data.get("target", "不明"),
        }

        # Extract request information
        if "interpreted_request" in analysis_data:
            report_data["request_summary"] = analysis_data["interpreted_request"]

        # Extract schema information
        if "schema_info" in analysis_data:
            report_data["schema_info"] = analysis_data["schema_info"]

        # Extract SQL query
        if "sql_query_info" in analysis_data:
            sql_info = analysis_data["sql_query_info"]
            if isinstance(sql_info, dict) and "query" in sql_info:
                report_data["sql_query"] = sql_info["query"]
            elif isinstance(sql_info, str):
                # Try to extract SQL from string content
                report_data["sql_query"] = self._extract_sql_from_text(sql_info)

        # Process query results
        if "query_execution_result" in analysis_data:
            query_result = analysis_data["query_execution_result"]
            report_data["data_table"] = self._format_query_results(query_result)
            report_data["summary_stats"] = self._generate_summary_stats(query_result)

        # Extract analysis insights
        if "analysis_results" in analysis_data:
            insights = analysis_data["analysis_results"]
            report_data["insights"] = self._format_insights(insights)

        # Add recommendations if available
        if "recommendations" in analysis_data:
            report_data["recommendations"] = self._format_recommendations(
                analysis_data["recommendations"]
            )

        return report_data

    def _extract_sql_from_text(self, text: str) -> Optional[str]:
        """Extract SQL query from text content."""
        lines = text.split("\n")
        sql_lines = []
        in_sql = False

        for line in lines:
            line = line.strip()
            if line.upper().startswith(
                ("SELECT", "WITH", "INSERT", "UPDATE", "DELETE")
            ):
                in_sql = True
                sql_lines.append(line)
            elif in_sql and (line.endswith(";") or line == ""):
                if line.endswith(";"):
                    sql_lines.append(line)
                break
            elif in_sql:
                sql_lines.append(line)

        return "\n".join(sql_lines) if sql_lines else None

    def _format_query_results(self, query_result: Any) -> Dict[str, Any]:
        """Format query results for table display."""
        if isinstance(query_result, str):
            # Try to parse as JSON or extract tabular data
            return self._parse_text_results(query_result)

        if isinstance(query_result, dict) and "data" in query_result:
            data = query_result["data"]
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict):
                    # List of dictionaries
                    headers = list(data[0].keys())
                    rows = [[str(row.get(col, "")) for col in headers] for row in data]
                    return {"headers": headers, "rows": rows}
                elif isinstance(data[0], (list, tuple)):
                    # List of lists/tuples
                    headers = [f"Column {i+1}" for i in range(len(data[0]))]
                    rows = [[str(cell) for cell in row] for row in data]
                    return {"headers": headers, "rows": rows}

        return {"headers": [], "rows": []}

    def _parse_text_results(self, text: str) -> Dict[str, Any]:
        """Parse text-based query results."""
        lines = text.strip().split("\n")
        if len(lines) < 2:
            return {"headers": [], "rows": []}

        # Look for table-like structure
        headers = []
        rows = []

        for line in lines:
            line = line.strip()
            if "|" in line and not line.startswith("|--"):
                parts = [part.strip() for part in line.split("|")]
                if parts[0] == "":
                    parts = parts[1:]
                if parts[-1] == "":
                    parts = parts[:-1]

                if not headers:
                    headers = parts
                else:
                    rows.append(parts)

        return {"headers": headers, "rows": rows}

    def _generate_summary_stats(self, query_result: Any) -> List[Dict[str, str]]:
        """Generate summary statistics from query results."""
        stats = []

        if isinstance(query_result, dict) and "data" in query_result:
            data = query_result["data"]
            if isinstance(data, list):
                stats.append({"value": str(len(data)), "label": "データ件数"})

                # Try to extract numeric columns for additional stats
                if len(data) > 0 and isinstance(data[0], dict):
                    numeric_cols = []
                    for key, value in data[0].items():
                        try:
                            float(value)
                            numeric_cols.append(key)
                        except (ValueError, TypeError):
                            continue

                    for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                        values = []
                        for row in data:
                            try:
                                values.append(float(row.get(col, 0)))
                            except (ValueError, TypeError):
                                continue

                        if values:
                            avg_val = sum(values) / len(values)
                            stats.append(
                                {"value": f"{avg_val:.2f}", "label": f"{col} (平均)"}
                            )

        return stats

    def _format_insights(self, insights: str) -> str:
        """Format analysis insights for HTML display."""
        if not insights:
            return ""

        # Convert simple markdown-like formatting to HTML
        formatted = insights.replace("\n\n", "</p><p>")
        formatted = f"<p>{formatted}</p>"

        # Handle bullet points
        lines = insights.split("\n")
        if any(line.strip().startswith(("- ", "* ", "• ")) for line in lines):
            ul_items = []
            in_list = False
            current_paragraph = ""

            for line in lines:
                line = line.strip()
                if line.startswith(("- ", "* ", "• ")):
                    if current_paragraph:
                        formatted = f"<p>{current_paragraph}</p>"
                        current_paragraph = ""
                    ul_items.append(f"<li>{line[2:]}</li>")
                    in_list = True
                elif line == "" and in_list:
                    if ul_items:
                        formatted += f'<ul>{"".join(ul_items)}</ul>'
                        ul_items = []
                        in_list = False
                else:
                    current_paragraph += line + " "

            if ul_items:
                formatted += f'<ul>{"".join(ul_items)}</ul>'
            if current_paragraph:
                formatted += f"<p>{current_paragraph}</p>"

        return formatted

    def _format_recommendations(self, recommendations: Union[str, List[str]]) -> str:
        """Format recommendations for HTML display."""
        if isinstance(recommendations, list):
            items = [f"<li>{rec}</li>" for rec in recommendations]
            return f'<ul>{"".join(items)}</ul>'

        return self._format_insights(recommendations)

    def create_from_workflow_result(
        self,
        workflow_output: Dict[str, Any],
        title: Optional[str] = None,
        output_filename: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Create HTML report from ADK workflow output.

        Args:
            workflow_output: Output from the data analysis workflow
            title: Custom report title
            output_filename: Custom output filename

        Returns:
            Dictionary containing file path, link information, and metadata
        """
        # Extract relevant data from workflow steps
        analysis_data = {}

        # Map workflow outputs to report data structure
        for key, value in workflow_output.items():
            if "request" in key.lower():
                analysis_data["interpreted_request"] = value
            elif "schema" in key.lower():
                analysis_data["schema_info"] = value
            elif "sql" in key.lower():
                analysis_data["sql_query_info"] = value
            elif "query" in key.lower() and "result" in key.lower():
                analysis_data["query_execution_result"] = value
            elif "analysis" in key.lower():
                analysis_data["analysis_results"] = value

        return self.generate_report(
            analysis_data=analysis_data, title=title, output_filename=output_filename
        )


def create_html_report(
    analysis_data: Dict[str, Any],
    output_dir: str = "reports",
    title: Optional[str] = None,
    template_name: str = "basic_report.html",
) -> Dict[str, str]:
    """
    Convenience function to create an HTML report.

    Args:
        analysis_data: Analysis results and metadata
        output_dir: Directory for output files
        title: Report title
        template_name: Template to use

    Returns:
        Dictionary containing file path, link information, and metadata
    """
    generator = HTMLReportGenerator(output_dir=output_dir)
    return generator.generate_report(
        analysis_data=analysis_data, template_name=template_name, title=title
    )


# Example usage for testing
if __name__ == "__main__":
    # Example data structure
    sample_data = {
        "title": "サンプル売上分析レポート",
        "target": "2024年売上データ",
        "interpreted_request": "2024年の月別売上分析を実施し、売上傾向を把握する",
        "schema_info": "sales_dataテーブル（date, amount, product_category列を含む）を使用",
        "sql_query_info": {
            "query": """SELECT 
    DATE_TRUNC('month', date) as month,
    SUM(amount) as total_sales,
    COUNT(*) as transaction_count
FROM sales_data 
WHERE date >= '2024-01-01' 
GROUP BY DATE_TRUNC('month', date) 
ORDER BY month"""
        },
        "query_execution_result": {
            "data": [
                {
                    "month": "2024-01-01",
                    "total_sales": 1500000,
                    "transaction_count": 250,
                },
                {
                    "month": "2024-02-01",
                    "total_sales": 1750000,
                    "transaction_count": 300,
                },
                {
                    "month": "2024-03-01",
                    "total_sales": 2100000,
                    "transaction_count": 350,
                },
            ]
        },
        "analysis_results": """分析結果から以下の重要な傾向が判明しました：

• 売上は1月から3月にかけて継続的に増加傾向
• 2月に16.7%、3月に20%の成長を記録
• 取引件数も同様に増加しており、客単価は安定

この傾向から、第1四半期の事業戦略が効果的に機能している可能性があります。""",
    }

    try:
        generator = HTMLReportGenerator()
        report_result = generator.generate_report(
            analysis_data=sample_data, title="テスト用分析レポート"
        )
        print(f"サンプルレポート生成完了: {report_result['file_path']}")
        print("\n" + report_result.get("user_message", ""))
    except Exception as e:
        print(f"レポート生成エラー: {e}")
