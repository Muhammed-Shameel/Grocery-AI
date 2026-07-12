from retrieval.retriever import Retriever

class PromptBuilder:

    def __init__(self, retriever):
        self.retriever = retriever

    def build_context(self, question):

        top_chunks = self.retriever.retrieve(question)

        context = ""

        for chunk, _ in top_chunks:

            context += (
                f"{chunk['text']}\n\n"
            )

        return context

    def build_prompt(self, question):

        context = self.build_context(question)

        prompt = f"""
You are a Grocery AI Assistant.

Answer ONLY using the provided context.

Rules:
- Answer only the user's question.
- Keep answers concise.
- Do not include extra information that was not requested.
- Do not explain related facts unless the user asks.
- If the question asks for a single value, return only that value with a short sentence.
- If multiple answers exist, return only those directly relevant to the question.
- If the answer is not in the context, reply:
"I don't have enough information to answer that."

Context:

{context}

Question:
{question}

Answer:
"""

        return prompt 
