"""Mesure la qualité de la RECHERCHE (hit@k, MRR) sur un petit jeu de questions écrites à la main.
Ne mesure pas la qualité des réponses du LLM."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.chunking import load_chunks  # noqa: E402
from app.retriever import TfidfRetriever  # noqa: E402


def evaluate(retriever, questions, k: int):
    hits, rr = 0, 0.0
    for item in questions:
        sources = [c.source for c, _ in retriever.search(item["q"], k)]
        if item["source"] in sources:
            hits += 1
            rr += 1 / (sources.index(item["source"]) + 1)
    n = len(questions)
    return hits / n, rr / n


if __name__ == "__main__":
    qs = [json.loads(l) for l in Path("eval/questions.jsonl").read_text(encoding="utf-8").splitlines() if l]
    r = TfidfRetriever(load_chunks("data/docs"))
    for k in (1, 3):
        hit, mrr = evaluate(r, qs, k)
        print(f"TF-IDF  k={k}  hit@k={hit:.2f}  MRR={mrr:.2f}  ({len(qs)} questions)")
