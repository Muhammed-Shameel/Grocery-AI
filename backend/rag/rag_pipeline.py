import os
from embedding.chroma_db import ChromaDBManager
from embedding.voyage_embedder import get_embedder
from llm.llm import LLM
from prompt_builder.prompt import PromptBuilder
from retrieval.retriever import Retriever
from rag.context_builder import ContextBuilder
from agents.orchestrator import Orchestrator

class RAGPipeline:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(base_dir, "../data/vector_db"))
        # Embedder is selected via EMBEDDING_PROVIDER (default: voyage API,
        # no local model loaded; falls back to local sentence-transformers).
        self.embedder = get_embedder()
        # Collection is provider-aware: Voyage uses grocery_ai_voyage, local
        # keeps the original grocery_ai collection untouched.
        self.db = ChromaDBManager(db_path=db_path, embedder=self.embedder)
        self.llm = LLM()
        self.retriever = Retriever(self.db, self.embedder)
        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()
        self.orchestrator = Orchestrator(self.retriever, self.context_builder, self.llm)

    def ask(self, question: str, history=None, subject=None, image_data=None):
        # Delegate to the orchestrator agent workflow with strict grounding & subject filtering
        result = self.orchestrator.process_request(question, subject=subject, image_data=image_data, history=history)

        return {
            "question": result["question"],
            "answer": result["answer"],
            "sources": result["sources"],
            "visual_observation": result.get("visual_observation"),
            "grounded": result.get("grounded"),
            "subject": result.get("subject")
        }
