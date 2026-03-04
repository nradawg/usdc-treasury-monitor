# ─────────────────────────────────────────────────────────────
#  blockchain.py — Fetches USDC balances from the Solana network.
#
#  Uses the Solana JSON-RPC API — no special SDK required,
#  just plain HTTP requests.
# ─────────────────────────────────────────────────────────────

import requests
from config import SOLANA_RPC_URL, USDC_MINT


def get_usdc_balance(wallet_address: str) -> float | None:
    """
    Queries the Solana RPC for the USDC token balance of a wallet.

    Returns the human-readable balance as a float (e.g. 142.50),
    or None if the request failed (so the caller can skip that round
    rather than misreporting a zero balance).
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet_address,
            {"mint": USDC_MINT},
            {"encoding": "jsonParsed"}
        ]
    }

    try:
        response = requests.post(SOLANA_RPC_URL, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()

        accounts = data.get("result", {}).get("value", [])

        # No USDC token account means a zero balance — that's valid
        if not accounts:
            return 0.0

        # A wallet can technically have multiple USDC accounts (rare),
        # so we sum them all just to be safe
        total = 0.0
        for account in accounts:
            token_amount = (
                account["account"]["data"]["parsed"]["info"]["tokenAmount"]
            )
            total += float(token_amount.get("uiAmount") or 0.0)

        return round(total, 6)

    except requests.exceptions.Timeout:
        print(f"[WARN] RPC timeout for {wallet_address[:8]}...")
        return None

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error fetching balance: {e}")
        return None

    except (KeyError, ValueError, TypeError) as e:
        print(f"[ERROR] Unexpected RPC response format: {e}")
        return None
