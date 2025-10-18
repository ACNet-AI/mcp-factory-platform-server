"""
Withdrawal Management Tools

Provides withdrawal request, query, and detail features.
"""

import os

import httpx

__all__ = [
    "request_withdrawal",
    "list_withdrawals",
    "get_withdrawal_detail",
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


async def request_withdrawal(
    amount: float,
    payment_method: str = "bank_transfer",
    account_name: str = "",
    account_number: str = "",
    bank_name: str = "",
    notes: str = "",
) -> str:
    """Request withdrawal

    Args:
        amount: Withdrawal amount (credits)
        payment_method: Payment method (bank_transfer/alipay/wechat)
        account_name: Account name (optional)
        account_number: Account number (optional)
        bank_name: Bank name (required for bank transfer)
        notes: Notes (optional)

    Returns:
        Withdrawal request result

    Example:
        >>> await request_withdrawal(
        ...     100.0,
        ...     "bank_transfer",
        ...     "John Doe",
        ...     "6222021234567890",
        ...     "ICBC"
        ... )
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Please configure PLATFORM_API_KEY environment variable first.
Use explain_authentication() for configuration instructions.
"""

    if amount <= 0:
        return """❌ Withdrawal Amount Must Be Greater Than 0

Please enter valid withdrawal amount (unit: credits).
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

Current API Key is invalid or expired.
Visit {PLATFORM_API_BASE}/auth/login to re-login.
"""

            user_data = verify_response.json()
            user_id = user_data.get("user_id")

            if not user_id:
                return "❌ Cannot get user information, please re-login."

            # Build account info
            account_info = {}
            if account_name:
                account_info["account_name"] = account_name
            if account_number:
                account_info["account_number"] = account_number
            if bank_name:
                account_info["bank_name"] = bank_name

            # Request withdrawal
            response = await client.post(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/withdrawals",
                headers=_get_headers(),
                json={
                    "amount": amount,
                    "payment_method": payment_method,
                    "account_info": account_info,
                    "notes": notes,
                },
            )

            if response.status_code in (200, 201):
                data = response.json()
                withdrawal_id = data.get("withdrawal_id", "N/A")
                status = data.get("status", "pending")
                estimated_arrival = data.get("estimated_arrival", "3-5 business days")

                return f"""✅ Withdrawal Request Submitted!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💸 Withdrawal Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Withdrawal ID: {withdrawal_id}
• Amount: ¥{amount:.2f}
• Payment Method: {payment_method}
• Status: {status}
• Estimated Arrival: {estimated_arrival}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Account Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Account Name: {account_name or "Not provided"}
• Account Number: {account_number or "Not provided"}
{f"• Bank: {bank_name}" if bank_name else ""}
{f"• Notes: {notes}" if notes else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳ Processing Steps
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ✅ Submit Request (Completed)
2. ⏳ Platform Review (1 business day)
3. ⏳ Financial Processing (1-2 business days)
4. ⏳ Bank Transfer (1-2 business days)

💡 Tips:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Withdrawal amount will be deducted from provider wallet
• Can cancel before approval
• Use get_withdrawal_detail("{withdrawal_id}") to check progress
• Use list_withdrawals() to view all withdrawal records

Next Steps:
• Wait patiently for review result
• Check email for review notification
• Ensure account information is accurate
"""

            elif response.status_code == 400:
                detail = response.json().get("detail", {})
                if isinstance(detail, dict):
                    message = detail.get("message", "Request parameter error")
                    description = detail.get("description", "")

                    # Beta version restriction
                    if "beta" in message.lower() or "beta" in description.lower():
                        return f"""❌ Beta Version Restriction

{message}

Description: {description}

💡 Beta users can:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• ✅ Register services and earn revenue
• ✅ View provider wallet balance
• ✅ View revenue statistics
• ❌ Withdrawal not supported (Beta restriction)

After official release, you can withdraw all accumulated revenue.
"""

                    return f"""❌ Withdrawal Request Failed

{message}

{description}

Common Issues:
• Check if withdrawal amount exceeds available balance
• Confirm account information is complete
• Check if payment method is supported (bank_transfer/alipay/wechat)
"""

                return f"""❌ Withdrawal Request Failed

{detail}
"""

            elif response.status_code == 403:
                return """❌ Insufficient Balance

Withdrawal amount exceeds available balance.

Solutions:
• Use get_provider_wallet() to check available balance
• Reduce withdrawal amount
• Wait for more revenue to accumulate
"""

            else:
                return f"""❌ Request Failed

HTTP {response.status_code}: {response.text[:200]}
"""

    except httpx.TimeoutException:
        return f"❌ Request Timeout ({API_TIMEOUT} seconds)\nCheck network connection."
    except Exception as e:
        return f"❌ Request Failed: {e!s}"


async def list_withdrawals(limit: int = 10, status_filter: str = "") -> str:
    """List withdrawal records

    Args:
        limit: Return count limit (default 10)
        status_filter: Status filter (pending/processing/completed/rejected)

    Returns:
        Withdrawal records list

    Example:
        >>> await list_withdrawals(10, "pending")
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

            # Get withdrawal list
            params = {"limit": limit}
            if status_filter:
                params["status"] = status_filter

            response = await client.get(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/withdrawals",
                headers=_get_headers(),
                params=params,
            )

            if response.status_code == 200:
                data = response.json()
                withdrawals = data.get("withdrawals", [])

                if not withdrawals:
                    return f"""📋 Withdrawal Records

{"No withdrawal records currently." if not status_filter else f"No withdrawal records with {status_filter} status."}

Request Withdrawal:
Use request_withdrawal(amount, payment_method, ...) to request withdrawal

Example:
request_withdrawal(
    100.0,
    "bank_transfer",
    "John Doe",
    "6222021234567890",
    "ICBC"
)
"""

                result = f"""📋 Withdrawal Records

{"All withdrawals" if not status_filter else f"{status_filter} status withdrawals"} (Total {len(withdrawals)} records):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

                for i, withdrawal in enumerate(withdrawals, 1):
                    withdrawal_id = withdrawal.get("withdrawal_id", "N/A")
                    amount = withdrawal.get("amount", 0)
                    status = withdrawal.get("status", "unknown")
                    payment_method = withdrawal.get("payment_method", "N/A")
                    created_at = withdrawal.get("created_at", "N/A")

                    status_icons = {
                        "pending": "⏳",
                        "processing": "🔄",
                        "completed": "✅",
                        "rejected": "❌",
                        "cancelled": "🚫",
                    }
                    status_icon = status_icons.get(status, "❓")

                    result += f"""{i}. {status_icon} ¥{amount:.2f}
   • ID: {withdrawal_id}
   • Status: {status}
   • Payment Method: {payment_method}
   • Request Time: {created_at}

"""

                result += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Actions:
• get_withdrawal_detail(withdrawal_id) - View details
• request_withdrawal(...) - Request new withdrawal

Status Explanation:
• ⏳ pending - Awaiting review
• 🔄 processing - Processing
• ✅ completed - Completed
• ❌ rejected - Rejected
• 🚫 cancelled - Cancelled
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


async def get_withdrawal_detail(withdrawal_id: str) -> str:
    """Get withdrawal details

    Args:
        withdrawal_id: Withdrawal ID

    Returns:
        Withdrawal detailed information

    Example:
        >>> await get_withdrawal_detail("withdrawal_123")
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

            # Get withdrawal details
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/withdrawals/{withdrawal_id}",
                headers=_get_headers(),
            )

            if response.status_code == 200:
                data = response.json()

                withdrawal_id = data.get("withdrawal_id", "N/A")
                amount = data.get("amount", 0)
                status = data.get("status", "unknown")
                payment_method = data.get("payment_method", "N/A")
                account_info = data.get("account_info", {})
                created_at = data.get("created_at", "N/A")
                processed_at = data.get("processed_at", "Pending")
                notes = data.get("notes", "")
                admin_notes = data.get("admin_notes", "")

                status_icons = {
                    "pending": "⏳",
                    "processing": "🔄",
                    "completed": "✅",
                    "rejected": "❌",
                    "cancelled": "🚫",
                }
                status_icon = status_icons.get(status, "❓")

                # Build notes section
                notes_section = ""
                if notes or admin_notes:
                    notes_section = "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📝 Notes\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    if notes:
                        notes_section += f"\n• Request Notes: {notes}"
                    if admin_notes:
                        notes_section += f"\n• Admin Notes: {admin_notes}"

                bank_line = (
                    f"\n• Bank: {account_info.get('bank_name')}"
                    if account_info.get("bank_name")
                    else ""
                )

                return f"""💸 Withdrawal Details

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Basic Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Withdrawal ID: {withdrawal_id}
• Amount: ¥{amount:.2f}
• Status: {status_icon} {status}
• Payment Method: {payment_method}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏦 Account Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Account Name: {account_info.get("account_name", "N/A")}
• Account Number: {account_info.get("account_number", "N/A")}{bank_line}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Time Records
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Request Time: {created_at}
• Process Time: {processed_at}{notes_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{_get_status_help(status)}

Next Steps:
• Use list_withdrawals() to view all withdrawal records
• Use get_provider_wallet() to view wallet balance
"""

            elif response.status_code == 404:
                return f"""❌ Withdrawal Record Does Not Exist

Withdrawal ID: {withdrawal_id}

Possible Reasons:
• Incorrect ID
• Record already deleted
• No permission to access

Use list_withdrawals() to view all withdrawal records.
"""

            else:
                return f"""❌ Query Failed

HTTP {response.status_code}: {response.text[:200]}
"""

    except httpx.TimeoutException:
        return f"❌ Request Timeout ({API_TIMEOUT} seconds)"
    except Exception as e:
        return f"❌ Query Failed: {e!s}"


def _get_status_help(status: str) -> str:
    """Return help information based on status"""
    status_help = {
        "pending": """⏳ Current Status: Awaiting Review

• Your withdrawal request is awaiting platform review
• Usually completed within 1 business day
• Can cancel during review period
• Please ensure account information is accurate""",
        "processing": """🔄 Current Status: Processing

• Review passed, financial team is processing
• Expected to complete transfer in 1-2 business days
• Cannot cancel during processing
• Will receive email notification upon completion""",
        "completed": """✅ Current Status: Completed

• Withdrawal successfully completed
• Funds have been transferred to your account
• Please check your bank account
• Contact customer service if any issues""",
        "rejected": """❌ Current Status: Rejected

• Withdrawal request did not pass review
• Check admin notes for reason
• Amount has been returned to provider wallet
• Can reapply after updating information""",
        "cancelled": """🚫 Current Status: Cancelled

• Withdrawal request has been cancelled
• Amount has been returned to provider wallet
• Can reapply for withdrawal""",
    }

    return status_help.get(status, "❓ Unknown Status")
