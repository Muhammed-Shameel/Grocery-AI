import json


class LLMQuestionAnalyzer:

    def __init__(self, llm):
        self.llm = llm

    def analyze(self, question):

        prompt = f"""
You are a question analysis component for a Grocery AI Assistant.

Analyze the user's question and return ONLY valid JSON.

The analysis must use ONLY the following allowed values.

Allowed intents:
- nutrient
- storage
- safety
- preparation
- quality
- ingredient
- benefit
- general

Allowed operations:
- lookup
- comparison
- instruction
- explanation
- safety
- general

The following fields are required:

{{
    "intents": [],
    "attributes": [],
    "entities": [],
    "operations": []
}}

Rules:

- Extract the food or grocery products mentioned as entities.
- Extract the specific information being asked about as attributes.
- Determine the main topic or topics as intents.
- Determine what the user wants to do as operations.
- Use multiple values when the question contains multiple topics.
- Do not invent entities that are not present or clearly implied by the question.
- Do not answer the question.
- Return JSON only.
- Do not include markdown.
- Do not include explanations.

User question:

{question}
"""

        response = self.llm.generate(prompt)

        try:

            analysis = json.loads(response)

            return analysis

        except json.JSONDecodeError:

            return {
                "intents": ["general"],
                "attributes": [],
                "entities": [],
                "operations": ["general"]
            }