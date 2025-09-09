from fastmcp import FastMCP
from .api_utilities import normalize_nodes, lookup_name, genetics_kp

# Create the FastMCP instance at module level
mcp = FastMCP("trapimcp")

# Register all tools
mcp.tool(lookup_name)
mcp.tool(normalize_nodes)
mcp.tool(genetics_kp)


def main():
    """Main entry point for the application."""
    mcp.run()


if __name__ == "__main__":
    main()
