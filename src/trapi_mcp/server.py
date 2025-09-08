from fastmcp import FastMCP
from .tools import normalize_nodes, lookup_name

# Create the FastMCP instance at module level
mcp = FastMCP("trapimcp")

# Register all tools
mcp.tool(lookup_name)
mcp.tool(normalize_nodes)


def main():
    """Main entry point for the application."""
    mcp.run()


if __name__ == "__main__":
    main()
