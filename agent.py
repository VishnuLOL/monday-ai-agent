import os
import google.generativeai as genai

class BIAgent:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        genai.configure(api_key=api_key)
        
        # Define the tools for Gemini
        self.tools = [
            {
                "function_declarations": [
                    {
                        "name": "get_sales_pipeline_metrics",
                        "description": "Get aggregated metrics from the Deals board (e.g., total pipeline value, group by stage).",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "group_by": {"type": "STRING", "description": "Deal Stage, Sector/service, Deal Status, or None"}
                            },
                            "required": ["group_by"]
                        }
                    },
                    {
                        "name": "get_work_order_metrics",
                        "description": "Get aggregated metrics from the Work Orders board.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "group_by": {"type": "STRING", "description": "Execution Status, Sector, WO Status (billed), or None"}
                            },
                            "required": ["group_by"]
                        }
                    },
                    {
                        "name": "cross_reference_deal",
                        "description": "Query across BOTH boards to find if a specific deal has both closed revenue and active work orders.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "deal_name": {"type": "STRING", "description": "The normalized name of the deal"}
                            },
                            "required": ["deal_name"]
                        }
                    }
                ]
            }
        ]
        
        system_instruction = """
        You are a senior Business Intelligence Agent for the founders of Skylark Drones.
        You answer strategic business questions using data from monday.com Deals and Work Orders boards.
        1. NO GUESSING: If a query is ambiguous, ask clarifying questions before calling a tool.
        2. CONTEXT OVER NUMBERS: Explain the business implication of the metric, don't just output a table.
        """
        
        # Use gemini-1.5-flash (fast, reliable, free tier)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=self.tools,
            system_instruction=system_instruction
        )
        self.chat = self.model.start_chat(enable_automatic_function_calling=False)

    def process_query(self, user_message: str, chat_history: list):
        # Format chat history for Gemini if needed, or send direct message
        response = self.chat.send_message(user_message)
        return response