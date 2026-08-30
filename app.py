import streamlit as st
import pandas as pd
from monday_client import MondayClient
from data_cleaner import DataNormalizer

st.set_page_config(page_title="Monday BI Agent", page_icon="🤖", layout="wide")
st.title("Skylark Drones: BI Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_data(ttl=600)
def load_and_clean_data():
    client = MondayClient()
    cleaner = DataNormalizer()
    
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

if user_input := st.chat_input("Ask about stuck orders, pipeline, or type /summary..."):
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    agents_input = user_input.strip().lower()
    
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            
            # 1. Handle /summary command
            if agents_input == "/summary":
                total_pipeline = deals_df['Masked Deal value'].sum() if 'Masked Deal value' in deals_df.columns else 0
                
                stuck_count = 0
                if 'Execution Status' in wo_df.columns:
                    stuck_orders = wo_df[wo_df['Execution Status'].str.contains('Stuck|Pause', na=False, case=False)]
                    stuck_count = len(stuck_orders)
                
                response_text = f"""
### 📊 Executive Leadership Memo

* **Total Pipeline Value:** ₹{total_pipeline:,.2f}
* **Stuck / Paused Work Orders:** {stuck_count} active blockages requiring operational intervention.

> **Operational Risk Assessment:** 
> There are currently **{stuck_count} work orders** marked as stuck or paused in the operations tracker. Type **"what are the stuck work orders"** to view the specific accounts and details.
                """
                
            # 2. Handle queries about stuck or paused work orders
            elif "stuck" in agents_input or "paused" in agents_input:
                if 'Execution Status' in wo_df.columns:
                    stuck_df = wo_df[wo_df['Execution Status'].str.contains('Stuck|Pause', na=False, case=False)]
                    if not stuck_df.empty:
                        response_text = f"### ⚠️ Stuck / Paused Work Orders Found ({len(stuck_df)}): \n\n"
                        for idx, row in stuck_df.iterrows():
                            deal_name = row.get('Deal name masked', row.get('item_name', 'Unknown Deal'))
                            status = row.get('Execution Status', 'Stuck/Paused')
                            sector = row.get('Sector', 'N/A')
                            response_text += f"- **Deal/Client:** {deal_name} | **Sector:** {sector} | **Status:** `{status}`\n"
                    else:
                        response_text = "No work orders are currently marked as stuck or paused in the dataset."
                else:
                    response_text = "The 'Execution Status' column is not available in the current work order dataset view."
                    
            # 3. Handle pipeline / deal queries
            elif "pipeline" in agents_input or "deal" in agents_input:
                total_pipeline = deals_df['Masked Deal value'].sum() if 'Masked Deal value' in deals_df.columns else 0
                response_text = f"### 💰 Sales Pipeline Overview\n- **Total Pipeline Value:** ₹{total_pipeline:,.2f}\n- **Total Deals Tracked:** {len(deals_df)}"
                
            # 4. Fallback general response
            # 4. Fallback general response
            else:
                response_text = f"I've analyzed your Monday.com boards ({len(deals_df)} deals, {len(wo_df)} work orders). Try typing **`/summary`** for the executive report or ask **'what are the stuck work orders'** to see operational bottlenecks."


            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})