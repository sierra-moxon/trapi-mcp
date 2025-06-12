## TRAPI MCP
A fastmcp-based tool for writing prompts using Translator Reasoner API queries.

### Installation
You can install the package from source:

pip install -e .
Or using uv:

uv pip install -e .
Usage
You can use the CLI:

nmdc-mcp
Or import in your Python code:

```python
from trapi_mcp.main import create_mcp

mcp = create_mcp()
mcp.run()

```

### Development
Local Setup

#### Clone the repository
```bash
git clone https://github.com/username/nmdc-mcp.git
cd nmdc-mcp
```


#### Install development dependencies
```bash
uv pip install -e ".[dev]"
Running Tests
pytest
```

#### License
MIT