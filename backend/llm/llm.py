import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class LLM:
    def __init__(self, model_name="gemini-3.1-flash-lite"):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.model_name = model_name

    def generate(self, prompt):
        if not self.client:
            self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
            if not self.api_key:
                raise ValueError("No GEMINI_API_KEY found. Please set the GEMINI_API_KEY environment variable.")
            self.client = genai.Client(api_key=self.api_key)
        models_to_try = [self.model_name, "gemini-3.1-flash-lite", "gemini-3.5-flash"]
        last_error = None
        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                last_error = e
                continue
        raise last_error
