import json
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate

CLASSIFIER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a banking support triage classifier.\n"
     "Classify the user message into one of:\n"
     "1) feedback_positive\n"
     "2) feedback_negative\n"
     "3) query\n"
     "Return STRICT JSON with keys: label, confidence (0-1), rationale (short).\n"
     "If it expresses praise/thanks -> feedback_positive.\n"
     "If it expresses complaint/frustration -> feedback_negative.\n"
     "If it asks for help/status/how-to -> query."),
    ("human", "{message}")
])

SENTIMENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a sentiment analyzer for banking customer messages.\n"
     "Return STRICT JSON: sentiment (positive|neutral|negative), intensity (0-1), emotions (list), notes (short)."),
    ("human", "{message}")
])

RESPONSE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful banking customer support agent.\n"
     "Use the message classification and sentiment to craft a personalized response.\n"
     "If ticket_action is present, include status/update details.\n"
     "Be empathetic if sentiment is negative.\n"
     "Never invent ticket IDs or private details.\n"
     "Return a clear, concise answer with next steps."),
    ("human",
     "User message: {message}\n\n"
     "Classification: {classification}\n"
     "Sentiment: {sentiment}\n"
     "Ticket action result (optional): {ticket_action}\n")
])

def _safe_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        # best-effort fallback
        return {"raw": text}

def classify_message(llm, message: str) -> Dict[str, Any]:
    resp = llm.invoke(CLASSIFIER_PROMPT.format_messages(message=message))
    return _safe_json(resp.content if hasattr(resp, "content") else str(resp))

def analyze_sentiment(llm, message: str) -> Dict[str, Any]:
    resp = llm.invoke(SENTIMENT_PROMPT.format_messages(message=message))
    return _safe_json(resp.content if hasattr(resp, "content") else str(resp))

def generate_response(llm, user_message: str, classification: Dict[str, Any], sentiment: Dict[str, Any], ticket_action: Optional[Dict[str, Any]]):
    resp = llm.invoke(RESPONSE_PROMPT.format_messages(
        message=user_message,
        classification=json.dumps(classification, indent=2),
        sentiment=json.dumps(sentiment, indent=2),
        ticket_action=json.dumps(ticket_action, indent=2) if ticket_action else "(none)"
    ))
    return resp.content if hasattr(resp, "content") else str(resp)
