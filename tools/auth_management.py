"""Authentication Management Tools - Handle OAuth and API Key"""

import os

__all__ = [
    "get_oauth_login_url",
    "explain_authentication",
]

# Platform backend configuration
PLATFORM_API_BASE = os.getenv("PLATFORM_API_BASE", "http://localhost:8001")
API_TIMEOUT = float(os.getenv("API_TIMEOUT", "30.0"))


async def get_oauth_login_url(redirect_uri: str | None = None) -> str:
    """Get OAuth login URL

    Args:
        redirect_uri: Redirect URI after successful login (optional)

    Returns:
        OAuth login instructions and URL
    """
    try:
        login_url = f"{PLATFORM_API_BASE}/auth/login"
        if redirect_uri:
            login_url += f"?redirect_uri={redirect_uri}"

        return f"""🔐 MCP Factory Platform Authentication

Authentication Method: GitHub OAuth Login

Login Steps:
1. Open the following URL in your browser:
   {login_url}

2. Authorize with your GitHub account

3. After successful login, create an API Key on the platform management page:
   {PLATFORM_API_BASE}/auth/api-keys

4. Add the generated API Key to your .env file:
   PLATFORM_API_KEY=mcp_key_xxxxxxxxxx

5. Restart the MCP server to use authentication features

📝 Note:
- API Key format: mcp_key_xxx
- Keep it secure and don't expose it
- You can set expiration time and permission scopes

💡 Tip:
Use explain_authentication() to view detailed authentication instructions
"""

    except Exception as e:
        return f"❌ Failed to get login URL: {str(e)}"


async def explain_authentication() -> str:
    """Detailed explanation of authentication flow and configuration"""

    return f"""🔐 MCP Factory Platform Authentication Complete Guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Authentication Methods
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ GitHub OAuth Login (Recommended)
   - Secure and convenient
   - Automatic account creation
   - Receive 1000 Beta credits

2️⃣ API Key Authentication
   - For MCP server calls
   - Requires OAuth login first
   - Configurable permissions and expiration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Quick Start
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: OAuth Login
  Visit: {PLATFORM_API_BASE}/auth/login
  Complete authorization with your GitHub account

Step 2: Generate API Key
  Visit: {PLATFORM_API_BASE}/auth/api-keys
  Click "Create API Key" button

  Configuration Example:
  - Name: "My MCP Server"
  - Description: "For Cursor MCP integration"
  - Scopes: ["read", "write"]
  - Expires: 30 days (or never expires)

Step 3: Configure Environment Variables
  Add to mcp-factory-platform-server/.env:

  ```
  PLATFORM_API_BASE={PLATFORM_API_BASE}
  PLATFORM_API_KEY=mcp_key_xxxxxxxxxxxxxxxxx
  API_TIMEOUT=30.0
  ```

Step 4: Restart MCP Server
  Reload MCP configuration in Cursor

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 API Key Usage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add Authorization header in all API requests:

```
Authorization: mcp_key_xxxxxxxxxxxxxxxxx
```

Or pass in tool calls:

```python
await get_user_profile(user_id="xxx", api_key="mcp_key_xxx")
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  Security Tips
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Do:
  - Keep API Key secure
  - Rotate keys regularly
  - Set reasonable expiration time
  - Use principle of least privilege

❌ Don't:
  - Don't commit API Key to Git
  - Don't share in public channels
  - Don't use the same Key in multiple places

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Related Documentation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- API Docs: {PLATFORM_API_BASE}/docs
- Health Check: {PLATFORM_API_BASE}/health
- Beta Guide: {PLATFORM_API_BASE}/beta-guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 Need Help?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use the following tools for more information:
- test_platform_connection() - Test platform connection
- platform_status() - Check server status
- list_platform_endpoints() - View all available APIs

"""
