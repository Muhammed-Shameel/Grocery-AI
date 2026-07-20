"""
query_contextualizer.py

Contextualizes follow-up questions using conversation history to 
create standalone search queries.
"""

class QueryContextualizer:
    def __init__(self, llm):
        self.llm = llm

    def contextualize(self, question, history):
        """
        Rewrites a follow-up question into a standalone query.
        Returns the original question if it is already standalone.
        """
        if not history:
            return question

        # Prepare history for the prompt
        formatted_history = "\n".join(
            [f"User: {msg['user']}\nAssistant: {msg['assistant']}" for msg in history[-3:]]
        )

        prompt = f"""
You are an expert query contextualizer for a Grocery AI Assistant.
Your goal is to ensure the user's follow-up questions are fully understandable without needing previous conversation history.

RULES:
1. If the latest question is standalone, return it as-is.
2. If the latest question is a follow-up (e.g., "What about...", "Is it the same..."), rewrite it by incorporating necessary context from the conversation history to make it a self-contained, complete query.
3. Replace references like "it", "that", "What about milk?" with the specific entity being discussed.
4. Return ONLY the final standalone query. Do not add any conversational filler.

CONVERSATION HISTORY:
{formatted_history}

LATEST QUESTION:
{question}

REWRITTEN STANDALONE QUERY:
"""

        rewritten_query = self.llm.generate(prompt).strip()
        
        print(f"\n--- QUERY CONTEXTUALIZATION ---")
        print(f"Original query: {question}")
        print(f"Contextualized query: {rewritten_query}")
        print(f"-------------------------------\n")
        
        return rewritten_query
