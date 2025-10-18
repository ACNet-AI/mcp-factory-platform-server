"""
API Key Management Tools

Provides API Key creation, list, deletion, and statistics features.
"""

import os

import httpx

__all__ = [
    "create_api_key",
    "list_api_keys",
    "delete_api_key",
    "get_api_key_stats",
]

# Read configuration from environment variables
PLATFORM_API_BASE = os.getenv("PLATFORM_API_BASE", "http://localhost:8001")
PLATFORM_API_KEY = os.getenv("PLATFORM_API_KEY", "")
API_TIMEOUT = float(os.getenv("API_TIMEOUT", "30.0"))


def _get_headers() -> dict:
    """Get request headers (including authentication information)"""
    headers = {"Content-Type": "application/json"}
    if PLATFORM_API_KEY:
        headers["Authorization"] = PLATFORM_API_KEY
    return headers


async def create_api_key(
    name: str,
    scopes: str = "read,write",
    expires_in_days: int = 30,
    description: str = "",
) -> str:
    """Create new API Key

    Args:
        name: API Key name
        scopes: Permission scopes, comma-separated (e.g. "read,write")
        expires_in_days: Expiration days (default 30 days)
        description: Description (optional)

    Returns:
        Creation result (including API Key)

    Example:
        >>> await create_api_key("My MCP Server", "read,write", 30)
    """
    if not PLATFORM_API_KEY:
        return f"""❌ API Key Not Configured

Please configure PLATFORM_API_KEY environment variable first.

How to get:
1. Visit: {PLATFORM_API_BASE}/auth/login
2. GitHub login
3. Create first API Key at {PLATFORM_API_BASE}/auth/api-keys
4. Add API Key to .env file

Then you can manage more API Keys through this tool.
"""

    try:
        # Parse scopes string to list
        scope_list = [s.strip() for s in scopes.split(",") if s.strip()]

        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(
                f"{PLATFORM_API_BASE}/api/auth/api-keys",
                headers=_get_headers(),
                json={
                    "name": name,
                    "scopes": scope_list,
                    "expires_in_days": expires_in_days,
                    "description": description or f"Created via MCP for {name}",
                },
            )

            if response.status_code == 200:
                data = response.json()
                api_key = data.get("api_key", "N/A")
                key_id = data.get("key_id", "N/A")

                return f"""✅ API Key Created Successfully!

🔑 API Key Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Key ID: {key_id}
• Name: {name}
• API Key: {api_key}
• Scopes: {", ".join(scope_list)}
• Validity: {expires_in_days} days
• Description: {description or "None"}

⚠️  Important Notes:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Please save API Key immediately, it will only be shown once!
• Do not commit API Key to Git repository
• Save it to .env file
• Rotate API Key regularly for better security

📝 Usage Example:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Add to .env file:
PLATFORM_API_KEY={api_key}

Next Steps:
• Use list_api_keys() to view all keys
• Use get_api_key_stats() to view usage statistics
"""

            elif response.status_code == 400:
                detail = response.json().get("detail", {})
                if isinstance(detail, dict):
                    return f"""❌ API Key Creation Failed

{detail.get("message", "Request parameter error")}

Description: {detail.get("description", "Please check parameter format")}

Suggestions:
• Check if scopes are correct (supported: read, write)
• Check if expires_in_days is in valid range (1-365 days)
• Confirm name is not empty
"""
                return f"❌ Creation Failed: {detail}"

            elif response.status_code == 401:
                return f"""❌ Authentication Failed

Current API Key is invalid or expired.

Solutions:
1. Visit: {PLATFORM_API_BASE}/auth/login
2. Re-login and generate new API Key
3. Update PLATFORM_API_KEY in .env file
"""

            elif response.status_code == 403:
                return """❌ Insufficient Permissions

Current API Key does not have permission to create new keys.

Solutions:
• Use API Key with full permissions
• Or create manually on web
"""

            else:
                return f"""❌ Creation Failed

HTTP {response.status_code}: {response.text[:200]}

If problem persists, please contact technical support.
"""

    except httpx.TimeoutException:
        return f"""❌ Request Timeout

Cannot connect to platform server (timeout {API_TIMEOUT} seconds).

Solutions:
• Check network connection
• Verify PLATFORM_API_BASE is correct: {PLATFORM_API_BASE}
• Retry later
"""
    except Exception as e:
        return f"""❌ Creation Failed

Error: {e!s}

For help, use explain_authentication() to view configuration instructions.
"""


async def list_api_keys() -> str:
    """List all API Keys of current user

    Returns:
        API Keys list (hidden full keys)

    Example:
        >>> await list_api_keys()
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Please configure PLATFORM_API_KEY environment variable first.
Use explain_authentication() for configuration instructions.
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/auth/api-keys",
                headers=_get_headers(),
            )

            if response.status_code == 200:
                data = response.json()
                keys = data.get("api_keys", [])

                if not keys:
                    return """📋 API Keys List

No API Keys currently.

Create first one:
Use create_api_key("My First Key", "read,write", 30)
"""

                result = f"""📋 API Keys List

Total {len(keys)} API Keys:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

                for i, key in enumerate(keys, 1):
                    key_id = key.get("key_id", "N/A")
                    name = key.get("name", "Unnamed")
                    prefix = key.get("key_prefix", "mcp_key_")
                    scopes = key.get("scopes", [])
                    created_at = key.get("created_at", "N/A")
                    expires_at = key.get("expires_at", "Never expires")
                    is_active = key.get("is_active", False)
                    last_used = key.get("last_used_at", "Never used")

                    status = "✅ Active" if is_active else "⚠️ Disabled"

                    result += f"""{i}. {name}
   • ID: {key_id}
   • Prefix: {prefix}***
   • Status: {status}
   • Scopes: {", ".join(scopes)}
   • Created: {created_at}
   • Expires: {expires_at}
   • Last Used: {last_used}

"""

                result += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Tips:
• Use delete_api_key(key_id) to delete unnecessary keys
• Use get_api_key_stats() to view usage statistics
• Rotate API Keys regularly for better security
"""
                return result

            elif response.status_code == 401:
                return f"""❌ Authentication Failed

Current API Key is invalid or expired.

Solutions:
Visit {PLATFORM_API_BASE}/auth/login to re-login.
"""

            else:
                return f"""❌ Query Failed

HTTP {response.status_code}: {response.text[:200]}
"""

    except httpx.TimeoutException:
        return f"❌ Request Timeout ({API_TIMEOUT} seconds)\nCheck network connection."
    except Exception as e:
        return f"❌ Query Failed: {e!s}"


async def delete_api_key(key_id: str) -> str:
    """Delete specified API Key

    Args:
        key_id: API Key ID

    Returns:
        Deletion result

    Example:
        >>> await delete_api_key("key_abc123")
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Please configure PLATFORM_API_KEY environment variable first.
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.delete(
                f"{PLATFORM_API_BASE}/api/auth/api-keys/{key_id}",
                headers=_get_headers(),
            )

            if response.status_code == 200:
                return f"""✅ API Key Deleted

Key ID: {key_id}

⚠️  Note:
• All requests using this Key will fail immediately
• If deleted Key is currently in use, please update .env file immediately
• This operation cannot be recovered

Next Steps:
• Use list_api_keys() to view remaining keys
• Use create_api_key() to create new key
"""

            elif response.status_code == 404:
                return f"""❌ API Key Does Not Exist

Key ID: {key_id}

Possible Reasons:
• Incorrect Key ID
• Key already deleted
• No permission to access this Key

Use list_api_keys() to view all available Keys.
"""

            elif response.status_code == 403:
                return f"""❌ Insufficient Permissions

Cannot delete Key ID: {key_id}

Possible Reasons:
• This is another user's Key
• Current Key does not have delete permission
"""

            else:
                return f"""❌ Deletion Failed

Key ID: {key_id}
HTTP {response.status_code}: {response.text[:200]}
"""

    except httpx.TimeoutException:
        return f"❌ Request Timeout ({API_TIMEOUT} seconds)"
    except Exception as e:
        return f"❌ Deletion Failed: {e!s}"


async def get_api_key_stats() -> str:
    """Get API Key usage statistics

    Returns:
        Usage statistics information

    Example:
        >>> await get_api_key_stats()
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Please configure PLATFORM_API_KEY environment variable first.
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/auth/api-keys/stats",
                headers=_get_headers(),
            )

            if response.status_code == 200:
                data = response.json()

                total_keys = data.get("total_keys", 0)
                active_keys = data.get("active_keys", 0)
                total_requests = data.get("total_requests", 0)
                total_requests_today = data.get("requests_today", 0)
                most_used_key = data.get("most_used_key", {})

                return f"""📊 API Key Usage Statistics

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Keys: {total_keys}
• Active Keys: {active_keys}
• Total Requests: {total_requests:,}
• Today's Requests: {total_requests_today:,}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔝 Most Used Key
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{_format_most_used_key(most_used_key)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Recommendations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Review and rotate API Keys regularly
• Delete unused Keys
• Use different Keys for different applications
• Monitor abnormal request patterns

Next Steps:
• Use list_api_keys() to view all keys
• Use create_api_key() to create new key
"""

            elif response.status_code == 401:
                return f"""❌ Authentication Failed

Current API Key is invalid or expired.
Visit {PLATFORM_API_BASE}/auth/login to re-login.
"""

            else:
                return f"""❌ Query Failed

HTTP {response.status_code}: {response.text[:200]}
"""

    except httpx.TimeoutException:
        return f"❌ Request Timeout ({API_TIMEOUT} seconds)"
    except Exception as e:
        return f"❌ Query Failed: {e!s}"


def _format_most_used_key(key_data: dict) -> str:
    """Format most used Key information"""
    if not key_data:
        return "• No data available"

    name = key_data.get("name", "Unnamed")
    requests = key_data.get("request_count", 0)
    last_used = key_data.get("last_used_at", "N/A")

    return f"""• Key: {name}
• Requests: {requests:,}
• Last Used: {last_used}"""
