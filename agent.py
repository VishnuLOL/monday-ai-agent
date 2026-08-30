import openai
import os
import json

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_sales_pipeline_metrics",
            "description": "Get aggregated metrics from the Deals board (e.g., total pipeline value, group by stage).",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_by": {"type": "string", "enum": ["Deal Stage", "Sector/service", "Deal Status", "None"]},
                },
                "required": ["group_by"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_work_order_metrics",
            "description": "Get aggregated metrics from the Work Orders board (e.g., execution status, total WO amount).",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_by": {"type": "string", "enum": ["Execution Status", "Sector", "WO Status (billed)", "None"]},
                },
                "required": ["group_by"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cross_reference_deal",
            "description": "Query across BOTH boards to find if a specific deal has both closed revenue and active work orders.",
            "parameters": {
                "type": "object",
                "properties": {
                    "deal_name": {"type": "string", "description": "The normalized name of the deal"}
                },
                "required": ["deal_name"]
            }
        }
    }
]

SYSTEM_PROMPT = """
You are a senior Business Intelligence Agent for the founders of Skylark Drones.
You answer strategic business questions using data from monday.com Deals and Work Orders boards.

CRITICAL RULES:
1. NO GUESSING: If a query is ambiguous (e.g., "how are we doing?"), ask clarifying questions before calling a tool.
2. DATA RESILIENCE: You will receive 'Data Quality Flags' with tool results. You MUST append caveats to your answer if data is incomplete.
3. CONTEXT OVER NUMBERS: Explain the business implication of the metric.
4. CROSS-BOARD QUERIES: If a query requires sales and operations data, use the `cross_reference_deal` tool.
"""

class BIAgent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def process_query(self, user_message: str, chat_history: list):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history
        messages.append({"role": "user", "content": user_message})
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=AGENT_TOOLS,
            tool_choice="auto"
        )
        
        return response.choices[0].message