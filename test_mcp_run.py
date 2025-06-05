# test_mcp_run.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool()
async def say_hello():
    return "Hello from MCP!"


if __name__ == "__main__":
    mcp.run()
