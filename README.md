# mcp-factory-platform-server

**MCP Factory Platform Server** - AI Agent interface layer for platform management functions

Converts the mcp-factory-platform backend REST API into MCP tools, enabling AI Agents (such as Claude) to manage users, wallets, billing and other platform functions through natural language conversation.

## 🌟 Features

### 🔐 Authentication Management (6 tools)
- `get_oauth_login_url()` - Get OAuth login URL
- `explain_authentication()` - Detailed authentication configuration instructions
- `create_api_key()` - Create new API Key ⭐ NEW
- `list_api_keys()` - List all API Keys ⭐ NEW
- `delete_api_key()` - Delete API Key ⭐ NEW
- `get_api_key_stats()` - Get API Key usage statistics ⭐ NEW

### 👤 User Management (4 tools)
- `get_user_profile()` - Get user profile
- `update_user_profile()` - Update user profile
- `get_user_account()` - Get account summary
- `get_user_analytics()` - User revenue analytics

### 🖥️ MCP Service Management (5 tools) ⭐ NEW
- `register_mcp_service()` - Register new MCP service ⭐ NEW
- `list_my_services()` - List all my services ⭐ NEW
- `update_mcp_service()` - Update service information ⭐ NEW
- `delete_mcp_service()` - Delete service ⭐ NEW
- `get_service_revenue()` - View service revenue statistics ⭐ NEW

### 💰 Wallet Management (5 tools)
- `get_consumer_wallet()` - Get consumer wallet details
- `get_provider_wallet()` - Get provider wallet details
- `create_charge()` - Create charge order
- `transfer_credits()` - Transfer credits between users
- `get_transactions()` - Get transaction records

### 💸 Withdrawal Management (3 tools) ⭐ NEW
- `request_withdrawal()` - Request withdrawal ⭐ NEW
- `list_withdrawals()` - List withdrawal records ⭐ NEW
- `get_withdrawal_detail()` - View withdrawal details ⭐ NEW

### 📊 Billing Management (5 tools)
- `consume_service()` - Consume service and bill
- `list_services()` - List available MCP services
- `get_service_endpoint()` - Get service endpoint details
- `check_server_balance()` - Check server balance
- `get_server_analytics()` - Get server usage analytics

### 🔧 Platform Tools (1 tool)
- `test_platform_connection()` - Test platform connection

**Total: 28 MCP Tools** ✨ **Complete bilateral market closed loop!**

## 🚀 Quick Start

### Prerequisites

- Python >= 3.10
- `mcp-factory-platform` backend service (Production: https://mcp-factory-beta.up.railway.app)

### Step 1: OAuth Login and Get API Key

1. **Visit login page**
   ```
   https://mcp-factory-beta.up.railway.app/auth/login
   ```

2. **Authorize with GitHub account**
   - Automatically receive 1000 Beta credits after authorization

3. **Generate API Key**
   - Visit: https://mcp-factory-beta.up.railway.app/auth/api-keys
   - Click "Create API Key"
   - Configuration example:
     * Name: "My MCP Server"
     * Scopes: ["read", "write"]
     * Expires: 30 days

4. **Copy generated API Key**
   - Format: `mcp_key_xxxxxxxxxxxxxxxxx`

### Step 2: Configure Environment Variables

```bash
# 1. Copy environment configuration template
cp env.example .env

# 2. Edit .env file
nano .env
```

Add the following content:

```env
# Platform backend address (production)
PLATFORM_API_BASE=https://mcp-factory-beta.up.railway.app

# API authentication key (obtained from platform)
PLATFORM_API_KEY=mcp_key_your_api_key_here

# API timeout
API_TIMEOUT=30.0
```

### Step 3: Install Dependencies and Start

```bash
# Install dependencies
uv sync

# Test server
uv run python server.py
```

## 📋 Cursor/Claude Desktop Configuration

### Cursor Configuration

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mcp-factory-platform-server": {
      "command": "/absolute/path/to/project/.venv/bin/python",
      "args": ["/absolute/path/to/project/server.py"],
      "cwd": "/absolute/path/to/mcp-factory-platform-server"
    }
  }
}
```

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

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

## 💡 Usage Examples

### Authentication and Connection Test

```
You: "Test platform connection"
Claude: 
✅ Platform connection test successful
Health status: healthy
Service: mcp-factory-platform-foundation-early-access
Version: 0.9.0
```

### User Profile Query

```
You: "Get my user profile"
Claude: Calling get_user_profile() ...
```

### Wallet Balance Query

```
You: "Check my wallet balance"
Claude: Calling get_consumer_wallet() and get_provider_wallet() ...
```

### Service List

```
You: "What MCP services are available"
Claude: Calling list_services() ...
```

## 🏗️ Project Structure

```
mcp-factory-platform-server/
├── Dockerfile                    # Docker image configuration
├── .dockerignore                 # Docker build exclusions
├── docker-compose.yml            # Docker Compose orchestration
├── config.yaml                   # Server configuration
├── pyproject.toml                # Python project configuration
├── server.py                     # Server entry file
├── .env                          # Environment configuration (need to create)
├── env.example                   # Environment configuration example
├── README.md                     # This document
├── CHANGELOG.md                  # Version changelog
├── tools/                        # Tools implementation directory
│   ├── auth_management.py        # Authentication management tools (2)
│   ├── api_key_management.py     # API Key management tools (4)
│   ├── user_management.py        # User management tools (4)
│   ├── service_management.py     # MCP service management tools (5)
│   ├── wallet_management.py      # Wallet management tools (5)
│   ├── withdrawal_management.py  # Withdrawal management tools (3)
│   ├── billing_management.py     # Billing management tools (5)
│   └── platform_api_adapter.py   # Platform API adapter
├── resources/                    # Resources implementation directory
└── prompts/                      # Prompt template directory
```

## 🔧 Development

### Adding New Tools

1. Create a new file or edit existing file in `tools/` directory
2. Define tools using `@server.tool()` decorator
3. Call platform API using `httpx`
4. Add `Authorization` header for authentication

Example:

```python
import httpx
import os

PLATFORM_API_BASE = os.getenv("PLATFORM_API_BASE", "http://localhost:8001")
PLATFORM_API_KEY = os.getenv("PLATFORM_API_KEY", "")

def _get_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if PLATFORM_API_KEY:
        headers["Authorization"] = PLATFORM_API_KEY
    return headers

async def my_new_tool(param: str) -> str:
    """Tool description"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{PLATFORM_API_BASE}/api/endpoint",
            headers=_get_headers()
        )
        if response.status_code == 200:
            return f"Success: {response.json()}"
        return f"Failed: HTTP {response.status_code}"
```

### Code Quality Check

```bash
# Ruff check
uv run ruff check .

# Auto-fix
uv run ruff check --fix .

# Format
uv run ruff format .
```

## 🐳 Docker Deployment

### Docker Compose (Recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Docker Direct Run

```bash
# Build image
docker build -t mcp-factory-platform-server .

# Run container
docker run -d \
  --name mcp-platform-server \
  --env-file .env \
  mcp-factory-platform-server
```

## 🔐 Authentication Instructions

### OAuth Flow

1. User visits `/auth/login` in browser
2. Redirects to GitHub OAuth authorization page
3. After user authorization, platform creates account and grants 1000 Beta credits
4. User generates API Key on platform management page

### API Key Usage

All MCP tools require API Key authentication:

- Configure `PLATFORM_API_KEY` in `.env` file
- API Key format: `mcp_key_xxx`
- Restart MCP server to take effect

### Beta Version Limitations

- ✅ Available: All query and read functions
- ✅ Available: Use platform's 1000 complimentary credits
- ⚠️ Limited: Recharge function (not available in Beta)
- ⚠️ Limited: Withdrawal function (not available in Beta)

## 📚 Related Resources

- **Platform Backend**: [mcp-factory-platform](https://github.com/your-org/mcp-factory-platform)
- **Factory Framework**: [mcp-factory](https://github.com/your-org/mcp-factory)
- **API Documentation**: https://mcp-factory-beta.up.railway.app/docs
- **Beta Guide**: https://mcp-factory-beta.up.railway.app/beta-guide

## 🆘 Troubleshooting

### Issue: Tools show "API Key not configured"

**Solution:**
1. Ensure `.env` file is created
2. Check if `PLATFORM_API_KEY` is correctly filled in
3. Restart MCP server

### Issue: Connection failed HTTP 502

**Solution:**
1. Check if `PLATFORM_API_BASE` is correct
2. Confirm platform backend is running
3. Check network connection

### Issue: All requests return 403

**Solution:**
1. API Key may have expired or been revoked
2. Regenerate API Key
3. Update `.env` file and restart

### Getting Help

Use MCP tools to view help:
- `explain_authentication()` - Detailed authentication instructions
- `test_platform_connection()` - Test connection
- `platform_status()` - View platform status

## 📄 License

MIT License

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.

---

**Version**: 1.3.0  
**Last Updated**: 2025-10-18  
**Author**: MCP Factory Team

## ✨ v1.3.0 Feature Highlights

### Complete Bilateral Market Support

Now `mcp-factory-platform-server` supports complete bilateral market business processes:

**Service Provider Workflow:**
```
Register Service → Set Pricing → Earn Revenue → Request Withdrawal
```

**Service Consumer Workflow:**
```
Browse Services → Recharge Wallet → Consume Services → View Transactions
```

### Core New Features

1. **🔑 Self-service API Key Management** - No need to depend on web pages, AI Agent can directly create and manage API Keys
2. **🖥️ MCP Service Registration** - Service providers can register and manage their own MCP services through AI Agent
3. **💸 Withdrawal Function** - Service providers can withdraw earnings to bank account/Alipay/WeChat

These features complete the platform's core business loop, making `mcp-factory-platform` a true bilateral market platform!
