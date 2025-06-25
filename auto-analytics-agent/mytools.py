from typing import Any, Dict, Optional

from google.adk.agents import Agent, BaseAgent, LlmAgent
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .sub_agent.data_analyzer_agent import data_analyzer_agent
from .sub_agent.data_retrieval_agent import data_retrieval_agent
from .sub_agent.html_report_agent import html_report_agent
from .sub_agent.request_interpreter_agent import request_interpreter
from .sub_agent.table_explorer_agent import table_and_sameple_explorer


async def call_data_retrieval_agent(
    question: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Tool to call data retrieval agent."""
    agent_tool = AgentTool(agent=data_retrieval_agent)
    data_retrieval_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["data_retrieval_output"] = data_retrieval_output
    return data_retrieval_output


async def call_table_explorer_agent(
    question: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Tool to call table explorer agent."""
    agent_tool = AgentTool(agent=table_and_sameple_explorer)

    table_explorer_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["table_explorer_output"] = table_explorer_output
    return table_explorer_output


async def call_request_interpreter_agent(
    question: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Tool to call request interpreter agent."""
    agent_tool = AgentTool(agent=request_interpreter)

    request_interpreter_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["request_interpreter_output"] = request_interpreter_output
    return request_interpreter_output


async def call_html_report_agent(
    question: str, tool_context: ToolContext
) -> Dict[str, Any]:
    """Tool to call HTML report generator agent."""
    agent_tool = AgentTool(agent=html_report_agent)

    html_report_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["html_report_output"] = html_report_output
    return html_report_output


async def call_data_analyzer_agent(
    question: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Tool to call data analyzer agent."""
    agent_tool = AgentTool(agent=data_analyzer_agent)

    data_analyzer_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["data_analyzer_output"] = data_analyzer_output
    return data_analyzer_output
