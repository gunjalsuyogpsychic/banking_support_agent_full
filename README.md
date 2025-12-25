# Banking Customer Support AI Agent (Multi-Agent Architecture)

## What it does
- Classifies incoming messages into feedback_positive, feedback_negative, or query
- Runs sentiment analysis
- Tracks tickets in a SQLite support database (create, status lookup, status update)
- Uses LangGraph to orchestrate multiple specialized agents/tools

## Run locally
```bash
pip install -r requirements.txt
export GROQ_API_KEY="YOUR_KEY"
export LLM_PROVIDER="groq"
streamlit run app.py
```

## Demo
1) Click **Seed demo tickets**
2) Ask:
- "Ticket #1002 status?"
- "Update ticket 1002 to resolved"
- "I am really upset, my transfer is stuck since yesterday."
