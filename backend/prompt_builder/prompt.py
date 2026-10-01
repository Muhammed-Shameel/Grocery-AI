class PromptBuilder:
    """Builds the final LLM prompt."""
    
    @staticmethod
    def build_prompt(question: str, context: str) -> str:
        """Constructs the prompt for the LLM."""
        return f"""
You are a helpful Grocery AI assistant. Use the following context to answer the question. 
If you cannot answer the question from the context, state that you do not know.

{context}

Question: {question}
Answer:"""
