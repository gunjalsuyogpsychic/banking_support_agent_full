import re
from typing import Dict, Any, Optional
from src.db import get_ticket, update_ticket_status, create_ticket

def parse_ticket_request(message: str) -> Optional[Dict[str, Any]]:
    """
    Extracts ticket-related intents from message.
    Supports:
      - status request: "ticket 1002 status", "#1002", "Ticket #1002"
      - update: "update ticket 1002 to resolved"
      - create: "create ticket for transfer failure"
    """
    msg = message.strip()

    # Update intent
    m_upd = re.search(r"(update|set)\s+(ticket\s*)?#?(\d+)\s+(to\s+)?(open|in progress|resolved|closed)", msg, re.IGNORECASE)
    if m_upd:
        return {"action": "update_status", "ticket_id": int(m_upd.group(3)), "status": m_upd.group(5).title()}

    # Status intent
    m_stat = re.search(r"(ticket\s*)?#?(\d+)", msg, re.IGNORECASE)
    if m_stat and re.search(r"status|update|progress|what(?:'s)?\s+happening", msg, re.IGNORECASE):
        return {"action": "get_status", "ticket_id": int(m_stat.group(2))}

    # Create intent (simple)
    if re.search(r"\bcreate\b.*\bticket\b|\bopen\b.*\bticket\b", msg, re.IGNORECASE):
        issue = "General"
        m_issue = re.search(r"ticket\s+(for|about)\s+(.+)", msg, re.IGNORECASE)
        if m_issue:
            issue = m_issue.group(2)[:80]
        return {"action": "create", "customer_name": "Customer", "issue_type": issue, "notes": msg[:200]}

    return None

def handle_ticket_request(db_path: str, req: Dict[str, Any]) -> Dict[str, Any]:
    action = req.get("action")
    if action == "get_status":
        tid = req["ticket_id"]
        ticket = get_ticket(db_path, tid)
        if not ticket:
            return {"action": "get_status", "ticket_id": tid, "found": False, "message": "Ticket not found."}
        return {"action": "get_status", "found": True, "ticket": ticket}

    if action == "update_status":
        tid = req["ticket_id"]
        status = req["status"]
        ticket = get_ticket(db_path, tid)
        if not ticket:
            return {"action": "update_status", "ticket_id": tid, "found": False, "message": "Ticket not found."}
        upd = update_ticket_status(db_path, tid, status)
        return {"action": "update_status", "found": True, **upd}

    if action == "create":
        created = create_ticket(db_path, req.get("customer_name","Customer"), req.get("issue_type","General"), req.get("notes",""))
        return {"action": "create", "created": True, **created}

    return {"action": action, "message": "No action performed."}
