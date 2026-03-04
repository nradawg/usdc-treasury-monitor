# USDC Treasury Monitor

A lightweight Python app that tracks USDC balances across one or more Solana wallets,
sends SMS alerts when balances change, and displays a live dashboard in your browser.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                     app.py                          │
│   Starts Flask server + launches monitor thread     │
└────────────┬──────────────────────┬─────────────────┘
             │                      │
    ┌────────▼────────┐    ┌────────▼────────┐
    │   monitor.py    │    │   Flask routes  │
    │  (background    │    │  /  /api/wallets│
    │   thread)       │    │  /api/history   │
    └────────┬────────┘    └────────┬────────┘
             │                      │
    ┌────────▼────────┐    ┌────────▼────────┐
    │  blockchain.py  │    │  database.py    │
    │  Solana RPC     │    │  SQLite reads   │
    │  getTokenAccts  │    │  for dashboard  │
    └────────┬────────┘    └─────────────────┘
             │
    ┌────────▼────────┐    ┌─────────────────┐
    │  database.py    │───►│   alerts.py     │
    │  Write changes  │    │  Twilio SMS     │
    └─────────────────┘    └─────────────────┘
```

Every 60 seconds the monitor fetches your USDC balance from the Solana blockchain.
If it changed, the event is written to SQLite and an SMS is sent via Twilio.
The Flask web server reads from the same SQLite database to power the dashboard.

---

## Project Structure

```
usdc_treasury/
├── app.py            ← Entry point. Run this to start everything.
├── monitor.py        ← Background thread that polls Solana every 60s
├── blockchain.py     ← Fetches USDC balances from the Solana RPC API
├── alerts.py         ← Sends SMS messages via Twilio
├── database.py       ← SQLite setup, reads, and writes
├── config.py         ← All credentials and settings (edit this first)
├── requirements.txt  ← Python dependencies
└── templates/
    └── dashboard.html ← Web dashboard UI
```

---

## Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

---

## Step 2 — Fill in your credentials

Open `config.py` and replace the placeholder values:

```python
WALLETS = {
    "Main Treasury": "YOUR_PHANTOM_WALLET_PUBLIC_KEY",
}

TWILIO_ACCOUNT_SID  = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN   = "your_auth_token_here"
TWILIO_PHONE_NUMBER = "+12015551234"   # Twilio number
MY_PHONE_NUMBER     = "+18015557890"   # your real number
```

**Where to find each value:**
- Wallet address: Open Phantom → click your account name → copy the public key
- Twilio creds: https://console.twilio.com (Account SID and Auth Token on the home page)
- Twilio phone number: Console → Phone Numbers → Manage → Active Numbers

---

## Step 3 — Run the application

```bash
python app.py
```

You'll see:

```
Database initialized.
Monitor thread started.
Dashboard available at http://127.0.0.1:5000
Monitor started. Checking 1 wallet(s) every 60s.
[Main Treasury] Initial balance recorded: 142.50 USDC
```

Open your browser to **http://127.0.0.1:5000** to see the dashboard.

---

## Step 4 — Keep it running (optional)

**Mac / Linux:**
```bash
nohup python app.py &> treasury.log &
```

**Windows (PowerShell):**
```powershell
Start-Process python -ArgumentList "app.py" -WindowStyle Minimized
```

---

## Three improvements toward a production SaaS

**1. Use a private Solana RPC endpoint**
The free public node (`api.mainnet-beta.solana.com`) is rate-limited and shared.
Sign up for a free dedicated endpoint at Helius (helius.dev) or QuickNode and
swap the URL in config.py. This eliminates missed checks during high-traffic periods.

**2. Move secrets to environment variables**
Hardcoding credentials in config.py is fine for local use but a security risk
if the code is ever pushed to Git. Use `python-dotenv` and a `.env` file instead:
```bash
pip install python-dotenv
```
Then load with `os.environ.get("TWILIO_AUTH_TOKEN")` and add `.env` to `.gitignore`.

**3. Add user accounts and deploy to a server**
To turn this into a multi-tenant SaaS: add Flask-Login for authentication so each
user manages their own wallets, migrate from SQLite to PostgreSQL for concurrent
access, and deploy on Railway or Render (both offer free tiers). Each user's SMS
alert routes through a shared Twilio number but isolated to their account.
