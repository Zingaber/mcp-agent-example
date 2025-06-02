import asyncio
import os
import shutil

from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStdio

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TIME_MCP_SERVER: MCPServer = MCPServerStdio(
    name="Time Server",
    params={
        "command": "uvx",
        "args": ["mcp-server-time"],
    },
)
WEATHER_MCP_SERVER: MCPServer = MCPServerStdio(
    name="Weather Server",
    params={
        "command": "uv",
        "args": ["run", "weather_mcp.py"],
    },
)

async def run(mcp_servers: list[MCPServer] | None = None) -> None:
    if mcp_servers is None:
        mcp_servers = []
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to read the filesystem and answer questions based on those files.",
        mcp_servers=mcp_servers,
    )

    conversation_thread = []
    while True:
        message = input("\n\nEnter your next message (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break

        conversation_thread.append({"role": "user", "content": message})

        result = await Runner.run(
            starting_agent=agent, 
            input=conversation_thread,
        )
        print(result)
        conversation_thread.append({"role": "assistant", "content": result.final_output})

async def main() -> None:
    all_servers: list[MCPServer] = [TIME_MCP_SERVER, WEATHER_MCP_SERVER]
    await asyncio.gather(*[server.connect() for server in all_servers])
    try:
        await run(all_servers)
    finally:
        await asyncio.gather(*[server.cleanup() for server in all_servers])

if __name__ == "__main__":
    # Let's make sure the user has npx installed
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install it with `npm install -g npx`.")

    asyncio.run(main())