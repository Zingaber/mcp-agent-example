import asyncio
from mcp.server.fastmcp import FastMCP

# Create MCP instance
mcp = FastMCP()


# Register tool
@mcp.tool()
async def get_weather(location: str):
    return f"The weather in {location} is 35°C and sunny."


async def run():
    # Simulate calling the tool (like an OpenAI agent would)
    result = await mcp.tools["get_weather"]("Mumbai")
    print("🌦️ Agent response:", result)


if __name__ == "__main__":
    asyncio.run(run())
