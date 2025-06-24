from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

postgres_toolset = MCPToolset(
    connection_params=SseConnectionParams(url="http://localhost:5000/mcp/sse")
)
