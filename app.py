# ─────────────────────────────────────────────────────────────
#  app.py — Entry point. Starts Flask and the background monitor.
#
#  Run this file to launch the full application:
#      python app.py
# ─────────────────────────────────────────────────────────────

from flask import Flask, render_template, jsonify

from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from database import init_db, get_all_wallets, get_recent_history
from monitor import start_monitor_thread

app = Flask(__name__)


# ── Routes ──────────────────────────────────────────────────

@app.route("/")
def dashboard():
    """Renders the main treasury dashboard page."""
    wallets = get_all_wallets()
    history = get_recent_history(limit=20)
    return render_template("dashboard.html", wallets=wallets, history=history)


@app.route("/api/wallets")
def api_wallets():
    """JSON endpoint — used by the dashboard's auto-refresh JavaScript."""
    return jsonify(get_all_wallets())


@app.route("/api/history")
def api_history():
    """JSON endpoint — returns the 20 most recent balance change events."""
    return jsonify(get_recent_history(limit=20))


# ── Startup ─────────────────────────────────────────────────

if __name__ == "__main__":
    # 1. Make sure the database tables exist
    init_db()
    print("Database initialized.")

    # 2. Start the background blockchain monitor
    start_monitor_thread()
    print("Monitor thread started.")

    # 3. Start the Flask web server
    print(f"Dashboard available at http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
