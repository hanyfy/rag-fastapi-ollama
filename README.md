# RAG FastAPI + Ollama

Petit système **RAG** (Retrieval-Augmented Generation) en Python : découpage de documents, recherche, génération avec un LLM local via **Ollama**, exposé par **FastAPI**, conteneurisé avec **Docker**, testé avec **pytest**.

> Les documents de `data/docs/` sont de courts textes **rédigés pour cette démo** (qualité des données, scoring, RAG, Spark/Airflow, confidentialité). Aucune donnée client ni réelle.

## Architecture
```
data/docs/*.md ─► chunking (paragraphes, ≤ 500 car.) ─► Retriever ──┐
                                                                    ▼
question ─► POST /ask ─► top-k passages ─► prompt (contexte + sources) ─► Ollama /api/chat ─► réponse + sources
```
- `app/chunking.py` : découpage par paragraphes, avec taille maximale.
- `app/retriever.py` : deux implémentations interchangeables : **TF-IDF** (défaut, local) et **embeddings Ollama** (`RETRIEVER=ollama`, modèle `nomic-embed-text`).
- `app/llm.py` : prompt qui impose de répondre uniquement à partir du contexte, de citer les sources et d'avouer quand l'information manque ; client Ollama.
- `app/main.py` : `GET /health`, `POST /search` (recherche seule), `POST /ask` (RAG complet). Si aucun passage pertinent n'est trouvé, le LLM n'est pas appelé. Si Ollama est indisponible : HTTP 503.

## Lancer
```bash
pip install -r requirements.txt
pytest -q                          # 13 tests, sans Ollama (doublures)
python eval/run_eval.py            # évaluation de la recherche
# avec Ollama installé :
ollama pull llama3.2
uvicorn app.main:app --reload
curl -s localhost:8000/ask -H 'content-type: application/json' \
  -d '{"question":"Comment limiter les hallucinations d un système RAG ?"}'
```
Ou `docker compose up` (puis `docker compose exec ollama ollama pull llama3.2`). Variables : voir `.env.example`.

## Évaluation (recherche uniquement)
`eval/questions.jsonl` : 14 questions écrites à la main, avec le document attendu. Résultat mesuré avec TF-IDF :

| k | hit@k | MRR |
|---|---|---|
| 1 | 0,86 | 0,86 |
| 3 | 0,93 | 0,89 |

À interpréter avec prudence : corpus minuscule (6 documents), questions écrites par l'auteur, donc optimiste par rapport à un cas réel. Cette évaluation **ne mesure pas** la qualité des réponses du LLM.

## Limites
- Le chemin « génération avec Ollama » est testé avec un faux serveur HTTP (`httpx.MockTransport`), **pas** avec un vrai modèle dans ce dépôt ; l'index vit en mémoire (pas de base vectorielle).
- Pas d'authentification ni de limitation de débit.
- Pas de re-ranking ni d'évaluation automatique des réponses générées.
