# mcp/server/fastmcp.py


class FastMCP:
    def __init__(self):
        print("✅ FastMCP initialized.")
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator

    def run(self, transport="stdio"):
        print("📡 MCP Server running with tools:")
        for name in self.tools:
            print(f"🔧 Tool: {name}")
