# ─────────────────────────────────────────────────────────────
#  monitor.py — Background thread that polls Solana every 60s.
#
#  This runs independently of Flask. It uses Python's threading
#  module so both the web server and the monitor run simultaneously
#  when you launch app.py.
# ─────────────────────────────────────────────────────────────

import time
import threading
from datetime import datetime

from config import WALLETS, CHECK_INTERVAL
from blockchain import get_usdc_balance
from database import get_wallet, upsert_wallet, record_change
from alerts import alert_on_change


def check_wallet(address: str, label: str):
    """
    Fetches the current USDC balance for one wallet, compares it to the
    last stored value, and triggers an alert + database write if it changed.
    """
    current_balance = get_usdc_balance(address)

    if current_balance is None:
        # RPC error — skip this round, keep the old balance in the DB
        print(f"[{label}] RPC error, skipping this round.")
        return

    previous_row = get_wallet(address)

    if previous_row is None:
        # First time we've seen this wallet — just save the baseline
        upsert_wallet(address, label, current_balance)
        print(f"[{label}] Initial balance recorded: {current_balance} USDC")
        return

    previous_balance = previous_row["balance"]

    if current_balance != previous_balance:
        change = record_change(address, label, previous_balance, current_balance)
        alert_on_change(label, change, current_balance)
        upsert_wallet(address, label, current_balance)
        print(
            f"[{label}] CHANGE DETECTED — "
            f"{previous_balance} → {current_balance} USDC "
            f"(Δ {'+' if change > 0 else ''}{round(change, 6)})"
        )
    else:
        # No change — just update the last_checked timestamp
        upsert_wallet(address, label, current_balance)
        print(
            f"[{label}] {datetime.utcnow().strftime('%H:%M:%S')} — "
            f"No change: {current_balance} USDC"
        )


def run_monitor():
    """
    Infinite loop that checks every wallet in config.WALLETS
    on the configured interval. Designed to run in a background thread.
    """
    print(f"Monitor started. Checking {len(WALLETS)} wallet(s) every {CHECK_INTERVAL}s.")

    while True:
        for label, address in WALLETS.items():
            check_wallet(address, label)

        time.sleep(CHECK_INTERVAL)


def start_monitor_thread():
    """Launches the monitor loop in a daemon thread (stops when the main app stops)."""
    thread = threading.Thread(target=run_monitor, daemon=True)
    thread.start()
    return thread
