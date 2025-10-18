# Changelog

All notable changes to this MCP server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-10-18

### Removed - 🧹 Code Cleanup
- Removed temporary test files `test_platform.py` and `test_tools.py`
- Removed demo tool `tools/demo_platform_integration.py`
- Removed test tool `tools/test_mounting.py`
- Streamlined from 32 tools to 28 core business tools

### Added - ✨ Complete Bilateral Market Features

**🔑 API Key Management** (4 tools)
- `create_api_key()` - Create new API Key
  - Support custom name, permission scope and expiration time
  - Complete error handling and security tips
  - Automatically generate secure API Key
- `list_api_keys()` - List all API Keys
  - Display Key status, permissions, creation time and other information
  - Hide full key for security
- `delete_api_key()` - Delete API Key
  - Support instant revocation
  - Provide deletion confirmation and warning
- `get_api_key_stats()` - API Key usage statistics
  - Request count statistics
  - Most used Key analysis

**🖥️ MCP Service Management** (5 tools)
- `register_mcp_service()` - Register new MCP service
  - Support custom pricing model (per request/per token/per minute)
  - Auto-activate service
  - Complete configuration options
- `list_my_services()` - List all my services
  - Display service status, pricing, creation time
  - Batch management support
- `update_mcp_service()` - Update service information
  - Support updating name, description, endpoint, pricing, status
  - Flexible partial update
- `delete_mcp_service()` - Delete service
  - Safe deletion confirmation
  - Preserve historical revenue records
- `get_service_revenue()` - Service revenue statistics
  - Single service and total revenue query
  - Period statistics (daily/weekly/monthly)
  - Top service ranking

**💸 Withdrawal Management** (3 tools)
- `request_withdrawal()` - Request withdrawal
  - Support multiple payment methods (bank transfer/Alipay/WeChat)
  - Complete account information verification
  - Beta version limitation smart tips
- `list_withdrawals()` - List withdrawal records
  - Status filter (pending/processing/completed/rejected)
  - Pagination support
  - Complete timeline display
- `get_withdrawal_detail()` - View withdrawal details
  - Detailed status description
  - Processing progress tracking
  - Admin notes viewing

### Changed
- Tool count increased from 20 to 32
- API coverage improved from 17% to ~30%
- Authentication management tools expanded from 2 to 6
- Completed core business loop (service provider workflow)

### Improved
- All new tools include complete error handling
- User-friendly response format and Emoji icons
- Smart recognition and tips for Beta version limitations
- Detailed help documentation and operation guide

## [1.2.0] - 2025-10-18

### Changed
- 🔄 **Refactored all tools to use real backend API**
  - Fixed API endpoint paths to match production environment
  - Updated authentication mechanism to support OAuth and API Key
  - All tools now call real mcp-factory-platform API
  
- ✨ **Added authentication management tools** (2 tools)
  - `get_oauth_login_url()` - Get OAuth login URL
  - `explain_authentication()` - Detailed authentication configuration instructions

- 🔧 **Updated user management tools** (4 tools)
  - `get_user_profile()` - Get user profile (replaces register_user)
  - `update_user_profile()` - Update user profile
  - `get_user_account()` - Get account summary
  - `get_user_analytics()` - User revenue analytics

- 💰 **Updated wallet management tools** (5 tools)
  - `get_consumer_wallet()` - Get consumer wallet details
  - `get_provider_wallet()` - Get provider wallet details
  - `create_charge()` - Create charge order
  - `transfer_credits()` - Transfer credits between users
  - `get_transactions()` - Get transaction records

- 📊 **Updated billing management tools** (5 tools)
  - `consume_service()` - Consume service and bill
  - `list_services()` - List available MCP services
  - `get_service_endpoint()` - Get service endpoint details
  - `check_server_balance()` - Check server balance
  - `get_server_analytics()` - Get server usage analytics

### Added
- Added `python-dotenv` dependency for environment variable management
- Added `PLATFORM_API_KEY` environment variable configuration
- Added complete error handling and Beta version limitation tips
- Added authentication instruction tool `auth_management.py`

### Fixed
- Fixed OAuth authentication flow instructions
- Fixed API endpoint path errors
- Fixed environment variable not loading issue
- Removed non-existent API endpoints (such as /api/v1/users/register)

### Breaking Changes
- `register_user()` and `login_user()` have been removed (use OAuth login)
- All tools now require `PLATFORM_API_KEY` environment variable
- API endpoint structure has changed to match real backend

## [1.1.0] - 2025-10-18

### Added
- ✅ **User management tools** (5 real tools)
  - `register_user()` - Register new user
  - `login_user()` - User login to get token
  - `get_user_info()` - Get user detailed information
  - `update_user_profile()` - Update user profile
  - `list_users()` - List users (admin)
  
- ✅ **Wallet management tools** (6 real tools)
  - `get_wallet_balance()` - Query wallet balance
  - `add_credits()` - Add credits
  - `charge_credits()` - Charge credits
  - `transfer_credits()` - Transfer credits between users
  - `get_transaction_history()` - Transaction history
  - `get_wallet_details()` - Wallet details and statistics

- ✅ **Billing management tools** (6 real tools)
  - `record_usage()` - Record service usage
  - `get_usage_stats()` - Get usage statistics
  - `get_billing_history()` - Billing history
  - `create_subscription()` - Create subscription
  - `get_subscription_status()` - Query subscription status
  - `cancel_subscription()` - Cancel subscription

- Added httpx dependency for HTTP API calls
- Added environment configuration file `env.example`
- Complete error handling and user-friendly response format

### Changed
- Version upgraded from 1.0.0 to 1.1.0
- Updated project description to "MCP Factory Platform Server - Agent interface for platform management"
- All tools now directly call mcp-factory-platform backend API

### Fixed
- Removed fake tools that only returned demo text
- Implemented real HTTP API calls

## [Unreleased]

### Planned
- Server creation tools (calling mounted mcp-factory-server)
- Cache mechanism optimization
- Batch operation support
- WebSocket real-time notifications

## [1.0.0] - 2025-09-19

### Added
- Initial release
- Basic server configuration
- Core MCP functionality
- Tools, resources, and prompts modules
