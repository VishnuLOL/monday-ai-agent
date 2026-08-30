import streamlit as st
import pandas as pd
import json
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

    DEALS_BOARD_ID = "5030970514" 
    WO_BOARD_ID = "5030970498"
    
    raw_deals = client.fetch_board_data(DEALS_BOARD_ID)
    deals_df, deals_flags = cleaner.clean_deals(raw_deals)
    
    raw_wo = client.fetch_board_data(WO_BOARD_ID)
    wo_df, wo_flags = cleaner.clean_work_orders(raw_wo)
    
    return deals_df, deals_flags, wo_df, wo_flags

def execute_tool(tool_call, deals_df, wo_df):
    """Executes the pandas logic mapped to the LLM's chosen tool."""
    name = tool_call.function.name
    try:
        args = json.loads(tool_call.function.arguments)
    except:
        args = {}
        
    if name == "get_sales_pipeline_metrics":
        group_by = args.get("group_by", "None")
        if group_by != "None" and group_by in deals_df.columns:
            return deals_df.groupby(group_by)['Masked Deal value'].sum().to_string()
        return f"Total Pipeline Value: {deals_df['Masked Deal value'].sum():,.2f}"
        
    elif name == "get_work_order_metrics":
        group_by = args.get("group_by", "None")
        if group_by != "None" and group_by in wo_df.columns:
            return wo_df.groupby(group_by)['Amount in Rupees (Excl of GST) (Masked)'].sum().to_string()
        return f"Total WO Amount: {wo_df['Amount in Rupees (Excl of GST) (Masked)'].sum():,.2f}"
        
    elif name == "cross_reference_deal":
        deal = args.get("deal_name", "")
        deal_sales = deals_df[deals_df['Deal Name'].str.contains(deal, case=False, na=False)]
        deal_wo = wo_df[wo_df['Deal name masked'].str.contains(deal, case=False, na=False)]
        
        sales_val = deal_sales['Masked Deal value'].sum() if not deal_sales.empty else 0
        wo_val = deal_wo['Amount in Rupees (Excl of GST) (Masked)'].sum() if not deal_wo.empty else 0
        return f"Found '{deal}'. Pipeline Value: {sales_val:,.2f}. Work Order Value: {wo_val:,.2f}."
    
    return "Error: Tool not recognized."

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
        
    if user_input.strip().lower() == "/summary":
        with st.chat_message("assistant"):
            with st.spinner("Generating leadership update..."):
                total_pipeline = deals_df['Masked Deal value'].sum()
                
                # Check column existence before filtering to avoid crashes if headers map differently
                stuck_count = 0
                if 'Execution Status' in wo_df.columns:
                    stuck_orders = wo_df[wo_df['Execution Status'].str.contains('Stuck|Pause', na=False, case=False)]
                    stuck_count = len(stuck_orders)
                
                agent = BIAgent()
                exec_prompt = (
                    f"Format a brief Markdown Executive Memo. "
                    f"Total Pipeline: {total_pipeline:,.2f}. "
                    f"Stuck/Paused Work Orders: {stuck_count}. "
                    f"Highlight the stuck orders as operational risks."
                )
                
                response = agent.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": exec_prompt}]
                )
                
                summary_text = response.choices[0].message.content
                st.markdown(summary_text)
                st.session_state.messages.append({"role": "assistant", "content": summary_text})
                
    else:
        with st.chat_message("assistant"):
            with st.spinner("Analyzing data..."):
                agent = BIAgent()
                response_message = agent.process_query(user_input, st.session_state.messages)
                
                if response_message.tool_calls:
                    st.markdown("*Querying data boards...*")
                    tool_call = response_message.tool_calls[0]
                    
                    # Execute Pandas logic
                    tool_result = execute_tool(tool_call, deals_df, wo_df)
                    
                    # Send result back to LLM for final generation
                    final_response = agent.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Explain the following data findings to the user naturally."},
                            {"role": "user", "content": f"Tool Result: {tool_result}"}
                        ]
                    ).choices[0].message.content
                    
                    st.markdown(final_response)
                    st.session_state.messages.append({"role": "assistant", "content": final_response})
                else:
                    st.markdown(response_message.content)
                    st.session_state.messages.append({"role": "assistant", "content": response_message.content})