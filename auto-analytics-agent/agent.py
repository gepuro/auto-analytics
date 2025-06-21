from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from .workflow import data_analysis_workflow

# PostgreSQL MCP Server接続設定（バックアップ用）
postgres_toolset = MCPToolset(
    connection_params=SseConnectionParams(url="http://localhost:5000/mcp/sse")
)

# メインエージェント - シーケンシャルワークフローを使用
root_agent = data_analysis_workflow
