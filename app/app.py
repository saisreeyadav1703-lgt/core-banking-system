import sqlite3, os
from flask import Flask, jsonify, request, render_template
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "/data/banking.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS accounts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        balance REAL DEFAULT 0.0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account TEXT NOT NULL,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT DEFAULT '',
        status TEXT DEFAULT 'success',
        timestamp TEXT NOT NULL,
        FOREIGN KEY(account) REFERENCES accounts(id)
    )""")
    # Seed accounts
    accounts = [
        ("ACC-001", "Saisree Yadava",  50000.00),
        ("ACC-002", "Ravi Kumar",      25000.00),
        ("ACC-003", "Priya Sharma",    75000.00),
    ]
    c.executemany("INSERT OR IGNORE INTO accounts VALUES (?,?,?)", accounts)
    # Seed transactions
    seeds = [
        ("ACC-001","credit",15000,"Salary Credit","2026-09-01T09:00:00"),
        ("ACC-001","debit", 3500, "Electricity Bill","2026-09-02T10:30:00"),
        ("ACC-002","credit",8000, "Freelance Payment","2026-09-03T14:00:00"),
        ("ACC-003","debit", 5000, "Online Shopping","2026-09-04T16:45:00"),
        ("ACC-001","credit",2000, "Interest Credit","2026-09-05T08:00:00"),
    ]
    for s in seeds:
        c.execute("INSERT OR IGNORE INTO transactions (account,type,amount,description,timestamp) VALUES (?,?,?,?,?)", s)
        if s[1]=="credit":
            c.execute("UPDATE accounts SET balance=balance+? WHERE id=?", (s[2], s[0]))
        else:
            c.execute("UPDATE accounts SET balance=balance-? WHERE id=?", (s[2], s[0]))
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status":"healthy","env":os.environ.get("APP_ENV","dev"),
                    "version":os.environ.get("APP_VERSION","1.0.0"),
                    "timestamp":datetime.utcnow().isoformat()+"Z"})

@app.route("/api/stats")
def stats():
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM transactions"); total = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE type='credit'"); credits = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE type='debit'");  debits  = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT account) FROM transactions"); accs = c.fetchone()[0]
    conn.close()
    return jsonify({"total_transactions":total,"total_credits":credits,"total_debits":debits,"active_accounts":accs})

@app.route("/api/accounts")
def accounts():
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT * FROM accounts ORDER BY id")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({"accounts":rows})

@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 50")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({"transactions":rows,"count":len(rows)})

@app.route("/api/transactions", methods=["POST"])
def create_transaction():
    data = request.get_json()
    if not data or not all(k in data for k in ["account","type","amount"]):
        return jsonify({"error":"account, type and amount are required"}), 400
    if data["type"] not in ["credit","debit"]:
        return jsonify({"error":"type must be credit or debit"}), 400
    if float(data["amount"]) <= 0:
        return jsonify({"error":"amount must be positive"}), 400

    conn = get_db(); c = conn.cursor()
    ts = datetime.utcnow().isoformat()+"Z"
    c.execute("INSERT INTO transactions (account,type,amount,description,timestamp) VALUES (?,?,?,?,?)",
        (data["account"], data["type"], float(data["amount"]),
         data.get("description",""), ts))
    txn_id = c.lastrowid
    if data["type"] == "credit":
        c.execute("UPDATE accounts SET balance=balance+? WHERE id=?", (float(data["amount"]), data["account"]))
    else:
        c.execute("UPDATE accounts SET balance=balance-? WHERE id=?", (float(data["amount"]), data["account"]))
    conn.commit()
    txn = dict(c.execute("SELECT * FROM transactions WHERE id=?", (txn_id,)).fetchone())
    conn.close()
    return jsonify({"message":"Transaction created successfully","transaction":txn}), 201

@app.route("/api/transactions/<int:txn_id>")
def get_transaction(txn_id):
    conn = get_db(); c = conn.cursor()
    row = c.fetchone() if (c.execute("SELECT * FROM transactions WHERE id=?", (txn_id,)) or True) else None
    row = c.fetchone()
    conn.close()
    if not row: return jsonify({"error":"Transaction not found"}), 404
    return jsonify(dict(row))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",8080)),
            debug=(os.environ.get("APP_ENV","dev")=="dev"))

# Call init on import (for gunicorn)
init_db()
