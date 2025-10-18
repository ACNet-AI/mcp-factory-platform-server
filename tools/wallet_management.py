"""Wallet Management Tools - Interact with Platform Backend API"""

import os

import httpx

__all__ = [
    "get_consumer_wallet",
    "get_provider_wallet",
    "create_charge",
    "transfer_credits",
    "get_transactions",
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


async def get_consumer_wallet(user_id: str) -> str:
    """Get consumer wallet information

    Args:
        user_id: User ID

    Returns:
        Consumer wallet details
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/consumer_wallet",
                headers=_get_headers(),
            )

            if response.status_code == 200:
                data = response.json()

                return f"""✅ Consumer Wallet Details

💰 Balance Information:
- Current Balance: {data.get("balance", 0)} credits
- Frozen Balance: {data.get("frozen_balance", 0)} credits
- Available Balance: {data.get("available_balance", 0)} credits

📊 Usage Statistics:
- Total Recharged: {data.get("total_recharged", 0)} credits
- Total Spent: {data.get("total_spent", 0)} credits
- Transaction Count: {data.get("transaction_count", 0)}

📅 Recent Activity:
- Last Recharge: {data.get("last_recharge_at", "N/A")}
- Last Spend: {data.get("last_spend_at", "N/A")}

Next Steps:
- Use create_charge() to add credits
- Use get_transactions() to view transaction history
"""

            elif response.status_code == 403:
                return f"❌ Insufficient Permissions: Cannot access wallet for user {user_id}"

            elif response.status_code == 404:
                return f"❌ Wallet Not Found: user {user_id}"

            else:
                return f"❌ Failed to Retrieve Wallet: HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Failed to Retrieve Consumer Wallet: {str(e)}"


async def get_provider_wallet(user_id: str) -> str:
    """Get provider wallet information

    Args:
        user_id: User ID

    Returns:
        Provider wallet details
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/provider_wallet",
                headers=_get_headers(),
            )

            if response.status_code == 200:
                data = response.json()

                return f"""✅ Provider Wallet Details

💰 Balance Information:
- Current Balance: {data.get("balance", 0)} credits
- Frozen Balance: {data.get("frozen_balance", 0)} credits
- Withdrawable Balance: {data.get("withdrawable_balance", 0)} credits

📊 Revenue Statistics:
- Total Revenue: {data.get("total_revenue", 0)} credits
- Total Withdrawn: {data.get("total_withdrawn", 0)} credits
- Transaction Count: {data.get("transaction_count", 0)}

📅 Recent Activity:
- Last Revenue: {data.get("last_revenue_at", "N/A")}
- Last Withdrawal: {data.get("last_withdraw_at", "N/A")}

💡 Note:
- Revenue comes from other users using your MCP services
- Platform deducts fees before settling to provider wallet

Next Steps:
- Use request_withdrawal() to request withdrawal (Not available in Beta)
- Use get_transactions() to view revenue records
"""

            elif response.status_code == 403:
                return f"❌ Insufficient Permissions: Cannot access wallet for user {user_id}"

            elif response.status_code == 404:
                return f"❌ Wallet Not Found: user {user_id}"

            else:
                return f"❌ Failed to Retrieve Wallet: HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Failed to Retrieve Provider Wallet: {str(e)}"


async def create_charge(
    user_id: str, amount: float, payment_method: str = "credits"
) -> str:
    """Create charge order

    Args:
        user_id: User ID
        amount: Charge amount (credits)
        payment_method: Payment method (credits/stripe/alipay)

    Returns:
        Charge result
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/charges",
                headers=_get_headers(),
                json={"amount": amount, "payment_method": payment_method},
            )

            if response.status_code == 200:
                data = response.json()

                return f"""✅ Charge Order Created Successfully

Order Information:
- Order ID: {data.get("charge_id", "N/A")}
- Amount: {amount} credits
- Payment Method: {payment_method}
- Status: {data.get("status", "pending")}

{_get_payment_instructions(payment_method, data)}

Next Steps:
- Use get_consumer_wallet() to check balance after payment
"""

            elif response.status_code == 403:
                detail = response.json().get("detail", {})
                if detail.get("error") == "feature_restricted_in_beta":
                    return f"""❌ Beta Version Restriction

{detail.get("message")}

Description: {detail.get("description")}

💡 Beta users can:
- Use 1000 free credits provided by platform
- Experience all core features
- Use without recharging
"""
                return f"❌ Insufficient Permissions: {detail}"

            else:
                return f"❌ Failed to Create Charge Order: HTTP {response.status_code} - {response.text}"

    except Exception as e:
        return f"❌ Failed to Create Charge Order: {str(e)}"


async def transfer_credits(
    from_user_id: str, to_user_id: str, amount: float, note: str = ""
) -> str:
    """Transfer credits between users

    Args:
        from_user_id: Sender user ID
        to_user_id: Recipient user ID
        amount: Transfer amount (credits)
        note: Transfer note (optional)

    Returns:
        Transfer result
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(
                f"{PLATFORM_API_BASE}/api/users/{from_user_id}/transfers",
                headers=_get_headers(),
                json={"to_user_id": to_user_id, "amount": amount, "note": note},
            )

            if response.status_code == 200:
                data = response.json()

                return f"""✅ Transfer Successful

Transaction Information:
- Transaction ID: {data.get("transaction_id", "N/A")}
- From User: {from_user_id}
- To User: {to_user_id}
- Amount: {amount} credits
- Note: {note or "None"}

Account Balance:
- Current Balance: {data.get("new_balance", "N/A")} credits

Next Steps:
- Use get_transactions() to view transaction history
"""

            elif response.status_code == 400:
                error = response.json().get("detail", "Transfer failed")
                return f"❌ Transfer Failed: {error}"

            elif response.status_code == 403:
                return "❌ Insufficient Permissions or Insufficient Balance"

            else:
                return f"❌ Transfer Failed: HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Transfer Failed: {str(e)}"


async def get_transactions(
    user_id: str, limit: int = 10, transaction_type: str = "all"
) -> str:
    """Get transaction records

    Args:
        user_id: User ID
        limit: Return count limit
        transaction_type: Transaction type (all/charge/spend/transfer/revenue)

    Returns:
        Transaction records list
    """
    if not PLATFORM_API_KEY:
        return """❌ API Key Not Configured

Use explain_authentication() for authentication configuration instructions
"""

    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(
                f"{PLATFORM_API_BASE}/api/users/{user_id}/transactions",
                headers=_get_headers(),
                params={"limit": limit, "type": transaction_type},
            )

            if response.status_code == 200:
                data = response.json()
                transactions = data.get("transactions", [])

                if not transactions:
                    return f"📋 No Transactions (type: {transaction_type})"

                result = f"""📋 Transaction Records (Latest {len(transactions)} records)

"""

                for i, tx in enumerate(transactions, 1):
                    tx_type = tx.get("type", "unknown")
                    amount = tx.get("amount", 0)
                    sign = "+" if tx_type in ["charge", "revenue", "refund"] else "-"

                    result += f"""{i}. {tx.get("description", "N/A")}
   Amount: {sign}{amount} credits
   Type: {tx_type}
   Time: {tx.get("created_at", "N/A")}
   Status: {tx.get("status", "N/A")}

"""

                result += f"""
Total: {len(transactions)} transactions

Next Steps:
- Adjust limit parameter to view more records
- Use transaction_type parameter to filter by type
"""

                return result

            elif response.status_code == 403:
                return f"❌ Insufficient Permissions: Cannot access transaction records for user {user_id}"

            else:
                return f"❌ Failed to Retrieve Transaction Records: HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Failed to Retrieve Transaction Records: {str(e)}"


def _get_payment_instructions(payment_method: str, data: dict) -> str:
    """Get payment instructions"""
    if payment_method == "credits":
        return """💡 Using Platform Credits:
- Credits will be automatically deducted
- Beta users enjoy 1000 free credits"""

    elif payment_method == "stripe":
        return f"""💳 Stripe Payment:
- Payment Link: {data.get("payment_url", "N/A")}
- Please open the link in browser to complete payment"""

    elif payment_method == "alipay":
        return """💰 Alipay Payment:
- Not available in Beta version
- Coming soon"""

    return ""
