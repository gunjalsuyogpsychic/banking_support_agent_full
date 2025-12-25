import streamlit as st
from config import settings
from src.db import init_db, seed_demo_data, list_tickets
from src.orchestrator import build_graph, run_graph

st.set_page_config(page_title="Banking Support AI (Multi-Agent)", layout="wide")
st.title("Banking Customer Support AI Agent — Multi-Agent Architecture")

st.sidebar.header("Settings")
provider = st.sidebar.selectbox("LLM Provider", ["groq", "ollama"], index=0 if settings.LLM_PROVIDER=="groq" else 1)
st.sidebar.caption("Groq needs GROQ_API_KEY. Ollama needs local model.")
st.sidebar.divider()
st.sidebar.code(f"DB: {settings.DB_PATH}")

init_db(settings.DB_PATH)

with st.sidebar.expander("Demo tickets"):
    if st.button("Seed demo tickets"):
        seed_demo_data(settings.DB_PATH)
        st.success("Seeded demo tickets.")

graph = build_graph(provider)

tab1, tab2 = st.tabs(["Assistant", "Ticket Dashboard"])

with tab1:
    st.subheader("Chat")
    msg = st.text_area("Customer message", height=120, placeholder="E.g., My transfer is stuck. Ticket #1023 status?")
    if st.button("Send", type="primary") and msg.strip():
        result = run_graph(graph, msg, db_path=settings.DB_PATH)
        st.markdown("### Classification")
        st.write(result.get("classification"))
        st.markdown("### Sentiment")
        st.write(result.get("sentiment"))
        st.markdown("### Response")
        st.markdown(result.get("final_response", ""))
        if result.get("ticket_action"):
            st.markdown("### Ticket action")
            st.json(result["ticket_action"])

with tab2:
    st.subheader("Tickets")
    rows = list_tickets(settings.DB_PATH, limit=50)
    st.dataframe(rows)
    st.caption("Tip: Ask about 'ticket 1001' etc. Seed demo tickets first for best demo.")
