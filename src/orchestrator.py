from typing import TypedDict, Optional, Dict, Any
import re

from langgraph.graph import StateGraph, END

from src.llm import get_llm
from src.tools import classify_message, analyze_sentiment, generate_response
from src.ticket_agent import parse_ticket_request, handle_ticket_request

class AgentState(TypedDict, total=False):
    user_message: str
    classification: Dict[str, Any]
    sentiment: Dict[str, Any]
    ticket_action: Optional[Dict[str, Any]]
    final_response: str
    db_path: str

def node_classify(state: AgentState, llm):
    return {"classification": classify_message(llm, state["user_message"])}

def node_sentiment(state: AgentState, llm):
    return {"sentiment": analyze_sentiment(llm, state["user_message"])}

def node_ticket(state: AgentState):
    req = parse_ticket_request(state["user_message"])
    if not req:
        return {"ticket_action": None}
    action = handle_ticket_request(state["db_path"], req)
    return {"ticket_action": action}

def node_respond(state: AgentState, llm):
    return {"final_response": generate_response(
        llm=llm,
        user_message=state["user_message"],
        classification=state.get("classification", {}),
        sentiment=state.get("sentiment", {}),
        ticket_action=state.get("ticket_action")
    )}

def route_after_classify(state: AgentState):
    """
    If it's a query and mentions ticket, run ticket node. Otherwise skip to respond.
    """
    cls = state.get("classification", {})
    label = cls.get("label", "query")
    if label == "query":
        if re.search(r"\bticket\b|#", state["user_message"], re.IGNORECASE):
            return "ticket"
    return "sentiment"

def build_graph(provider: str):
    llm = get_llm(provider)

    g = StateGraph(AgentState)
    g.add_node("classify", lambda s: node_classify(s, llm))
    g.add_node("sentiment", lambda s: node_sentiment(s, llm))
    g.add_node("ticket", node_ticket)
    g.add_node("respond", lambda s: node_respond(s, llm))

    g.set_entry_point("classify")
    g.add_conditional_edges("classify", route_after_classify, {"ticket": "ticket", "sentiment": "sentiment"})
    g.add_edge("ticket", "sentiment")
    g.add_edge("sentiment", "respond")
    g.add_edge("respond", END)

    return g.compile()

def run_graph(graph, user_message: str, db_path: str):
    state: AgentState = {"user_message": user_message, "db_path": db_path}
    return graph.invoke(state)
