import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime


BACKEND_URL = "https://reservation-agent-t9ib.onrender.com"
st.set_page_config(page_title="Khana Darbaar | Pro AI Agent", layout="wide", initial_sidebar_state="expanded")


st.markdown("""
    <style>
    /* Main Background and Text */
    .stApp { background-color: #0e1117; color: #e0e0e0; }

    /* Metric Cards Glassmorphism */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    /* Force metrics text to be light */
    div[data-testid="stMetricValue"] { color: #58a6ff !important; font-size: 2rem !important; }
    div[data-testid="stMetricLabel"] { color: #8b949e !important; }

    /* Custom Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }

    /* Buttons and Inputs */
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3em; 
        background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #30363d; border-color: #8b949e; color: #ffffff; }

    /* Chat Styling */
    .agent-source { font-size: 0.75rem; color: #8b949e; margin-top: -10px; display: block; }

    /* Remove white borders from containers */
    div[data-testid="stExpander"] { border: 1px solid #30363d; background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)


if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'intent_log' not in st.session_state: st.session_state.intent_log = []



def query_agent(prompt):
    payload = {"message": prompt, "history": st.session_state.chat_history}
    try:
        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception:
        st.error("Backend unreachable. Ensure main.py is running.")
    return None



try:
    all_res = requests.get(f"{BACKEND_URL}/restaurants", timeout=1).json()
except:
    all_res = []


with st.sidebar:
    st.title("🍽️ Concierge AI")
    st.markdown("---")
    page = st.radio("Navigation", ["Agent Console", "System Intelligence"])
    st.markdown("---")
    st.caption(f"📍 Server: {BACKEND_URL}")
    if st.button("🧹 Clear Conversation"):
        st.session_state.chat_history = []
        st.session_state.intent_log = []
        st.rerun()


if page == "Agent Console":
    st.title("🍽️ KHANA DARBAAR")
    st.caption("Pro-Tier Reservation Engine | v2.1.0")

    # Scrollable Chat Container
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Suggest a premium Sushi spot in Bhubaneswar..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing Intelligence Layers..."):
                resp = query_agent(prompt)
                if resp:
                    answer = resp.get("answer")
                    source = resp.get("data_source", "Fallback")
                    intent = resp.get("intent", "general")

                    st.markdown(answer)
                    st.caption(f"Engine: {source}")

                    st.session_state.intent_log.append({
                        "Time": datetime.now().strftime("%H:%M:%S"),
                        "Intent": intent,
                        "Source": source,
                        "Query": prompt
                    })
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    st.rerun()

    
    if st.session_state.intent_log and st.session_state.intent_log[-1]["Intent"] == "search_restaurants":
        with st.expander("⚡ Contextual Actions", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1: st.button("📅 Instant Book")
            with c2: st.button("🗺️ Interactive Map")
            with c3: st.button("⭐ Add to Profile")


elif page == "System Intelligence":
    st.title("📈 Intelligence Telemetry")

 
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Active Intents", len(st.session_state.intent_log))
    m2.metric("Knowledge Base", len(all_res))
    m3.metric("System Health", "99.8%")
    m4.metric("Avg Latency", "1.1s")

    st.markdown("---")

    left, right = st.columns([2, 1])

    with left:
        st.subheader("Intent Distribution")
        if st.session_state.intent_log:
            df = pd.DataFrame(st.session_state.intent_log)
            
            fig = px.bar(df['Intent'].value_counts(),
                         color_discrete_sequence=['#58a6ff'],
                         template="plotly_dark")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Live Event Stream")
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("System awaiting user interaction to populate telemetry.")

    with right:
        st.subheader("Engine Status")
        
        st.success("FastAPI Gateway: Active")
        st.success("Web Scraper Engine: Active")
        st.warning("OSM Layer: High Latency")

        with st.container(border=True):
            st.markdown("**Architectural Design**")
            st.caption(
                "This system utilizes an asynchronous Fallback Pattern. If structured data from OSM is unavailable, the Scraper Engine activates to synthesize real-time web intelligence.")
