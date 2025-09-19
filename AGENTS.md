# Project Overview
MCP server: mcp-factory-platform-server

This is an MCP (Model Context Protocol) server built with mcp-factory. It provides tools, resources, and prompts accessible via the MCP protocol.

# # Server Configuration
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

# # Build and Test Commands
```bash
# Install dependencies
uv sync

# Run the server (always from mcp-factory root)
cd /path/to/mcp-factory
uv run python workspace/projects/mcp-factory-platform-server/server.py

# Test the server using mcp-inspector-server tools
# Call inspect_mcp_server with server_command parameter
# Call comprehensive_server_test for full validation
# Use call_mcp_tool to test individual functions
```

# # Code Style Guidelines
- Use `uv run ruff format .` to format code (from project directory)
- Run `uv run ruff check .` before committing
- Use type hints: functions return `dict[str, Any]` for tools
- Add docstrings to all functions (required for MCP registration)
- Use direct function parameters, not Pydantic models

# # Testing Instructions
- Use mcp-inspector-server tools for all testing
- Call `inspect_mcp_server` to verify server connectivity
- Use `comprehensive_server_test` for complete validation
- Test individual tools with `call_mcp_tool`
- Run `uv run ruff check .` to catch linting issues
- Always verify server starts from mcp-factory root directory

# # Security Considerations
- Validate all input parameters in tools
- Be cautious with file system access in tools
- Don't expose sensitive data through resources
- Use appropriate error handling to avoid information leakage

# # Component Management
This project supports dynamic component discovery and registration:

**Adding Components:**
- Tools: Create `.py` files in `tools/` directory with functions decorated with `@tool`
- Resources: Create `.py` files in `resources/` directory with functions decorated with `@resource`
- Prompts: Create `.py` files in `prompts/` directory with functions decorated with `@prompt`

**Component Discovery:**
- Components are automatically discovered and registered in `config.yaml`
- Use descriptive function names and comprehensive docstrings
- Ensure all parameters are JSON-serializable for MCP compatibility

# # Development Notes
- **Path requirements**: Always run server from mcp-factory root directory
- **Schema requirements**: Use `dict[str, Any]` returns, ensure JSON-serializable parameters
- **Component discovery**: Components are automatically found and registered in `config.yaml`