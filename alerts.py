# ─────────────────────────────────────────────────────────────
#  alerts.py — Sends SMS notifications through Twilio.
# ─────────────────────────────────────────────────────────────

from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    MY_PHONE_NUMBER,
)


def send_sms(message: str) -> bool:
    """
    Sends a text message via Twilio.
    Returns True on success, False on failure.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=MY_PHONE_NUMBER,
        )
        print(f"[SMS SENT] {message}")
        return True

    except Exception as e:
        print(f"[ERROR] SMS failed: {e}")
        return False


def build_alert_message(label: str, change: float, new_balance: float) -> str:
    """
    Builds a human-readable SMS based on whether USDC was sent or received.

    Examples:
        "Main Treasury: You received 50.00 USDC. New balance: 192.50 USDC."
        "Main Treasury: 25.00 USDC was sent. New balance: 117.50 USDC."
    """
    abs_change = abs(round(change, 2))
    new_bal    = round(new_balance, 2)

    if change > 0:
        action = f"You received {abs_change} USDC"
    else:
        action = f"{abs_change} USDC was sent"

    return f"{label}: {action}. New balance: {new_bal} USDC."


def alert_on_change(label: str, change: float, new_balance: float):
    """Convenience wrapper — builds and sends the alert in one call."""
    message = build_alert_message(label, change, new_balance)
    send_sms(message)
