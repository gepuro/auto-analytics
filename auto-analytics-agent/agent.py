from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

# ワークフローからルートエージェントをインポート
try:
    # カスタムエージェント（動的ワークフロー）を優先的に使用
    from .workflow import root_agent
    print("✅ Auto Analytics エージェントを正常に読み込みました")
except ImportError as e:
    print(f"❌ エージェントの読み込みに失敗: {e}")
    raise


# メインエージェント - カスタムワークフローまたはLlmAgentを使用
# workflow.pyで適切なエージェントが選択される
root_agent = root_agent
