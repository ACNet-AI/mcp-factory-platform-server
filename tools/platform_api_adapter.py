"""Platform API Adapter Tools - Convert mcp-factory-platform REST API to MCP tools"""

import os

# Exported tool functions list
__all__ = [
    "create_platform_api_adapter",
    "generate_platform_tools",
    "list_platform_endpoints",
    "test_platform_connection",
]

# Platform backend configuration - read from environment variables
PLATFORM_API_BASE = os.getenv("PLATFORM_API_BASE", "http://localhost:8001")
PLATFORM_OPENAPI_URL = f"{PLATFORM_API_BASE}/openapi.json"


async def create_platform_api_adapter() -> str:
    """Create platform API adapter - using mcp-factory's HTTP adapter functionality

    Returns:
        Adapter creation result
    """

    try:
        # Here we create the adapter through the mounted mcp-factory-server
        # The actual call should be:
        # result = await server.call_external_tool("mcp-factory-server", "create_adapter", {
        #     "adapter_type": "http",
        #     "source_path": PLATFORM_API_BASE,
        #     "config": {
        #         "timeout": 30,
        #         "use_fastmcp": True,
        #         "headers": {"Content-Type": "application/json"}
        #     }
        # })

        # MVP stage: return configuration information first
        return f"""✅ Platform API Adapter Configuration

Adapter Type: HTTP API
Target API: {PLATFORM_API_BASE}
OpenAPI Docs: {PLATFORM_OPENAPI_URL}

Configuration Parameters:
- Timeout: 30 seconds
- Use FastMCP: Yes
- Auto Discovery: Yes

Next Steps:
1. Use test_platform_connection() to test connection
2. Use list_platform_endpoints() to view available endpoints
3. Use generate_platform_tools() to generate MCP tools

Note: Actual adapter creation requires calling the mounted mcp-factory-server
"""

    except Exception as e:
        return f"❌ Failed to create platform API adapter: {str(e)}"


async def test_platform_connection() -> str:
    """Test connection to platform backend

    Returns:
        Connection test result
    """

    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test health check endpoint
            health_response = await client.get(f"{PLATFORM_API_BASE}/health")

            if health_response.status_code == 200:
                health_data = health_response.json()

                # Try to get OpenAPI documentation
                try:
                    openapi_response = await client.get(PLATFORM_OPENAPI_URL)
                    openapi_available = openapi_response.status_code == 200
                    if openapi_available:
                        openapi_data = openapi_response.json()
                        endpoint_count = len(openapi_data.get("paths", {}))
                    else:
                        endpoint_count = "Unknown"
                except Exception:
                    openapi_available = False
                    endpoint_count = "Unknown"

                return f"""✅ Platform Connection Test Successful

Health Status:
- Service: {health_data.get("service", "unknown")}
- Status: {health_data.get("status", "unknown")}
- Version: {health_data.get("version", "unknown")}
- Billing Proxy: {health_data.get("billing_proxy", "unknown")}

API Documentation:
- OpenAPI Available: {"Yes" if openapi_available else "No"}
- Endpoint Count: {endpoint_count}

Connection Info:
- Base URL: {PLATFORM_API_BASE}
- Response Time: {health_response.elapsed.total_seconds():.3f}s
"""
            else:
                return f"❌ Platform connection failed: HTTP {health_response.status_code}"

    except httpx.ConnectError:
        return f"❌ Platform connection failed: Unable to connect to {PLATFORM_API_BASE}"
    except httpx.TimeoutException:
        return "❌ Platform connection failed: Connection timeout"
    except Exception as e:
        return f"❌ Platform connection test failed: {str(e)}"


async def list_platform_endpoints() -> str:
    """List all endpoints of the platform API

    Returns:
        Endpoint list
    """

    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(PLATFORM_OPENAPI_URL)

            if response.status_code != 200:
                return f"❌ Unable to get OpenAPI documentation: HTTP {response.status_code}"

            openapi_data = response.json()
            paths = openapi_data.get("paths", {})

            if not paths:
                return "⚠️ No API endpoints found"

            result = f"📋 Platform API Endpoint List ({len(paths)} endpoints)\n\n"

            # Group by functionality
            user_endpoints = []
            wallet_endpoints = []
            service_endpoints = []
            admin_endpoints = []
            other_endpoints = []

            for path, methods in paths.items():
                for method, details in methods.items():
                    if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                        summary = details.get("summary", path)
                        endpoint_info = f"{method.upper()} {path} - {summary}"

                        if "/users/" in path:
                            user_endpoints.append(endpoint_info)
                        elif "/wallet" in path or "/credit" in path:
                            wallet_endpoints.append(endpoint_info)
                        elif "/services/" in path:
                            service_endpoints.append(endpoint_info)
                        elif "/admin/" in path:
                            admin_endpoints.append(endpoint_info)
                        else:
                            other_endpoints.append(endpoint_info)

            # Output grouped results
            if user_endpoints:
                result += "👤 User Management:\n"
                for endpoint in user_endpoints[:5]:  # Limit display count
                    result += f"  - {endpoint}\n"
                if len(user_endpoints) > 5:
                    result += f"  ... {len(user_endpoints) - 5} more endpoints\n"
                result += "\n"

            if wallet_endpoints:
                result += "💰 Wallet Management:\n"
                for endpoint in wallet_endpoints[:5]:
                    result += f"  - {endpoint}\n"
                if len(wallet_endpoints) > 5:
                    result += f"  ... {len(wallet_endpoints) - 5} more endpoints\n"
                result += "\n"

            if service_endpoints:
                result += "🔧 Service Management:\n"
                for endpoint in service_endpoints[:5]:
                    result += f"  - {endpoint}\n"
                if len(service_endpoints) > 5:
                    result += f"  ... {len(service_endpoints) - 5} more endpoints\n"
                result += "\n"

            if admin_endpoints:
                result += "⚙️ Admin Features:\n"
                for endpoint in admin_endpoints[:3]:
                    result += f"  - {endpoint}\n"
                if len(admin_endpoints) > 3:
                    result += f"  ... {len(admin_endpoints) - 3} more endpoints\n"
                result += "\n"

            if other_endpoints:
                result += "🔗 Other Features:\n"
                for endpoint in other_endpoints[:3]:
                    result += f"  - {endpoint}\n"
                if len(other_endpoints) > 3:
                    result += f"  ... {len(other_endpoints) - 3} more endpoints\n"

            result += (
                "\n💡 Tip: Use generate_platform_tools() to convert these endpoints to MCP tools"
            )

            return result

    except Exception as e:
        return f"❌ Failed to get endpoint list: {str(e)}"


async def generate_platform_tools(endpoint_filter: str = "") -> str:
    """Generate MCP tool code for platform API

    Args:
        endpoint_filter: Endpoint filter (optional, e.g., "users", "wallet", etc.)

    Returns:
        Tool generation result
    """

    try:
        # Here we should call the mounted mcp-factory-server to generate tools
        # The actual call should be:
        # result = await server.call_external_tool("mcp-factory-server", "generate_tools_from_api", {
        #     "api_url": PLATFORM_API_BASE,
        #     "openapi_url": PLATFORM_OPENAPI_URL,
        #     "filter": endpoint_filter,
        #     "output_format": "mcp_tools"
        # })

        # MVP stage: return generation plan
        filter_desc = f" (Filter: {endpoint_filter})" if endpoint_filter else ""

        return f"""🔧 Platform API Tool Generation Plan{filter_desc}

Generation Configuration:
- Source API: {PLATFORM_API_BASE}
- OpenAPI Docs: {PLATFORM_OPENAPI_URL}
- Adapter Type: HTTP API
- Output Format: MCP Tools

Expected Tool Categories:
1. User Management Tools:
   - register_user() - Register user
   - get_user_info() - Get user information
   - get_user_wallets() - Get user wallets

2. Wallet Management Tools:
   - add_credits() - Add credits
   - charge_credits() - Charge credits
   - transfer_credits() - Transfer credits

3. Service Management Tools:
   - list_services() - List services
   - get_service_info() - Get service information
   - search_services() - Search services

4. Billing Tools:
   - record_usage() - Record usage
   - get_invoices() - Get invoices

Actual Generation Steps:
1. Call mcp-factory-server's HTTP adapter
2. Parse OpenAPI specification
3. Generate corresponding MCP tool code
4. Register to platform server

Note: Currently in MVP stage, need to implement actual call to mounted server.
"""

    except Exception as e:
        return f"❌ Failed to generate platform tools: {str(e)}"
