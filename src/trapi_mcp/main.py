from fastmcp import FastMCP
from .tools import trapi, one_hop

# Create the FastMCP instance at module level
mcp = FastMCP("trapi_mcp")

# Register all tools
mcp.tool(one_hop)
mcp.tool(trapi)


def main():
    """Main entry point for the application."""
    mcp.run()


if __name__ == "__main__":
    main()