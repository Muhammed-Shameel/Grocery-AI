from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from rag.rag_pipeline import RAGPipeline

class QuestionRequest(BaseModel):
    question: str
    subject: Optional[str] = None
    history: Optional[List[dict]] = None
    image_data: Optional[str] = None

# Lazily initialized so the process starts fast and only builds the RAG
# stack (ChromaDB + embedder health check) when the first request arrives.
pipeline: Optional[RAGPipeline] = None

def get_pipeline() -> RAGPipeline:
    global pipeline
    if pipeline is None:
        pipeline = RAGPipeline()
    return pipeline
app = FastAPI(
    title="Grocery AI API",
    description="""
    Welcome to the Grocery AI Knowledge Assistant! 🍏🥦
    
    Strictly data-grounded knowledge assistant for fruits, vegetables, milk, and eggs.
    """,
    version="2.0.0",
    docs_url="/docs"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"Message": "Welcome To Grocery AI Knowledge Assistant. Head over to /docs to try it out!"}

@app.get("/subjects")
def get_subjects():
    raw_subjects = get_pipeline().db.get_subjects()
    clean_subjects = [s for s in raw_subjects if s and s.strip() and s.lower() != "unknown"]
    return {"subjects": clean_subjects}

@app.get("/health")
def health():
    p = get_pipeline()
    return {
        "status": "healthy",
        "vector_count": p.db.count(),
        "collection": p.db.collection_name,
        "embedder": type(p.embedder).__name__,
        "subjects_count": len(p.db.get_subjects())
    }

@app.post("/ask")
def ask(request: QuestionRequest):
    return get_pipeline().ask(
        question=request.question,
        history=request.history,
        subject=request.subject,
        image_data=request.image_data
    )
