"""
Simplified Link Generator for Auto Analytics System

This module provides basic file:// URL generation for HTML reports
without any HTTP server dependencies. This is for the decoupled
AI agent that only generates reports.
"""

import platform
from pathlib import Path
from typing import Dict, Optional, Union
from urllib.parse import quote


class SimpleReportLinkGenerator:
    """
    Simple generator for creating file:// links to HTML reports.

    This class only handles file:// URLs and does not start any HTTP servers.
    It's designed for the decoupled AI agent that only generates reports.
    """

    def __init__(self):
        """Initialize the simple link generator."""
        self.platform = platform.system().lower()

    def generate_file_url(self, file_path: Union[str, Path]) -> str:
        """
        Generate a file:// URL for the given file path.

        Args:
            file_path: Path to the HTML report file

        Returns:
            Properly formatted file:// URL
        """
        file_path = Path(file_path).resolve()

        # Convert path to string and handle platform differences
        path_str = str(file_path)

        if self.platform == "windows":
            # Windows: file:///C:/path/to/file.html
            # Replace backslashes with forward slashes
            path_str = path_str.replace("\\", "/")
            # Ensure we have the right number of slashes
            if path_str.startswith("/"):
                file_url = f"file://{path_str}"
            else:
                file_url = f"file:///{path_str}"
        else:
            # Unix-like systems: file:///path/to/file.html
            file_url = f"file://{path_str}"

        # URL encode any special characters
        return self._encode_file_url(file_url)

    def _encode_file_url(self, url: str) -> str:
        """
        Properly encode file URL while preserving the file:// protocol.

        Args:
            url: Raw file URL

        Returns:
            Properly encoded file URL
        """
        if url.startswith("file://"):
            protocol = "file://"
            path_part = url[7:]  # Remove file://

            # Split path into components and encode each
            if self.platform == "windows" and path_part.startswith("/"):
                # Windows absolute path
                drive_and_path = path_part[1:]  # Remove leading slash
                if ":" in drive_and_path:
                    drive, remaining_path = drive_and_path.split(":", 1)
                    encoded_path = f"/{drive}:" + quote(remaining_path, safe="/")
                else:
                    encoded_path = "/" + quote(drive_and_path, safe="/")
            else:
                # Unix path or relative path
                encoded_path = quote(path_part, safe="/")

            return protocol + encoded_path

        return url

    def _get_file_size(self, file_path: Path) -> str:
        """
        Get human-readable file size.

        Args:
            file_path: Path to the file

        Returns:
            Human-readable file size string
        """
        try:
            size_bytes = file_path.stat().st_size

            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except (OSError, FileNotFoundError):
            return "不明"

    def generate_report_summary(
        self,
        file_path: Union[str, Path],
        report_title: Optional[str] = None,
        generation_time: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Generate a simple report summary with basic info and file:// URL.

        Args:
            file_path: Path to the HTML report file
            report_title: Title of the report
            generation_time: When the report was generated

        Returns:
            Dictionary containing report metadata and file URL
        """
        file_path = Path(file_path)

        # Check if file exists
        file_exists = file_path.exists()
        file_size = self._get_file_size(file_path) if file_exists else "不明"

        # Get file URL
        file_url = self.generate_file_url(file_path)

        summary = {
            "file_path": str(file_path),
            "file_url": file_url,
            "file_exists": file_exists,
            "file_size": file_size,
            "report_title": report_title or file_path.stem,
            "generation_time": generation_time or "不明",
            "filename": file_path.name,
        }

        return summary

    def format_user_message(
        self,
        file_path: Union[str, Path],
        report_title: Optional[str] = None,
        generation_time: Optional[str] = None,
    ) -> str:
        """
        Format a user-friendly message with report information.

        Args:
            file_path: Path to the HTML report file
            report_title: Title of the report
            generation_time: When the report was generated

        Returns:
            Formatted message string
        """
        summary = self.generate_report_summary(file_path, report_title, generation_time)

        # FastAPI server information
        fastapi_url = f"http://127.0.0.1:9000/reports/{summary['filename']}"
        fastapi_base = "http://127.0.0.1:9000/"

        message = f"""📊 データ分析レポートが完成しました！

レポートタイトル: {summary['report_title']}
生成日時: {summary['generation_time']}
ファイルサイズ: {summary['file_size']}
保存場所: {summary['file_path']}

🔗 レポートを表示する方法:

1. 🌐 FastAPIサーバー経由 (推奨):
   レポート: {fastapi_url}
   レポート一覧: {fastapi_base}
   
   ※ FastAPIサーバーが起動していない場合は、以下のコマンドで起動してください:
   cd fastapi-server && python main.py

2. 📁 ローカルファイル:
   {summary['file_url']}
   
   ※ ブラウザでファイルを開くには、リンクをコピーしてアドレスバーに貼り付けてください。

FastAPIサーバーを使用すると、レポートの一覧表示、削除、API機能などが利用できます。"""

        if not summary["file_exists"]:
            message += "\n\n⚠️ 警告: レポートファイルが見つかりません。"

        return message
