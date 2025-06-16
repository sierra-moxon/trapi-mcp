# TRAPI MCP

A FastMCP-based tool for writing prompts using Translator Reasoner API (TRAPI) queries. 
This package enables easy integration of biomedical knowledge graph queries into your 
LLM workflows.

## Installation

You can install the package from source:

```bash
pip install -e .
```

Or using uv (recommended):

```bash
uv install trapi-mcp
```

### Python API

```python
from trapi_mcp.tools import trapi, trapi_status, trapi_results

# Submit a TRAPI query
response = trapi(
    subject="MONDO:0005148",  # Alzheimer's disease
    object_="CHEBI:6801",     # Acetylcholine
    predicate="biolink:affects"
)

# Get the query ID
pk = response["pk"]

# Check status
status_response = trapi_status(pk)
print(f"Query status: {status_response.get('status')}")

# When status is "Done", get results
if status_response.get("status") == "Done":
    results = trapi_results(pk)
    # Process results
```

## Developer Guide

### Setup Development Environment

1. Clone the repository:

```bash
git clone https://github.com/your-username/trapi-mcp.git
cd trapi-mcp
```

2. Install development dependencies:

```bash
uv install
```

### Architecture

The package consists of several key components:

- `api_utilities.py`: Low-level functions for interacting with Translator API services - e.g., how to make API calls
- `tools.py`: High-level functions for building and executing TRAPI queries.  Currently, NameResolver, NodeNormalizer, 
and ARS query endpoints are all callable as MCP servers from this repository.
- `main.py`: FastMCP integration and CLI setup

## Integration with Goose (Example)

[Goose](https://github.com/GSK-AI/goose) is a framework for building LLM applications. 
Here's how to integrate TRAPI MCP with Goose:

#### install goose:
https://block.github.io/goose/docs/getting-started/installation/

#### Set an LLM Provider
https://block.github.io/goose/docs/getting-started/installation/#set-llm-provider

#### Add TRAPI MCP as an extenstion

https://block.github.io/goose/docs/getting-started/using-extensions#adding-extensions

- Under "Advanced Settings"
  - "Add custom extension"
  - Name the extension "TRAPI MCP"
  - For "Command", add "uvx trapi-mcp"
  - "Save Changes"
  - Turn "on" the extension for your session.
  - Ask questions of goose like:
  - ```text
    What is the relationship between Alzheimer's disease and acetylcholine?
    ```
  - ```text
    How many disesaes is ABCA1 related to?
    ```
  - ```text
    What treats diabetes mellitus?
    ```
