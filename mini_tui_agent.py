import asyncio
import os
import shutil

from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStdio
from agents.result import RunResult

AGENT_MAX_TURNS = 16
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TIME_MCP_SERVER: MCPServer = MCPServerStdio(
    name="Time Server",
    params={
        "command": "uvx",
        "args": ["mcp-server-time"],
    },
)

# WEATHER_MCP_SERVER: MCPServer = MCPServerStdio(
#     name="Weather Server",
#     params={
#         "command": "uv",
#         "args": ["run", "weather_mcp.py"],
#     },
# )

# SQLITE_MCP_SERVER: MCPServer = MCPServerStdio(
#     name="SQLite Server",
#     params={
#         "command": "uvx",
#         "args": ["mcp-server-sqlite", "--db-path", "sqlite.db"],
#     },
# )

ACTIVE_MCP_SERVERS: list[MCPServer] = [
    TIME_MCP_SERVER,
]


def log_agent_response(response: RunResult) -> None:
    """Log any function calls and the final output of the agent."""
    print("\n\n")
    for item in response.raw_responses:
        for item_output in item.output:
            if item_output.type == "function_call":
                print(f"Function call: {item_output.name} {item_output.arguments}")
    print(f"\n\nAgent: {response.final_output}")


async def run(mcp_servers: list[MCPServer] | None = None) -> None:
    """Run the main agent loop."""
    if mcp_servers is None:
        mcp_servers = []

    agent = Agent(
        name="Assistant",
        instructions="""
        You are a helpful assistant.
        Use the tools available to assist the user.
        Do your best to answer the user's question.
        """,
        mcp_servers=mcp_servers,
    )

    runner_result = await Runner.run(agent, "Please introduce yourself.")
    log_agent_response(runner_result)
    conversation_thread = runner_result.to_input_list()

    while True:
        message = input("\n\nEnter your next message (or 'exit' to quit) >>> ")
        if message.lower() == "exit":
            break

        conversation_thread.append(dict(role="user", content=message))

        result = await Runner.run(
            starting_agent=agent,
            input=conversation_thread,
            max_turns=AGENT_MAX_TURNS,
        )
        log_agent_response(result)
        conversation_thread = result.to_input_list()


async def main() -> None:
    print("Starting MCP servers...")
    async with asyncio.TaskGroup() as tg:
        for server in ACTIVE_MCP_SERVERS:
            tg.create_task(server.connect())

    try:
        await run(ACTIVE_MCP_SERVERS)
    finally:
        async with asyncio.TaskGroup() as tg:
            for server in ACTIVE_MCP_SERVERS:
                tg.create_task(server.cleanup())


if __name__ == "__main__":
    # make sure npx/uvx are installed for the MCP servers
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install it with node.")
    if not shutil.which("uvx"):
        raise RuntimeError(
            "uvx is not installed. Please install it with pip install uvx."
        )

    print("Starting mini-tui agent...")
    asyncio.run(main())
