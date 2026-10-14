import os
from functools import lru_cache
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.chunking import load_chunks
from app.llm import OllamaClient, OllamaError, build_messages
from app.retriever import OllamaEmbeddingRetriever, Retriever, TfidfRetriever

app = FastAPI(title="RAG FastAPI + Ollama", version="0.1.0")

DOCS_DIR = os.getenv("DOCS_DIR", "data/docs")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
RETRIEVER = os.getenv("RETRIEVER", "tfidf")  # tfidf | ollama


class Source(BaseModel):
    ref: str
    score: float
    text: str


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    k: int = Field(default=4, ge=1, le=10)


class AskResponse(BaseModel):
    answer: str
    sources: List[Source]


@lru_cache
def get_retriever() -> Retriever:
    chunks = load_chunks(DOCS_DIR)
    if RETRIEVER == "ollama":
        return OllamaEmbeddingRetriever(chunks, OLLAMA_URL)
    return TfidfRetriever(chunks)


@lru_cache
def get_llm() -> OllamaClient:
    return OllamaClient(OLLAMA_URL, LLM_MODEL)


def _sources(hits) -> List[Source]:
    return [Source(ref=c.ref, score=round(s, 4), text=c.text) for c, s in hits]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/search", response_model=List[Source])
def search(req: AskRequest, retriever: Retriever = Depends(get_retriever)):
    """Recherche seule, sans LLM."""
    return _sources(retriever.search(req.question, req.k))


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, retriever: Retriever = Depends(get_retriever),
        llm: OllamaClient = Depends(get_llm)):
    hits = retriever.search(req.question, req.k)
    if not hits:  # rien de pertinent : on ne sollicite pas le LLM
        return AskResponse(answer="Je ne sais pas d'après les documents fournis.", sources=[])
    try:
        answer = llm.chat(build_messages(req.question, hits))
    except OllamaError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return AskResponse(answer=answer, sources=_sources(hits))
