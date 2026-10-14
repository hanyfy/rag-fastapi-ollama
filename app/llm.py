"""Client Ollama (chat) + construction du prompt RAG."""
from typing import List

import httpx

from app.retriever import Hit

SYSTEM = (
    "Tu es un assistant qui répond en français uniquement à partir du CONTEXTE fourni. "
    "Cite les sources entre crochets, par exemple [rag_principes.md#1]. "
    "Si le contexte ne contient pas la réponse, dis exactement : « Je ne sais pas d'après les documents fournis. »"
)


def build_messages(question: str, hits: List[Hit]) -> List[dict]:
    context = "\n\n".join(f"[{c.ref}] {c.text}" for c, _ in hits)
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"CONTEXTE:\n{context}\n\nQUESTION: {question}"},
    ]


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, base_url: str, model: str, client: httpx.Client | None = None):
        self.model = model
        self.client = client or httpx.Client(base_url=base_url, timeout=120)

    def chat(self, messages: List[dict]) -> str:
        try:
            r = self.client.post("/api/chat", json={"model": self.model, "messages": messages,
                                                    "stream": False, "options": {"temperature": 0.1}})
            r.raise_for_status()
            return r.json()["message"]["content"]
        except (httpx.HTTPError, KeyError) as e:
            raise OllamaError(f"Ollama indisponible ou réponse invalide : {e}") from e
