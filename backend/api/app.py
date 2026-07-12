from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.model import QuestionRequest
from rag.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()
app = FastAPI(
    title="Grocery AI API",
    description="""
    Welcome to the Grocery AI ChatBot! 🍏🥦
    
    You can use this API to ask questions regarding:
    * Fruits
    * Vegetables
    * Milk
    * Eggs
    """,
    version="1.0.0",
    docs_url="/docs"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"Message" : "Welcome To Grocery AI. Head over to /docs to try it out!"}

@app.post("/ask")
def ask(request : QuestionRequest):
    return pipeline.ask(request.question)