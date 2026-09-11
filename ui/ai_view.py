"""
Central AI Data Analyst View
Interactive conversational intelligence interface with multi-intent classification,
exact SQL evidence grounding, RAG document synthesis, and ML forecasting.
"""

import streamlit as st
import pandas as pd
from ai.analyst import analyze_user_query
from utils.config import OPENAI_API_KEY, GROQ_API_KEY, GEMINI_API_KEY

def render_ai_view():
    st.title("🤖 Unified AI Data Analyst")
    st.caption("Ask natural language business questions. The AI routes dynamically across SQL, RAG documents, and ML forecasts.")
    
    # Optional API key expander
    with st.expander("🔑 Optional: Configure External LLM API Key (OpenAI / Groq)", expanded=False):
        st.markdown("""
        *The platform has a built-in intelligent rule & template reasoning engine that works 100% offline with zero keys.*
        If you wish to use an external cloud LLM (e.g. Llama 3.3 via Groq or GPT-4o-mini via OpenAI) for natural language polish, enter your key below:
        """)
        user_key = st.text_input("API Key (Groq / OpenAI)", type="password", placeholder="gsk_... or sk-...")
        if user_key:
            st.session_state["custom_api_key"] = user_key
            st.success("API key saved in active session.")
            
    active_key = st.session_state.get("custom_api_key", "")
    
    # Suggested quick-click prompt buttons
    st.markdown("##### ⚡ Quick Prompt Starters (Click to Test)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📊 Total Revenue & AOV"):
            st.session_state["user_query_input"] = "What is our total revenue and average order value?"
        if st.button("📦 Best Selling Product"):
            st.session_state["user_query_input"] = "Which product sold the most units?"
    with col2:
        if st.button("🏆 Top Revenue Category"):
            st.session_state["user_query_input"] = "Which category generated the highest revenue?"
        if st.button("🔄 Portfolio Return Rate"):
            st.session_state["user_query_input"] = "What is our overall return rate and financial loss?"
    with col3:
        if st.button("🔮 Next Month Forecast"):
            st.session_state["user_query_input"] = "What will revenue be next month?"
        if st.button("📄 Mobile Return Policy (RAG)"):
            st.session_state["user_query_input"] = "What does the return policy say about Mobiles?"
    with col4:
        if st.button("💡 Why did sales drop? (Hybrid)"):
            st.session_state["user_query_input"] = "Why did sales decrease and what should we do?"
        if st.button("📑 Pricing Strategy (RAG)"):
            st.session_state["user_query_input"] = "What does the uploaded pricing report say?"

    # Input Form
    query_input = st.text_input(
        "Enter your question for the AI Data Analyst:",
        value=st.session_state.get("user_query_input", ""),
        placeholder="e.g., Which category is most profitable and what does our pricing strategy suggest?"
    )
    
    if st.button("🚀 Analyze Query", type="primary") or (query_input and query_input != st.session_state.get("last_processed_query", "")):
        if not query_input.strip():
            st.warning("Please type a question or select a prompt starter.")
            return
            
        st.session_state["last_processed_query"] = query_input
        
        with st.spinner("Analyzing intent, extracting verified facts, and synthesizing response..."):
            result = analyze_user_query(query_input, custom_api_key=active_key)
            
        route = result["route"]
        route_class = {
            "SQL": "badge-sql",
            "RAG": "badge-rag",
            "FORECAST": "badge-forecast",
            "HYBRID": "badge-hybrid"
        }.get(route, "badge-sql")
        
        st.markdown(f"""
            <div style="margin: 14px 0;">
                <span class="{route_class}">Routed to: {route} ENGINE</span>
                &nbsp;&nbsp;<span style="color: #94a3b8; font-size: 0.85rem;">Sources: {', '.join(result.get('sources', []))}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Display formatted structured answer
        st.markdown(result["response"])
        
        # If SQL raw data is available, display an expander
        if "raw_data" in result and result["raw_data"] is not None and not result["raw_data"].empty:
            with st.expander("🔍 View Raw SQL Query Result"):
                st.dataframe(result["raw_data"])
