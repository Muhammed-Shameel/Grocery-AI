from database.vector_database import VectorDatabase
from llm.llm import LLM
from prompt_builder.prompt import PromptBuilder
from retrieval.retriever import Retriever

class RAGPipeline():
    def __init__(self):
        self.db = VectorDatabase()
        self.db.load_data()

        self.retriever = Retriever(self.db)
        self.prompt_builder = PromptBuilder(self.retriever)
        self.llm = LLM()
    
    def ask(self, question):
        top_chunks = self.retriever.retrieve(question)
        prompt = self.prompt_builder.build_prompt(question)
        answer = self.llm.generate(prompt)
        sources = []

        for chunk, score in top_chunks:
            sources.append({
                "article": chunk["article"],
                "section": chunk["section"],
                "score": score
            })
        return {
            "question": question,
            "answer" : answer,
            "sources" : sources
            
        } 
        
