"""User Management Tools - Interact with Platform Backend API"""

import os

import httpx

# Exported tool function list
__all__ = [
    "get_user_profile",
    "update_user_profile",
    "get_user_account",
    "get_user_analytics",
]

# Platform backend configuration
PLATFORM_API_BASE = os.getenv("PLATFORM_API_BASE", "http://localhost:8001")
PLATFORM_API_KEY = os.getenv("PLATFORM_API_KEY", "")
API_TIMEOUT = float(os.getenv("API_TIMEOUT", "30.0"))


def _get_headers() -> dict:
    """Get authentication headers"""
    headers = {"Content-Type": "application/json"}
    if PLATFORM_API_KEY:
        headers["Authorization"] = PLATFORM_API_KEY
    return headers


async def get_user_profile(user_id: str) -> str:
    """Get user profile

    Args:
        user_id: User ID

    Returns:
        User profile information
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Please complete authentication setup:
1. Use get_oauth_login_url() to get login link
2. Generate API Key on the platform
3. Add to .env file: PLATFORM_API_KEY=mcp_key_xxx
4. Restart MCP server

Use explain_authentication() for detailed instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/profile",
                headers=_get_headers(),
            )

            if response.status_code == 200:
                data = response.json()

                return f"""✅ User Profile

Basic Information:
- User ID: {data.get("user_id", "N/A")}
- Name: {data.get("name", "N/A")}
- Email: {data.get("email", "N/A")}
- GitHub: {data.get("github_username", "N/A")}

Account Status:
- Status: {data.get("status", "N/A")}
- User Tier: {data.get("tier", "N/A")}
- Registered At: {data.get("created_at", "N/A")}

Next Steps:
- Use get_user_account() to view account details
- Use get_user_analytics() to view usage analytics
"""

            elif response.status_code == 403:
                return f"❌ Insufficient Permissions: Cannot access profile for user {user_id}"

            elif response.status_code == 404:
                return f"❌ User Not Found: {user_id}"

            else:
                return f"❌ Failed to Retrieve User Profile: HTTP {response.status_code}"

    except httpx.ConnectError:
        return f"❌ Cannot Connect to Platform: {PLATFORM_API_BASE}\nPlease check network connection and platform status"

    except httpx.TimeoutException:
        return f"❌ Request Timeout ({API_TIMEOUT} seconds)"

    except Exception as e:
        return f"❌ Failed to Retrieve User Profile: {str(e)}"


async def update_user_profile(
    user_id: str,
    name: str | None = None,
    bio: str | None = None,
    website: str | None = None,
) -> str:
    """Update user profile

    Args:
        user_id: User ID
        name: New name (optional)
        bio: Personal bio (optional)
        website: Personal website (optional)

    Returns:
        Update result
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        # Build update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if bio is not None:
            update_data["bio"] = bio
        if website is not None:
            update_data["website"] = website

        if not update_data:
            return "❌ Please provide at least one field to update (name, bio, website)"

        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.put(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/profile",
                headers=_get_headers(),
                json=update_data,
            )

            if response.status_code == 200:
                data = response.json()
                updated_fields = ", ".join(update_data.keys())

                return f"""✅ User Profile Updated Successfully

Updated Fields: {updated_fields}

Current Information:
- Name: {data.get("name", "N/A")}
- Bio: {data.get("bio", "N/A")}
- Website: {data.get("website", "N/A")}
"""

            elif response.status_code == 403:
                return f"❌ Insufficient Permissions: Cannot update profile for user {user_id}"

            elif response.status_code == 404:
                return f"❌ User Not Found: {user_id}"

            else:
                return f"❌ Update Failed: HTTP {response.status_code} - {response.text}"

    except Exception as e:
        return f"❌ Failed to Update User Profile: {str(e)}"


async def get_user_account(user_id: str) -> str:
    """Get user account summary

    Args:
        user_id: User ID

    Returns:
        Account summary information
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/account",
                headers=_get_headers(),
            )

            if response.status_code == 200:
                data = response.json()

                wallet_info = data.get("wallet", {})
                server_info = data.get("servers", {})
                stats = data.get("stats", {})

                return f"""✅ User Account Summary

💰 Wallet Information:
- Consumer Wallet Balance: {wallet_info.get("consumer_balance", 0)} credits
- Provider Wallet Balance: {wallet_info.get("provider_balance", 0)} credits
- Total Transactions: {wallet_info.get("transaction_count", 0)}

🖥️  Server Information:
- Registered Servers: {server_info.get("total_servers", 0)}
- Active Servers: {server_info.get("active_servers", 0)}

📊 Usage Statistics:
- Total Service Calls: {stats.get("total_calls", 0)}
- Monthly Spending: {stats.get("month_spending", 0)} credits
- Monthly Revenue: {stats.get("month_revenue", 0)} credits

Next Steps:
- Use get_wallet_balance() to view wallet details
- Use get_user_analytics() to view usage analytics
"""

            elif response.status_code == 403:
                return f"❌ Insufficient Permissions: Cannot access account for user {user_id}"

            elif response.status_code == 404:
                return f"❌ User Not Found: {user_id}"

            else:
                return f"❌ Failed to Retrieve Account Summary: HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Failed to Retrieve Account Summary: {str(e)}"


async def get_user_analytics(user_id: str, period: str = "30d") -> str:
    """Get user revenue analytics

    Args:
        user_id: User ID
        period: Analysis period (7d/30d/90d/365d)

    Returns:
        Revenue analytics data
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/analytics",
                headers=_get_headers(),
                params={"period": period},
            )

            if response.status_code == 200:
                data = response.json()

                return f"""✅ User Analytics Report ({period})

📈 Revenue Overview:
- Total Revenue: {data.get("total_revenue", 0)} credits
- Service Calls: {data.get("total_calls", 0)}
- Average Revenue Per Call: {data.get("avg_revenue_per_call", 0)} credits

🔝 Top Services:
{_format_top_services(data.get("top_services", []))}

📊 Trend Analysis:
- Growth Rate: {data.get("growth_rate", 0)}%
- Active Days: {data.get("active_days", 0)}

Next Steps:
- Adjust period parameter to view different time ranges
- Use get_server_analytics() to view server details
"""

            elif response.status_code == 403:
                return f"❌ Insufficient Permissions: Cannot access analytics for user {user_id}"

            elif response.status_code == 404:
                return f"❌ User Not Found: {user_id}"

            else:
                return f"❌ Failed to Retrieve Analytics: HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Failed to Retrieve Analytics: {str(e)}"


def _format_top_services(services: list) -> str:
    """Format top services list"""
    if not services:
        return "  No data available"

    result = []
    for i, service in enumerate(services[:5], 1):
        result.append(
            f"  {i}. {service.get('name', 'Unknown')} - "
            f"{service.get('revenue', 0)} credits ({service.get('calls', 0)} calls)"
        )

    return "\n".join(result)
