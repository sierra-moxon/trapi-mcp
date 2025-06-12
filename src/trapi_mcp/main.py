from fastmcp import FastMCP

# Create the FastMCP instance at module level
mcp = FastMCP("trapi_mcp")

# Register all tools
mcp.tool("one_hop", "trapi")


def main():
    """Main entry point for the application."""
    mcp.run()


if __name__ == "__main__":
    main()