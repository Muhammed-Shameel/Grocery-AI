from database.vector_database import VectorDatabase
from llm.llm import LLM
from prompt_builder.prompt import PromptBuilder
from retrieval.retriever import Retriever
from prompt_builder.question_understanding import QuestionUnderstanding
from retrieval.context_selector import ContextSelector


class RAGPipeline():

    def __init__(self):

        self.db = VectorDatabase()

        self.db.load_data()
        
        self.retriever = Retriever(self.db)

        self.prompt_builder = PromptBuilder()

        self.llm = LLM()


    def ask(self, question):
        
        question_understander = QuestionUnderstanding(question)
        
        question_understander.analyze()
        
        retrieval_query = question_understander.retrieval_query

        top_chunks = self.retriever.retrieve(retrieval_query)
        
        context_selector = ContextSelector(top_chunks, question_understander)
        
        selected_context = context_selector.select_context()

        prompt = self.prompt_builder.build_prompt(
            question,
            selected_context,
            question_understander
        )

        answer = self.llm.generate(prompt)

        sources = []

        for chunk, score in selected_context:

            sources.append({

                "article": chunk["article"],

                "section": chunk["section"],

                "score": score

            })


        return {

            "question": question,

            "answer": answer,

            "sources": sources

        }