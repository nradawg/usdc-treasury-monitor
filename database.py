# ─────────────────────────────────────────────────────────────
#  database.py — Sets up and talks to the SQLite database.
#
#  Two tables:
#    wallets  — stores the latest known balance for each address
#    history  — a log of every balance change ever detected
# ─────────────────────────────────────────────────────────────

import sqlite3
from datetime import datetime
from config import DATABASE_PATH


def get_connection():
    """Opens (or creates) the SQLite database and returns a connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row   # lets us access columns by name
    return conn


def init_db():
    """Creates the tables if they don't already exist. Safe to call on every startup."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            address       TEXT PRIMARY KEY,
            label         TEXT NOT NULL,
            balance       REAL NOT NULL DEFAULT 0,
            last_change   REAL,           -- amount of the last detected change
            last_checked  TEXT            -- ISO timestamp of the last poll
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            address       TEXT NOT NULL,
            label         TEXT NOT NULL,
            old_balance   REAL NOT NULL,
            new_balance   REAL NOT NULL,
            change_amount REAL NOT NULL,  -- positive = received, negative = sent
            timestamp     TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def upsert_wallet(address: str, label: str, balance: float):
    """Inserts a new wallet row or updates the balance and last_checked timestamp."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO wallets (address, label, balance, last_checked)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(address) DO UPDATE SET
            balance      = excluded.balance,
            last_checked = excluded.last_checked
    """, (address, label, balance, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_wallet(address: str):
    """Returns the stored row for a wallet, or None if it hasn't been seen before."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM wallets WHERE address = ?", (address,)
    ).fetchone()
    conn.close()
    return row


def record_change(address: str, label: str, old_balance: float, new_balance: float):
    """Logs a balance change and updates the wallet's last_change field."""
    change = round(new_balance - old_balance, 6)
    now = datetime.utcnow().isoformat()

    conn = get_connection()
    conn.execute("""
        INSERT INTO history (address, label, old_balance, new_balance, change_amount, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (address, label, old_balance, new_balance, change, now))

    conn.execute("""
        UPDATE wallets SET last_change = ?, last_checked = ? WHERE address = ?
    """, (change, now, address))

    conn.commit()
    conn.close()
    return change


def get_all_wallets():
    """Returns all monitored wallets — used by the dashboard."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM wallets ORDER BY label").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_history(limit: int = 20):
    """Returns the most recent balance change events — used by the dashboard."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM history ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
