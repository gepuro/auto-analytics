import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (f"Sorry, I don't have timezone information for {city}."),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    return {"status": "success", "report": report}


# PostgreSQL MCP Server接続設定
postgres_toolset = MCPToolset(
    connection_params=SseConnectionParams(url="http://localhost:5000/mcp/sse")
)


root_agent = Agent(
    name="auto_analytics_agent",
    # model="gemini-2.0-flash",
    model="gemini-2.5-flash-lite-preview-06-17",
    description=(
        "Agent to answer questions about the time and weather in a city, "
        "and perform database analysis tasks on PostgreSQL."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city, "
        "and perform database analysis tasks. You can access PostgreSQL database to retrieve user data, "
        "analyze table schemas, test database connections, and execute SQL queries. "
        "Use the appropriate tools based on the user's request - weather/time tools for weather/time queries, "
        "and database tools for data analysis tasks."
    ),
    tools=[get_weather, get_current_time, postgres_toolset],
)
