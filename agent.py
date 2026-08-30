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
            "You are a senior Business Intelligence Agent for Skylark Drones. "
            "Provide clear business context and explanations based on the data."
        )
        
        try:
            self.model = genai.GenerativeModel(
                model_name="gemini-flash-latest",
                system_instruction=system_instruction
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini model: {e}")

    def generate_text(self, prompt: str) -> str:
        try:
            # Generate content with explicit safety/error handling
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                return "Error: Gemini returned an empty response. Please try again."
            return response.text
        except Exception as e:
            return f"API Error during generation: {str(e)}"

    def chat_response(self, user_message: str, data_context: str = "") -> str:
        prompt = f"""
        Context Data from Monday.com Boards:
        {data_context}
        
        User Question: {user_message}
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"API Error during chat: {str(e)}"