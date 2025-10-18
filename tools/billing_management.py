"""Billing Management Tools - Interact with Platform Backend API"""

import os

import httpx

__all__ = [
    "consume_service",
    "list_services",
    "get_service_endpoint",
    "check_server_balance",
    "get_server_analytics",
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


async def consume_service(
    user_id: str,
    service_id: str,
    usage_amount: float = 1.0,
    usage_type: str = "request",
) -> str:
    """Consume service and record usage

    Args:
        user_id: User ID
        service_id: Service ID
        usage_amount: Usage amount
        usage_type: Usage type (request/tokens/minutes)

    Returns:
        Consumption result
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(
                f"{PLATFORM_API_BASE}/api/services/consume",
                headers=_get_headers(),
                json={
                    "user_id": user_id,
                    "service_id": service_id,
                    "usage_amount": usage_amount,
                    "usage_type": usage_type,
                },
            )

            if response.status_code == 200:
                data = response.json()

                return f"""✅ Service Consumed Successfully

Service Information:
- Service ID: {service_id}
- Usage: {usage_amount} {usage_type}
- Cost: {data.get("cost", 0)} credits

Account Balance:
- Remaining Balance: {data.get("remaining_balance", 0)} credits

Billing Details:
- Unit Price: {data.get("unit_price", 0)} credits/{usage_type}
- Service Provider: {data.get("provider_id", "N/A")}
- Platform Fee: {data.get("platform_fee", 0)} credits

Next Steps:
- Use get_consumer_wallet() to view balance details
- Use get_transactions() to view consumption records
"""

            elif response.status_code == 402:
                return """❌ Insufficient Balance

Current balance is insufficient to pay for this service consumption.

Solutions:
1. Use get_consumer_wallet() to check current balance
2. Beta users can contact platform for test credits
3. In production, use create_charge() to add credits
"""

            elif response.status_code == 404:
                return f"❌ Service Not Found: {service_id}\nUse list_services() to view available services"

            else:
                return f"❌ Service Consumption Failed: HTTP {response.status_code} - {response.text}"

    except Exception as e:
        return f"❌ Service Consumption Failed: {str(e)}"


async def list_services(limit: int = 20, category: str = "all") -> str:
    """List available MCP services

    Args:
        limit: Return count limit
        category: Service category (all/ai/dev/data/...)

    Returns:
        Service list
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/services",
                headers=_get_headers(),
                params={"limit": limit, "category": category},
            )

            if response.status_code == 200:
                data = response.json()
                services = data.get("services", [])

                if not services:
                    return f"📋 No Available Services (category: {category})"

                result = f"""📋 Available Services List ({len(services)} services)

"""

                for i, service in enumerate(services, 1):
                    result += f"""{i}. {service.get("name", "N/A")}
   ID: {service.get("server_id", "N/A")}
   Provider: {service.get("provider_name", "N/A")}
   Pricing: {service.get("pricing", "N/A")}
   Status: {service.get("status", "N/A")}
   Description: {service.get("description", "N/A")[:60]}...

"""

                result += f"""
Total: {len(services)} services

Next Steps:
- Use get_service_endpoint() to get service details
- Use consume_service() to call service
"""

                return result

            else:
                return f"❌ Failed to Retrieve Service List: HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Failed to Retrieve Service List: {str(e)}"


async def get_service_endpoint(service_id: str) -> str:
    """Get service endpoint information

    Args:
        service_id: Service ID

    Returns:
        Service endpoint details
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/services/{service_id}/endpoint",
                headers=_get_headers(),
            )

            if response.status_code == 200:
                data = response.json()

                return f"""✅ Service Endpoint Information

Basic Information:
- Service ID: {service_id}
- Service Name: {data.get("name", "N/A")}
- Provider: {data.get("provider_name", "N/A")}

Connection Information:
- Endpoint Type: {data.get("endpoint_type", "N/A")}
- Transport Protocol: {data.get("transport", "N/A")}
- Endpoint URL: {data.get("endpoint_url", "N/A")}

Billing Information:
- Pricing Model: {data.get("pricing_model", "N/A")}
- Unit Price: {data.get("unit_price", 0)} credits
- Billing Unit: {data.get("billing_unit", "N/A")}

Status:
- Service Status: {data.get("status", "N/A")}
- Availability: {data.get("availability", "N/A")}%

Next Steps:
- Use consume_service() to call this service
- Use get_server_analytics() to view usage statistics
"""

            elif response.status_code == 404:
                return f"❌ Service Not Found: {service_id}"

            else:
                return f"❌ Failed to Retrieve Service Endpoint: HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Failed to Retrieve Service Endpoint: {str(e)}"


async def check_server_balance(
    server_id: str, required_amount: float | None = None
) -> str:
    """Check if server balance is sufficient

    Args:
        server_id: Server ID
        required_amount: Required amount (optional)

    Returns:
        Balance check result
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            payload = {"server_id": server_id}
            if required_amount is not None:
                payload["required_amount"] = required_amount

            response = await client.post(
                f"{PLATFORM_API_BASE}/api/servers/check-balance",
                headers=_get_headers(),
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()

                sufficient = data.get("sufficient", False)
                status_icon = "✅" if sufficient else "⚠️"

                return f"""{status_icon} Balance Check Result

Server Information:
- Server ID: {server_id}
- Current Balance: {data.get("balance", 0)} credits

Check Result:
- Required Amount: {required_amount or "Not specified"} credits
- Balance Sufficient: {"Yes" if sufficient else "No"}

{_get_balance_warning(sufficient, data)}

Next Steps:
- Use create_charge() to add credits if insufficient
- Use get_server_analytics() to view consumption trends
"""

            elif response.status_code == 404:
                return f"❌ Server Not Found: {server_id}"

            else:
                return f"❌ Balance Check Failed: HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Balance Check Failed: {str(e)}"


async def get_server_analytics(server_id: str, period: str = "30d") -> str:
    """Get server usage analytics

    Args:
        server_id: Server ID
        period: Analysis period (7d/30d/90d/365d)

    Returns:
        Usage analytics data
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/servers/{server_id}/analytics",
                headers=_get_headers(),
                params={"period": period},
            )

            if response.status_code == 200:
                data = response.json()

                return f"""✅ Server Analytics Report ({period})

📈 Usage Overview:
- Total Calls: {data.get("total_calls", 0)}
- Total Cost: {data.get("total_cost", 0)} credits
- Average Cost Per Call: {data.get("avg_cost_per_call", 0)} credits

👥 User Statistics:
- Active Users: {data.get("active_users", 0)}
- New Users: {data.get("new_users", 0)}

📊 Trend Analysis:
- Usage Growth: {data.get("usage_growth", 0)}%
- Revenue Growth: {data.get("revenue_growth", 0)}%
- Active Days: {data.get("active_days", 0)}

🔝 Top Features:
{_format_top_features(data.get("top_features", []))}

Next Steps:
- Adjust period parameter to view different time ranges
- Use get_user_analytics() to view user dimension analytics
"""

            elif response.status_code == 404:
                return f"❌ Server Not Found: {server_id}"

            else:
                return f"❌ Failed to Retrieve Analytics: HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Failed to Retrieve Analytics: {str(e)}"


def _get_balance_warning(sufficient: bool, data: dict) -> str:
    """Get balance warning information"""
    if sufficient:
        return """✅ Balance is sufficient, service can be used normally"""

    return """⚠️  Insufficient Balance Warning

Recommended Actions:
1. Recharge immediately to avoid service interruption
2. Optimize service usage to reduce consumption
3. Upgrade service plan for better discounts"""


def _format_top_features(features: list) -> str:
    """Format top features list"""
    if not features:
        return "  No data available"

    result = []
    for i, feature in enumerate(features[:5], 1):
        result.append(
            f"  {i}. {feature.get('name', 'Unknown')} - "
            f"{feature.get('calls', 0)} calls ({feature.get('percentage', 0)}%)"
        )

    return "\n".join(result)
