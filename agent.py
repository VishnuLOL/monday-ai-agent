import os
import google.generativeai as genai
import streamlit as st

class BIAgent:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets.get("GEMINI_API_KEY")
            except Exception:
                pass
                
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set. Please add it to Streamlit Secrets or environment variables.")
            
        genai.configure(api_key=api_key)
        
        system_instruction = (
            "You are a senior Business Intelligence Agent for the founders of Skylark Drones. "
            "You answer strategic business questions using data from monday.com Deals and Work Orders boards. "
            "Always provide clear business context and explanations, not just raw numbers."
        )
        
        # Using gemini-1.5-flash for fast, free-tier responses
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )

    def generate_text(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def chat_response(self, user_message: str, data_context: str = "") -> str:
        prompt = f"""
        Context Data from Monday.com Boards:
        {data_context}
        
        User Question: {user_message}
        """
        response = self.model.generate_content(prompt)
        return response.text