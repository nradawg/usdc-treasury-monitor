# ─────────────────────────────────────────────────────────────
#  config.py — All credentials and settings live here.
#  Fill in your real values before running the app.
# ─────────────────────────────────────────────────────────────

# Add one or more wallet addresses you want to monitor.
# Each entry is a label (nickname) paired with the public key.
WALLETS = {
    "Main Treasury": "SOLANA_WALLET_ADDRESS",
    # "Cold Wallet": "ANOTHER_SOLANA_WALLET_ADDRESS",  # uncomment to add more
}

# Twilio credentials — get these from twilio.com/console
TWILIO_ACCOUNT_SID  = "TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN   = "TWILIO_AUTH_TOKEN"
TWILIO_PHONE_NUMBER = "TWILIO_PHONE_NUMBER"   # e.g. "+12015551234"
MY_PHONE_NUMBER     = "MY_PHONE_NUMBER"        # e.g. "+18015557890"

# Solana RPC endpoint (free public node — swap for a private one for reliability)
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

# USDC mint address on Solana mainnet (do not change)
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# How often the monitor checks balances (in seconds)
CHECK_INTERVAL = 60

# SQLite database file path
DATABASE_PATH = "treasury.db"

# Flask web server settings
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = False
