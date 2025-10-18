# Project Overview
MCP server: mcp-factory-platform-server

MCP Factory Platform Server - Agent interface for platform management

This is an MCP (Model Context Protocol) server built with mcp-factory. It provides tools, resources, and prompts accessible via the MCP protocol.

## Server Configuration
**Claude Desktop Configuration (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "mcp-factory-platform-server": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "/path/to/mcp-factory-platform-server"
    }
  }
}
```

**Direct Connection:**
```bash
# Navigate to project directory first
cd /path/to/mcp-factory-platform-server
uv run python server.py
```

> **Note**: For alternative configuration methods (different environments, authentication, etc.),
> see the [MCP Configuration Guide](https://github.com/modelcontextprotocol/docs) or consult
> your MCP client documentation.

## Dev environment tips
- Navigate to project directory: `cd workspace/projects/mcp-factory-platform-server`
- Start server: `uv run python server.py`
- Install dependencies: `uv sync`
- Format code: `uv run ruff format .`
- Check linting: `uv run ruff check .`
- Add new tools in `tools/` directory with `@server.tool()` decorator
- Tools are auto-discovered from `tools/`, `resources/`, `prompts/` directories
- Configure environment variables in `.env` file (copy from `env.example`)

## Testing instructions
- Use mcp-inspector-server tools for all testing
- Call `inspect_mcp_server` to verify server connectivity and registration
- Use `comprehensive_server_test` for complete validation of all tools
- Test individual tools with `call_mcp_tool`
- Run `uv run ruff check .` before committing - all checks must pass
- Ensure all tools have comprehensive docstrings (required for MCP)
- Test with production backend: `PLATFORM_API_BASE=https://mcp-factory-beta.up.railway.app`

## PR instructions
- Title format: `[mcp-factory-platform-server] <Description>`
- Always run `uv run ruff check .` and `uv run ruff format .` before committing
- Add or update tests for new/modified tools
- Update CHANGELOG.md with your changes
- All tool functions must return `dict[str, Any]` for MCP compatibility
- Ensure all API calls are properly error-handled

## Code Style Guidelines
- Use `uv run ruff format .` to format code (from project directory)
- Run `uv run ruff check .` before committing
- Use type hints: functions return `dict[str, Any]` for tools
- Add docstrings to all functions (required for MCP registration)
- Use direct function parameters, not Pydantic models
- Follow async/await patterns for all API calls

## Component Management
This project supports dynamic component discovery and registration:

**Adding Components:**
- Tools: Create `.py` files in `tools/` directory with functions decorated with `@server.tool()`
- Resources: Create `.py` files in `resources/` directory with functions decorated with `@server.resource()`
- Prompts: Create `.py` files in `prompts/` directory with functions decorated with `@server.prompt()`

**Component Discovery:**
- Components are automatically discovered and registered in `config.yaml`
- Use descriptive function names and comprehensive docstrings
- Ensure all parameters are JSON-serializable for MCP compatibility
- All tools should use `platform_api_adapter.py` for backend API calls
