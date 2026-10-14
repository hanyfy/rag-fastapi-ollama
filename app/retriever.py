"""Recherche de passages. Deux implémentations derrière la même interface :
- TfidfRetriever : local, sans dépendance externe (défaut, utilisé par les tests).
- OllamaEmbeddingRetriever : embeddings via Ollama (ex. nomic-embed-text).
"""
from typing import List, Protocol, Tuple

import httpx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.chunking import Chunk

Hit = Tuple[Chunk, float]


class Retriever(Protocol):
    def search(self, query: str, k: int = 4) -> List[Hit]: ...


def _top_k(chunks: List[Chunk], scores: np.ndarray, k: int) -> List[Hit]:
    order = np.argsort(-scores)[:k]
    return [(chunks[i], float(scores[i])) for i in order if scores[i] > 0]


class TfidfRetriever:
    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks
        self.vec = TfidfVectorizer(strip_accents="unicode", lowercase=True,
                                   ngram_range=(1, 2), sublinear_tf=True)
        self.matrix = self.vec.fit_transform([c.text for c in chunks])

    def search(self, query: str, k: int = 4) -> List[Hit]:
        q = self.vec.transform([query])
        scores = (self.matrix @ q.T).toarray().ravel()  # tf-idf est normalisé L2 : produit scalaire = cosinus
        return _top_k(self.chunks, scores, k)


class OllamaEmbeddingRetriever:
    def __init__(self, chunks: List[Chunk], base_url: str, model: str = "nomic-embed-text",
                 client: httpx.Client | None = None):
        self.chunks, self.model = chunks, model
        self.client = client or httpx.Client(base_url=base_url, timeout=60)
        emb = np.array([self._embed(c.text) for c in chunks])
        self.matrix = emb / np.linalg.norm(emb, axis=1, keepdims=True)

    def _embed(self, text: str) -> List[float]:
        r = self.client.post("/api/embeddings", json={"model": self.model, "prompt": text})
        r.raise_for_status()
        return r.json()["embedding"]

    def search(self, query: str, k: int = 4) -> List[Hit]:
        q = np.array(self._embed(query))
        scores = self.matrix @ (q / np.linalg.norm(q))
        return _top_k(self.chunks, scores, k)
