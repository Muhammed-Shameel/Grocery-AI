from google import genai
from dotenv import load_dotenv
import os

load_dotenv()


class LLM:

    def __init__(
        self,
        model_name="models/gemini-3.5-flash"
    ):
        self.client = genai.Client(
            api_key=os.getenv("API_KEY")
        )
        self.model_name = model_name

    def generate(self, prompt):
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text