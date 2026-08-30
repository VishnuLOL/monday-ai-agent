import streamlit as st
import pandas as pd
from monday_client import MondayClient
from data_cleaner import DataNormalizer
from agent import BIAgent

st.set_page_config(page_title="Monday BI Agent", page_icon="🤖", layout="wide")
st.title("Skylark Drones: BI Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_data(ttl=600)
def load_and_clean_data():
    client = MondayClient()
    cleaner = DataNormalizer()
    
    # YOUR ACTUAL BOARD IDs
    DEALS_BOARD_ID = 5030970514 
    WO_BOARD_ID = 5030970498 
    raw_deals = client.fetch_board_data(DEALS_BOARD_ID)
    deals_df, deals_flags = cleaner.clean_deals(raw_deals)
    
    raw_wo = client.fetch_board_data(WO_BOARD_ID)
    wo_df, wo_flags = cleaner.clean_work_orders(raw_wo)
    
    return deals_df, deals_flags, wo_df, wo_flags

with st.spinner("Syncing live data from Monday.com..."):
    try:
        deals_df, deals_flags, wo_df, wo_flags = load_and_clean_data()
    except Exception as e:
        st.error(f"Failed to connect to Monday.com: {e}. Check API keys and Board IDs.")
        st.stop()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask a question about the business or type /summary..."):
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    agent = BIAgent()
    
    if user_input.strip().lower() == "/summary":
        with st.chat_message("assistant"):
            with st.spinner("Generating leadership update..."):
                # Deterministic Pandas Calculations
                total_pipeline = deals_df['Masked Deal value'].sum() if 'Masked Deal value' in deals_df.columns else 0
                
                stuck_count = 0
                if 'Execution Status' in wo_df.columns:
                    stuck_orders = wo_df[wo_df['Execution Status'].str.contains('Stuck|Pause', na=False, case=False)]
                    stuck_count = len(stuck_orders)
                
                # Generate clean Markdown Executive Memo directly (0 API calls, 0 rate limits)
                summary_text = f"""
### 📊 Executive Leadership Memo

* **Total Pipeline Value:** ₹{total_pipeline:,.2f}
* **Stuck / Paused Work Orders:** {stuck_count} active blockages requiring operational intervention.

> **Operational Risk Assessment:** 
> There are currently **{stuck_count} work orders** marked as stuck or paused in the operations tracker. Immediate cross-referencing with account managers is recommended to clear delivery bottlenecks, protect active revenue, and unblock client deliverables.
                """
                
                st.markdown(summary_text)
                st.session_state.messages.append({"role": "assistant", "content": summary_text})