import httpx
from fastapi.testclient import TestClient

from app import main
from app.chunking import load_chunks, split_text
from app.llm import OllamaClient, OllamaError, build_messages
from app.retriever import OllamaEmbeddingRetriever, TfidfRetriever

CHUNKS = load_chunks("data/docs")


def test_split_text_respects_max_chars_and_keeps_content():
    text = "Phrase une. " * 100
    pieces = split_text(text, max_chars=200)
    assert all(len(p) <= 200 for p in pieces)
    assert len(pieces) > 1


def test_load_chunks_has_sources_and_refs():
    assert len(CHUNKS) >= 10
    assert CHUNKS[0].ref.endswith("#0")


def test_tfidf_finds_right_document():
    r = TfidfRetriever(CHUNKS)
    top = r.search("Qu'est-ce que le data leakage ?", k=1)[0][0]
    assert top.source == "scoring_credit.md"


def test_tfidf_returns_nothing_for_unrelated_query():
    assert TfidfRetriever(CHUNKS).search("zzzqqq xxxyyy", k=3) == []


def test_prompt_contains_refs_and_question():
    hits = TfidfRetriever(CHUNKS).search("hallucinations RAG", k=2)
    msgs = build_messages("Ma question ?", hits)
    assert msgs[0]["role"] == "system"
    assert hits[0][0].ref in msgs[1]["content"] and "Ma question ?" in msgs[1]["content"]


def _mock_ollama(handler):
    return httpx.Client(base_url="http://ollama", transport=httpx.MockTransport(handler))


def test_ollama_client_parses_chat_response():
    def handler(req):
        assert req.url.path == "/api/chat"
        return httpx.Response(200, json={"message": {"content": "réponse"}})
    assert OllamaClient("http://x", "m", _mock_ollama(handler)).chat([]) == "réponse"


def test_ollama_client_raises_domain_error_when_down():
    def handler(req):
        raise httpx.ConnectError("down")
    try:
        OllamaClient("http://x", "m", _mock_ollama(handler)).chat([])
        assert False
    except OllamaError:
        pass


def test_ollama_embedding_retriever_with_fake_embeddings():
    small = CHUNKS[:3]
    vecs = {c.text: v for c, v in zip(small, ([1.0, 0.0], [0.0, 1.0], [1.0, 1.0]))}

    def handler(req):
        import json
        prompt = json.loads(req.content)["prompt"]
        return httpx.Response(200, json={"embedding": vecs.get(prompt, [0.0, 1.0])})
    r = OllamaEmbeddingRetriever(small, "http://x", client=_mock_ollama(handler))
    assert r.search("n'importe quoi", k=1)[0][0] == small[1]


class FakeLLM:
    def __init__(self, fail=False):
        self.fail, self.calls = fail, 0

    def chat(self, messages):
        self.calls += 1
        if self.fail:
            raise OllamaError("down")
        return "Réponse test [scoring_credit.md#0]"


def _client(llm):
    main.app.dependency_overrides[main.get_retriever] = lambda: TfidfRetriever(CHUNKS)
    main.app.dependency_overrides[main.get_llm] = lambda: llm
    return TestClient(main.app)


def test_health():
    assert TestClient(main.app).get("/health").json() == {"status": "ok"}


def test_ask_returns_answer_and_sources():
    llm = FakeLLM()
    r = _client(llm).post("/ask", json={"question": "Qu'est-ce que le data leakage ?"})
    body = r.json()
    assert r.status_code == 200 and body["answer"].startswith("Réponse test")
    assert body["sources"][0]["ref"].startswith("scoring_credit.md")


def test_ask_does_not_call_llm_without_relevant_context():
    llm = FakeLLM()
    r = _client(llm).post("/ask", json={"question": "zzzqqq xxxyyy"})
    assert r.json()["sources"] == [] and llm.calls == 0


def test_ask_503_when_ollama_down():
    r = _client(FakeLLM(fail=True)).post("/ask", json={"question": "data leakage"})
    assert r.status_code == 503


def test_validation_rejects_short_question():
    assert _client(FakeLLM()).post("/ask", json={"question": "a"}).status_code == 422
