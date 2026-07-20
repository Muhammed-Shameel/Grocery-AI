from database.vector_database import VectorDatabase
from llm.llm import LLM
from prompt_builder.prompt import PromptBuilder
from retrieval.retriever import Retriever
from prompt_builder.question_understanding import QuestionUnderstanding
from retrieval.context_selector import ContextSelector
from prompt_builder.llm_analyser import LLMQuestionAnalyzer
from prompt_builder.query_contextualizer import QueryContextualizer


class RAGPipeline:

    def __init__(self):

        self.db = VectorDatabase()

        self.db.load_data()

        self.llm = LLM()

        self.llm_analyzer = (
            LLMQuestionAnalyzer(
                self.llm
            )
        )
        
        self.contextualizer = QueryContextualizer(self.llm)

        self.retriever = Retriever(
            self.db
        )

        self.prompt_builder = (
            PromptBuilder()
        )


    def ask(self, question, history=None):
        # 1. Contextualize the question
        standalone_query = self.contextualizer.contextualize(question, history or [])

        # 2. Analyze the standalone query
        question_understander = (
            QuestionUnderstanding(
                standalone_query,
                self.llm_analyzer
            )
        )

        question_understander.analyze()

        retrieval_query = (
            question_understander.retrieval_query
        )

        top_chunks = (
            self.retriever.retrieve(
                retrieval_query
            )
        )

        context_selector = (
            ContextSelector(
                top_chunks,
                question_understander
            )
        )

        selected_context = (
            context_selector.select_context()
        )

        prompt = (
            self.prompt_builder.build_prompt(
                standalone_query,
                selected_context,
                question_understander
            )
        )

        answer = (
            self.llm.generate(prompt)
        )
        sources = []

        for chunk, score in selected_context:

            sources.append({

                "article": chunk["article"],

                "section": chunk["section"],

                "score": score,
                "category": chunk.get("category", "General"),
                "quality": chunk.get("quality", {"is_clean": True})

            })


        return {

            "question": question,

            "answer": answer,

            "sources": sources

        }
