import sqlite3
from datetime import datetime
from typing import List, Dict, Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
  ticket_id INTEGER PRIMARY KEY,
  customer_name TEXT,
  issue_type TEXT,
  status TEXT,
  created_at TEXT,
  updated_at TEXT,
  notes TEXT
);
"""

def init_db(db_path: str):
    with sqlite3.connect(db_path) as conn:
        conn.execute(SCHEMA)
        conn.commit()

def seed_demo_data(db_path: str):
    now = datetime.utcnow().isoformat()
    demo = [
        (1001, "Anjali", "Card dispute", "In Progress", now, now, "Merchant dispute filed. Awaiting investigation."),
        (1002, "David", "Transfer pending", "Open", now, now, "IMPS transfer pending verification."),
        (1003, "Ramesh", "Account login", "Resolved", now, now, "Password reset completed; customer confirmed access."),
    ]
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            "INSERT OR REPLACE INTO tickets(ticket_id, customer_name, issue_type, status, created_at, updated_at, notes) VALUES (?,?,?,?,?,?,?)",
            demo
        )
        conn.commit()

def get_ticket(db_path: str, ticket_id: int) -> Dict[str, Any] | None:
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute("SELECT ticket_id, customer_name, issue_type, status, created_at, updated_at, notes FROM tickets WHERE ticket_id=?", (ticket_id,))
        row = cur.fetchone()
        if not row:
            return None
        keys = ["ticket_id","customer_name","issue_type","status","created_at","updated_at","notes"]
        return dict(zip(keys, row))

def update_ticket_status(db_path: str, ticket_id: int, status: str) -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE tickets SET status=?, updated_at=? WHERE ticket_id=?", (status, now, ticket_id))
        conn.commit()
    return {"ticket_id": ticket_id, "updated_status": status}

def create_ticket(db_path: str, customer_name: str, issue_type: str, notes: str="") -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO tickets(customer_name, issue_type, status, created_at, updated_at, notes) VALUES (?,?,?,?,?,?)",
            (customer_name, issue_type, "Open", now, now, notes)
        )
        conn.commit()
        tid = cur.lastrowid
    return {"ticket_id": tid, "status": "Open"}

def list_tickets(db_path: str, limit: int = 50) -> List[Dict[str, Any]]:
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute("SELECT ticket_id, customer_name, issue_type, status, updated_at FROM tickets ORDER BY updated_at DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
    return [dict(ticket_id=r[0], customer_name=r[1], issue_type=r[2], status=r[3], updated_at=r[4]) for r in rows]
