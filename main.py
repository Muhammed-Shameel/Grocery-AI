from backend.database.vector_database import VectorDatabase
from backend.retrieval.retriever import Retriever
from backend.prompt_builder.prompt import PromptBuilder
from backend.llm.llm import LLM

db = VectorDatabase()
db.load_data()

retriever = Retriever(db)

prompt_builder = PromptBuilder(retriever)

llm = LLM()

question = input("Ask a question: ")

prompt = prompt_builder.build_prompt(question)

answer = llm.generate(prompt)

print(answer)

