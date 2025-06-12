from fastmcp import FastMCP
from src.trapi_mcp.tools import trapi, normalize_nodes, name_resolver, lookup_name, trapi_status, trapi_results, submit_trapi_query

# Create the FastMCP instance at module level
mcp = FastMCP("trapi_mcp")

# Register all tools
mcp.tool(lookup_name)
mcp.tool(trapi)
mcp.tool(name_resolver)
mcp.tool(trapi_status)
mcp.tool(trapi_results)
mcp.tool(submit_trapi_query)
mcp.tool(normalize_nodes)




def main():
    """Main entry point for the application."""
    mcp.run()


if __name__ == "__main__":
    main()