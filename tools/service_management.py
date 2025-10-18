"""
MCP Service Management Tools

Provides MCP service registration, update, deletion, and revenue query features.
"""

import os

import httpx

__all__ = [
    "register_mcp_service",
    "list_my_services",
    "update_mcp_service",
    "delete_mcp_service",
    "get_service_revenue",
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


def _get_user_id_from_token() -> str:
    """Extract user ID from API Key (simplified version, should call API for verification)"""
    # Should call /api/auth/verify to get real user_id
    # Temporarily return placeholder, need to call verification endpoint in actual use
    return "current_user"


async def register_mcp_service(
    name: str,
    description: str,
    endpoint_url: str,
    pricing_model: str = "per_request",
    unit_price: float = 0.01,
) -> str:
    """Register new MCP service

    Args:
        name: Service name
        description: Service description
        endpoint_url: Service endpoint URL
        pricing_model: Pricing model (per_request/per_token/per_minute)
        unit_price: Unit price (credits)

    Returns:
        Registration result

    Example:
        >>> await register_mcp_service(
        ...     "My AI Service",
        ...     "A powerful AI service",
        ...     "https://my-service.com/mcp",
        ...     "per_request",
        ...     0.05
        ... )
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Please configure PLATFORM_API_KEY environment variable first.
Use explain_authentication() for configuration instructions.
"""

    try:
        # First verify current user
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            verify_response = await client.post(
                f"{PLATFORM_API_BASE}/api/auth/verify",
                headers=_get_headers(),
            )

            if verify_response.status_code != 200:
                return f"""❌ Authentication Failed

Current API Key is invalid or expired.
Visit {PLATFORM_API_BASE}/auth/login to re-login.
"""

            user_data = verify_response.json()
            user_id = user_data.get("user_id")

            if not user_id:
                return "❌ Cannot get user information, please re-login."

            # Register service
            response = await client.post(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/mcp-services",
                headers=_get_headers(),
                json={
                    "name": name,
                    "description": description,
                    "endpoint_url": endpoint_url,
                    "pricing": {
                        "model": pricing_model,
                        "unit_price": unit_price,
                    },
                    "status": "active",
                },
            )

            if response.status_code in (200, 201):
                data = response.json()
                service_id = data.get("server_id") or data.get("service_id", "N/A")

                return f"""✅ MCP Service Registered Successfully!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖥️  Service Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Service ID: {service_id}
• Service Name: {name}
• Description: {description}
• Endpoint URL: {endpoint_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Pricing Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Pricing Model: {pricing_model}
• Unit Price: ¥{unit_price:.4f}
• Status: Active

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Next Steps
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Your service is now discoverable and usable by other users
• Each call will be charged according to pricing
• Revenue will automatically go to your provider wallet
• Use list_my_services() to view all services
• Use get_service_revenue("{service_id}") to view revenue statistics

💡 Tips:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Ensure your service endpoint is publicly accessible
• Monitor service performance and availability regularly
• Set reasonable prices to attract users
• Respond to user feedback promptly
"""

            elif response.status_code == 400:
                detail = response.json().get("detail", "Request parameter error")
                return f"""❌ Service Registration Failed

{detail}

Common Issues:
• Check if endpoint URL is valid
• Verify pricing model is correct (per_request/per_token/per_minute)
• Check if unit price is positive
• Confirm service name is not empty
"""

            elif response.status_code == 409:
                return f"""❌ Service Already Exists

Service name "{name}" is already registered.

Solutions:
• Use a different service name
• Or use update_mcp_service() to update existing service
"""

            else:
                return f"""❌ Registration Failed

HTTP {response.status_code}: {response.text[:200]}
"""

    except httpx.TimeoutException:
        return f"❌ Request Timeout ({API_TIMEOUT} seconds)\nCheck network connection."
    except Exception as e:
        return f"❌ Registration Failed: {e!s}"


async def list_my_services() -> str:
    """List all MCP services registered by current user

    Returns:
        Service list

    Example:
        >>> await list_my_services()
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Please configure PLATFORM_API_KEY environment variable first.
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            # Verify user
            verify_response = await client.post(
                f"{PLATFORM_API_BASE}/api/auth/verify",
                headers=_get_headers(),
            )

            if verify_response.status_code != 200:
                return f"""❌ Authentication Failed

Visit {PLATFORM_API_BASE}/auth/login to re-login.
"""

            user_data = verify_response.json()
            user_id = user_data.get("user_id")

            # Get service list
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/mcp-services",
                headers=_get_headers(),
            )

            if response.status_code == 200:
                data = response.json()
                services = data.get("services", [])

                if not services:
                    return """📋 My MCP Services

No services registered currently.

Start registering your first service:
Use register_mcp_service() to register new service

Example:
register_mcp_service(
    "My AI Service",
    "A powerful AI service",
    "https://my-service.com/mcp",
    "per_request",
    0.05
)
"""

                result = f"""📋 My MCP Services

Total {len(services)} services:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

                for i, service in enumerate(services, 1):
                    service_id = service.get("server_id") or service.get(
                        "service_id", "N/A"
                    )
                    name = service.get("name", "Unnamed")
                    description = service.get("description", "No description")
                    status = service.get("status", "unknown")
                    pricing = service.get("pricing", {})
                    endpoint = service.get("endpoint_url", "N/A")
                    created_at = service.get("created_at", "N/A")

                    status_icon = (
                        "✅"
                        if status == "active"
                        else "⚠️"
                        if status == "inactive"
                        else "❌"
                    )

                    result += f"""{i}. {status_icon} {name}
   • ID: {service_id}
   • Status: {status}
   • Description: {description[:50]}{"..." if len(description) > 50 else ""}
   • Endpoint: {endpoint}
   • Pricing: ¥{pricing.get("unit_price", 0):.4f}/{pricing.get("model", "request")}
   • Created: {created_at}

"""

                result += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Actions:
• update_mcp_service(service_id, {...}) - Update service
• delete_mcp_service(service_id) - Delete service
• get_service_revenue(service_id) - View revenue
"""
                return result

            else:
                return f"""❌ Query Failed

HTTP {response.status_code}: {response.text[:200]}
"""

    except httpx.TimeoutException:
        return f"❌ Request Timeout ({API_TIMEOUT} seconds)"
    except Exception as e:
        return f"❌ Query Failed: {e!s}"


async def update_mcp_service(
    service_id: str,
    name: str | None = None,
    description: str | None = None,
    endpoint_url: str | None = None,
    unit_price: float | None = None,
    status: str | None = None,
) -> str:
    """Update MCP service information

    Args:
        service_id: Service ID
        name: New service name (optional)
        description: New description (optional)
        endpoint_url: New endpoint URL (optional)
        unit_price: New unit price (optional)
        status: New status (active/inactive) (optional)

    Returns:
        Update result

    Example:
        >>> await update_mcp_service(
        ...     "service_123",
        ...     name="Updated Service Name",
        ...     unit_price=0.08
        ... )
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Please configure PLATFORM_API_KEY environment variable first.
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            # Verify user
            verify_response = await client.post(
                f"{PLATFORM_API_BASE}/api/auth/verify",
                headers=_get_headers(),
            )

            if verify_response.status_code != 200:
                return f"""❌ Authentication Failed

Visit {PLATFORM_API_BASE}/auth/login to re-login.
"""

            user_data = verify_response.json()
            user_id = user_data.get("user_id")

            # Build update data
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            if endpoint_url is not None:
                update_data["endpoint_url"] = endpoint_url
            if unit_price is not None:
                update_data["pricing"] = {"unit_price": unit_price}
            if status is not None:
                update_data["status"] = status

            if not update_data:
                return """❌ No Update Fields Provided

Please provide at least one field to update:
• name - Service name
• description - Service description
• endpoint_url - Endpoint URL
• unit_price - Unit price
• status - Status (active/inactive)
"""

            # Update service
            response = await client.put(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/mcp-services/{service_id}",
                headers=_get_headers(),
                json=update_data,
            )

            if response.status_code == 200:
                changes = []
                if name:
                    changes.append(f"• Name → {name}")
                if description:
                    changes.append(f"• Description → {description[:50]}")
                if endpoint_url:
                    changes.append(f"• Endpoint → {endpoint_url}")
                if unit_price:
                    changes.append(f"• Unit Price → ¥{unit_price:.4f}")
                if status:
                    changes.append(f"• Status → {status}")

                changes_text = "\n".join(changes)

                return f"""✅ Service Updated Successfully!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Update Content
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service ID: {service_id}

{changes_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
• Use list_my_services() to view updated service list
• Use get_service_revenue("{service_id}") to view revenue statistics
"""

            elif response.status_code == 404:
                return f"""❌ Service Does Not Exist

Service ID: {service_id}

Possible Reasons:
• Incorrect service ID
• Service already deleted
• No permission to access this service

Use list_my_services() to view all your services.
"""

            elif response.status_code == 403:
                return f"""❌ Insufficient Permissions

Cannot update service ID: {service_id}

Possible Reasons:
• This is another user's service
• Current API Key has insufficient permissions
"""

            else:
                return f"""❌ Update Failed

HTTP {response.status_code}: {response.text[:200]}
"""

    except httpx.TimeoutException:
        return f"❌ Request Timeout ({API_TIMEOUT} seconds)"
    except Exception as e:
        return f"❌ Update Failed: {e!s}"


async def delete_mcp_service(service_id: str) -> str:
    """Delete MCP service

    Args:
        service_id: Service ID

    Returns:
        Deletion result

    Example:
        >>> await delete_mcp_service("service_123")
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Please configure PLATFORM_API_KEY environment variable first.
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            # Verify user
            verify_response = await client.post(
                f"{PLATFORM_API_BASE}/api/auth/verify",
                headers=_get_headers(),
            )

            if verify_response.status_code != 200:
                return f"""❌ Authentication Failed

Visit {PLATFORM_API_BASE}/auth/login to re-login.
"""

            user_data = verify_response.json()
            user_id = user_data.get("user_id")

            # Delete service
            response = await client.delete(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/mcp-services/{service_id}",
                headers=_get_headers(),
            )

            if response.status_code == 200:
                return f"""✅ Service Deleted

Service ID: {service_id}

⚠️  Note:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Service has been removed from platform
• Users can no longer discover or use this service
• Historical revenue records are still retained
• This operation cannot be recovered

💡 Tips:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• For temporary offline, use update_mcp_service() to change status to "inactive"
• Recommend checking revenue statistics before deletion
• Ensure no ongoing transactions

Next Steps:
• Use list_my_services() to view remaining services
• Use get_provider_wallet() to view total revenue
"""

            elif response.status_code == 404:
                return f"""❌ Service Does Not Exist

Service ID: {service_id}

Use list_my_services() to view all your services.
"""

            elif response.status_code == 403:
                return f"""❌ Insufficient Permissions

Cannot delete service ID: {service_id}

This may be another user's service.
"""

            else:
                return f"""❌ Deletion Failed

HTTP {response.status_code}: {response.text[:200]}
"""

    except httpx.TimeoutException:
        return f"❌ Request Timeout ({API_TIMEOUT} seconds)"
    except Exception as e:
        return f"❌ Deletion Failed: {e!s}"


async def get_service_revenue(service_id: str | None = None) -> str:
    """Get service revenue statistics

    Args:
        service_id: Service ID (optional, if not provided returns total revenue for all services)

    Returns:
        Revenue statistics information

    Example:
        >>> await get_service_revenue("service_123")
        >>> await get_service_revenue()  # Total revenue for all services
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Please configure PLATFORM_API_KEY environment variable first.
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            # Verify user
            verify_response = await client.post(
                f"{PLATFORM_API_BASE}/api/auth/verify",
                headers=_get_headers(),
            )

            if verify_response.status_code != 200:
                return f"""❌ Authentication Failed

Visit {PLATFORM_API_BASE}/auth/login to re-login.
"""

            user_data = verify_response.json()
            user_id = user_data.get("user_id")

            # Get service revenue
            url = f"{PLATFORM_API_BASE}/api/users/{user_id}/service-revenue"
            if service_id:
                url += f"?service_id={service_id}"

            response = await client.get(url, headers=_get_headers())

            if response.status_code == 200:
                data = response.json()

                if service_id:
                    # Single service revenue
                    service_name = data.get("service_name", "Unknown service")
                    total_revenue = data.get("total_revenue", 0)
                    total_calls = data.get("total_calls", 0)
                    avg_revenue = data.get("avg_revenue_per_call", 0)
                    period_revenue = data.get("period_revenue", {})

                    return f"""💰 Service Revenue Statistics

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖥️  Service Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Service: {service_name}
• ID: {service_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Revenue Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Revenue: ¥{total_revenue:.2f}
• Total Calls: {total_calls:,}
• Average Revenue Per Call: ¥{avg_revenue:.4f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Period Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Today: ¥{period_revenue.get("today", 0):.2f}
• This Week: ¥{period_revenue.get("week", 0):.2f}
• This Month: ¥{period_revenue.get("month", 0):.2f}

Next Steps:
• Use get_provider_wallet() to view total provider wallet
• Use request_withdrawal() to request withdrawal
"""

                else:
                    # Total revenue for all services
                    total_revenue = data.get("total_revenue", 0)
                    service_count = data.get("service_count", 0)
                    top_services = data.get("top_services", [])

                    result = f"""💰 Total Service Revenue Statistics

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Revenue: ¥{total_revenue:.2f}
• Service Count: {service_count}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔝 Top Services
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

                    if top_services:
                        for i, service in enumerate(top_services[:5], 1):
                            name = service.get("name", "Unknown")
                            revenue = service.get("revenue", 0)
                            calls = service.get("calls", 0)
                            result += (
                                f"{i}. {name}: ¥{revenue:.2f} ({calls:,} calls)\n"
                            )
                    else:
                        result += "No data available\n"

                    result += """
Next Steps:
• Use get_service_revenue(service_id) to view individual service details
• Use list_my_services() to view all services
• Use request_withdrawal() to request withdrawal
"""
                    return result

            elif response.status_code == 404:
                return f"""❌ Service Does Not Exist

Service ID: {service_id}

Use list_my_services() to view all your services.
"""

            else:
                return f"""❌ Query Failed

HTTP {response.status_code}: {response.text[:200]}
"""

    except httpx.TimeoutException:
        return f"❌ Request Timeout ({API_TIMEOUT} seconds)"
    except Exception as e:
        return f"❌ Query Failed: {e!s}"
