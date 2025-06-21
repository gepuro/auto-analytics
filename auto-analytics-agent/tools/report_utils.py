"""
Report Utilities for Auto Analytics System

This module provides utility functions for HTML report generation,
including data processing, formatting, and integration helpers.
"""

import os
import re
import json
import csv
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import pandas as pd


class DataProcessor:
    """Utility class for processing and formatting data for reports."""
    
    @staticmethod
    def normalize_query_results(results: Any) -> Dict[str, Any]:
        """
        Normalize query results to a standard format.
        
        Args:
            results: Query results in various formats
            
        Returns:
            Normalized data dictionary with 'headers' and 'rows' keys
        """
        if isinstance(results, pd.DataFrame):
            return {
                'headers': results.columns.tolist(),
                'rows': results.values.tolist()
            }
        
        if isinstance(results, dict):
            if 'headers' in results and 'rows' in results:
                return results
            elif 'data' in results:
                return DataProcessor.normalize_query_results(results['data'])
        
        if isinstance(results, list):
            if len(results) == 0:
                return {'headers': [], 'rows': []}
            
            if isinstance(results[0], dict):
                # List of dictionaries
                headers = list(results[0].keys())
                rows = [[str(row.get(col, '')) for col in headers] for row in results]
                return {'headers': headers, 'rows': rows}
            
            if isinstance(results[0], (list, tuple)):
                # List of lists/tuples - assume first row is headers if all strings
                if all(isinstance(item, str) for item in results[0]):
                    return {'headers': results[0], 'rows': results[1:]}
                else:
                    headers = [f'Column_{i+1}' for i in range(len(results[0]))]
                    return {'headers': headers, 'rows': results}
        
        # Fallback for string or other formats
        if isinstance(results, str):
            return DataProcessor._parse_text_table(results)
        
        return {'headers': [], 'rows': []}
    
    @staticmethod
    def _parse_text_table(text: str) -> Dict[str, Any]:
        """Parse text-based table format."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return {'headers': [], 'rows': []}
        
        headers = []
        rows = []
        
        for line in lines:
            # Handle pipe-separated tables
            if '|' in line and not line.startswith('|--'):
                parts = [part.strip() for part in line.split('|')]
                # Remove empty parts at beginning/end
                while parts and parts[0] == '':
                    parts.pop(0)
                while parts and parts[-1] == '':
                    parts.pop()
                
                if not headers and parts:
                    headers = parts
                elif parts:
                    rows.append(parts)
            
            # Handle tab or space-separated tables
            elif '\t' in line or '  ' in line:
                parts = re.split(r'\s{2,}|\t', line)
                parts = [part.strip() for part in parts if part.strip()]
                
                if not headers and parts:
                    headers = parts
                elif parts:
                    rows.append(parts)
        
        return {'headers': headers, 'rows': rows}
    
    @staticmethod
    def calculate_summary_statistics(data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Calculate summary statistics from tabular data.
        
        Args:
            data: Normalized data dictionary
            
        Returns:
            List of statistic dictionaries with 'label' and 'value' keys
        """
        stats = []
        
        if not data.get('rows'):
            return stats
        
        rows = data['rows']
        headers = data.get('headers', [])
        
        # Basic count
        stats.append({
            'label': 'データ件数',
            'value': f"{len(rows):,}"
        })
        
        if not headers:
            return stats
        
        # Analyze numeric columns
        numeric_columns = []
        for col_idx, header in enumerate(headers):
            values = []
            for row in rows:
                if col_idx < len(row):
                    try:
                        val = float(str(row[col_idx]).replace(',', ''))
                        values.append(val)
                    except (ValueError, TypeError):
                        continue
            
            if len(values) > 0:
                numeric_columns.append((header, values))
        
        # Calculate statistics for numeric columns (limit to first 3)
        for header, values in numeric_columns[:3]:
            if values:
                avg_val = sum(values) / len(values)
                max_val = max(values)
                min_val = min(values)
                
                stats.extend([
                    {
                        'label': f'{header} (平均)',
                        'value': f"{avg_val:,.2f}"
                    },
                    {
                        'label': f'{header} (最大)',
                        'value': f"{max_val:,.2f}"
                    },
                    {
                        'label': f'{header} (最小)',
                        'value': f"{min_val:,.2f}"
                    }
                ])
        
        return stats
    
    @staticmethod
    def detect_data_quality_issues(data: Dict[str, Any]) -> List[str]:
        """
        Detect potential data quality issues.
        
        Args:
            data: Normalized data dictionary
            
        Returns:
            List of data quality warnings
        """
        issues = []
        
        if not data.get('rows'):
            issues.append("データが空です")
            return issues
        
        rows = data['rows']
        headers = data.get('headers', [])
        
        if not headers:
            issues.append("カラムヘッダーが不明です")
        
        # Check for missing values
        total_cells = len(rows) * len(headers) if headers else 0
        empty_cells = 0
        
        for row in rows:
            for cell in row:
                if cell is None or str(cell).strip() in ('', 'NULL', 'null', 'None'):
                    empty_cells += 1
        
        if total_cells > 0:
            missing_percentage = (empty_cells / total_cells) * 100
            if missing_percentage > 10:
                issues.append(f"欠損値が多く含まれています ({missing_percentage:.1f}%)")
            elif missing_percentage > 0:
                issues.append(f"一部欠損値が含まれています ({missing_percentage:.1f}%)")
        
        # Check for duplicate rows
        row_strings = [str(row) for row in rows]
        unique_rows = set(row_strings)
        if len(unique_rows) < len(rows):
            duplicate_count = len(rows) - len(unique_rows)
            issues.append(f"重複行が {duplicate_count} 件含まれています")
        
        # Check row consistency
        if headers:
            inconsistent_rows = [
                i for i, row in enumerate(rows) 
                if len(row) != len(headers)
            ]
            if inconsistent_rows:
                issues.append(f"列数が不一致の行があります (行番号: {inconsistent_rows[:5]})")
        
        return issues


class TextFormatter:
    """Utility class for text formatting and processing."""
    
    @staticmethod
    def format_insights_for_html(text: str) -> str:
        """
        Format analysis insights text for HTML display.
        
        Args:
            text: Raw insights text
            
        Returns:
            HTML-formatted text
        """
        if not text:
            return ""
        
        # Handle different line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Handle bullet points
            if TextFormatter._is_bullet_list(paragraph):
                formatted_paragraphs.append(TextFormatter._format_bullet_list(paragraph))
            else:
                # Regular paragraph
                formatted_paragraphs.append(f'<p>{paragraph}</p>')
        
        return '\n'.join(formatted_paragraphs)
    
    @staticmethod
    def _is_bullet_list(text: str) -> bool:
        """Check if text contains bullet points."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        bullet_lines = [
            line for line in lines 
            if line.startswith(('- ', '* ', '• ', '1. ', '2. ', '3.'))
        ]
        return len(bullet_lines) > 0
    
    @staticmethod
    def _format_bullet_list(text: str) -> str:
        """Format bullet list as HTML."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        html_lines = []
        in_list = False
        
        for line in lines:
            if line.startswith(('- ', '* ', '• ')):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                html_lines.append(f'<li>{line[2:].strip()}</li>')
            elif line.startswith(('1. ', '2. ', '3.', '4.', '5.')):
                if not in_list:
                    html_lines.append('<ol>')
                    in_list = True
                content = re.sub(r'^\d+\.\s*', '', line)
                html_lines.append(f'<li>{content}</li>')
            else:
                if in_list:
                    html_lines.append('</ul>' if html_lines[-2].startswith('<ul>') else '</ol>')
                    in_list = False
                html_lines.append(f'<p>{line}</p>')
        
        if in_list:
            html_lines.append('</ul>' if '<ul>' in html_lines else '</ol>')
        
        return '\n'.join(html_lines)
    
    @staticmethod
    def extract_sql_from_text(text: str) -> Optional[str]:
        """Extract SQL query from mixed text content."""
        if not text:
            return None
        
        # Look for SQL keywords at line start
        lines = text.split('\n')
        sql_lines = []
        capturing = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Start capturing on SQL keywords
            if not capturing and any(
                line_stripped.upper().startswith(keyword) 
                for keyword in ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE', 'CREATE']
            ):
                capturing = True
                sql_lines.append(line)
            elif capturing:
                # Stop on empty line followed by non-SQL content
                if line_stripped == '':
                    sql_lines.append(line)
                elif line_stripped.endswith(';'):
                    sql_lines.append(line)
                    break
                elif any(char in line_stripped for char in ['。', '：', 'です', 'ます']):
                    # Japanese text indicates end of SQL
                    break
                else:
                    sql_lines.append(line)
        
        if sql_lines:
            sql_text = '\n'.join(sql_lines).strip()
            # Remove trailing non-SQL text
            if '。' in sql_text:
                sql_text = sql_text.split('。')[0]
            return sql_text
        
        return None
    
    @staticmethod
    def highlight_sql_keywords(sql: str) -> str:
        """Add HTML highlighting to SQL keywords."""
        if not sql:
            return ""
        
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN',
            'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'DISTINCT', 'AS', 'ON',
            'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'INDEX',
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'
        ]
        
        highlighted = sql
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            replacement = f'<span class="sql-keyword">{keyword}</span>'
            highlighted = re.sub(pattern, replacement, highlighted, flags=re.IGNORECASE)
        
        return highlighted


class FileUtils:
    """Utility functions for file operations."""
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """Ensure directory exists, create if necessary."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def generate_unique_filename(base_name: str, directory: Union[str, Path], extension: str = 'html') -> str:
        """Generate unique filename by adding counter if file exists."""
        directory = Path(directory)
        base_path = directory / f"{base_name}.{extension}"
        
        if not base_path.exists():
            return base_path.name
        
        counter = 1
        while True:
            new_name = f"{base_name}_{counter}.{extension}"
            new_path = directory / new_name
            if not new_path.exists():
                return new_name
            counter += 1
    
    @staticmethod
    def save_data_as_csv(data: Dict[str, Any], filepath: Union[str, Path]) -> None:
        """Save tabular data as CSV file."""
        filepath = Path(filepath)
        
        headers = data.get('headers', [])
        rows = data.get('rows', [])
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if headers:
                writer.writerow(headers)
            writer.writerows(rows)
    
    @staticmethod
    def read_template_file(template_path: Union[str, Path]) -> str:
        """Read template file content."""
        template_path = Path(template_path)
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()


class ValidationUtils:
    """Utility functions for data validation."""
    
    @staticmethod
    def validate_report_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate report data structure.
        
        Args:
            data: Report data dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required fields
        required_fields = ['report_title']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Required field missing: {field}")
        
        # Validate data_table structure if present
        if 'data_table' in data and data['data_table']:
            table_data = data['data_table']
            if not isinstance(table_data, dict):
                errors.append("data_table must be a dictionary")
            else:
                if 'headers' in table_data and not isinstance(table_data['headers'], list):
                    errors.append("data_table.headers must be a list")
                if 'rows' in table_data and not isinstance(table_data['rows'], list):
                    errors.append("data_table.rows must be a list")
        
        # Validate summary_stats structure if present
        if 'summary_stats' in data and data['summary_stats']:
            stats = data['summary_stats']
            if not isinstance(stats, list):
                errors.append("summary_stats must be a list")
            else:
                for i, stat in enumerate(stats):
                    if not isinstance(stat, dict):
                        errors.append(f"summary_stats[{i}] must be a dictionary")
                    elif 'label' not in stat or 'value' not in stat:
                        errors.append(f"summary_stats[{i}] must have 'label' and 'value' keys")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_html_content(content: str) -> str:
        """Basic HTML sanitization for user content."""
        if not content:
            return ""
        
        # Remove potentially dangerous tags
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input']
        for tag in dangerous_tags:
            content = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', content, flags=re.IGNORECASE | re.DOTALL)
            content = re.sub(f'<{tag}[^>]*/?>', '', content, flags=re.IGNORECASE)
        
        return content


def create_sample_report_data() -> Dict[str, Any]:
    """Create sample report data for testing purposes."""
    return {
        'report_title': 'サンプル分析レポート',
        'generation_time': datetime.now().strftime("%Y年%m月%d日 %H:%M:%S"),
        'analysis_target': 'テストデータセット',
        'request_summary': 'サンプルデータの分析を実行し、基本統計情報を取得する',
        'schema_info': 'test_table (id: integer, name: varchar, value: numeric)',
        'sql_query': 'SELECT name, AVG(value) as avg_value FROM test_table GROUP BY name ORDER BY avg_value DESC',
        'data_table': {
            'headers': ['商品名', '平均売上', '件数'],
            'rows': [
                ['商品A', '150,000', '25'],
                ['商品B', '120,000', '18'],
                ['商品C', '90,000', '12']
            ]
        },
        'summary_stats': [
            {'label': 'データ件数', 'value': '3'},
            {'label': '平均売上 (平均)', 'value': '120,000'},
            {'label': '総売上', 'value': '360,000'}
        ],
        'insights': '''分析結果から以下の知見が得られました：

• 商品Aが最も高い平均売上を記録
• 件数と売上に正の相関が見られる
• 全体的に安定した売上パフォーマンス

今後は商品Aの成功要因を他商品にも展開することを推奨します。'''
    }


# Export commonly used functions
__all__ = [
    'DataProcessor',
    'TextFormatter', 
    'FileUtils',
    'ValidationUtils',
    'create_sample_report_data'
]