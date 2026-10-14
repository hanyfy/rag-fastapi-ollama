# RAG FastAPI + Ollama

Petit système **RAG** (Retrieval-Augmented Generation) en Python : découpage de documents, recherche, génération avec un LLM local via **Ollama**, exposé par **FastAPI**, conteneurisé avec **Docker**, testé avec **pytest**.

> **EN —** A small Retrieval-Augmented Generation service: Markdown documents are chunked, retrieved (TF-IDF or Ollama embeddings) and passed to a local LLM via Ollama; answers cite their sources. FastAPI, Docker, pytest. Retrieval is evaluated; LLM answer quality is not.

> Les documents de `data/docs/` sont de courts textes **rédigés pour cette démo** (qualité des données, scoring, RAG, Spark/Airflow, confidentialité). Aucune donnée client ni réelle.

## Le problème
Les équipes (conformité, data, support) perdent du temps à chercher dans des documents internes, et un LLM seul **invente** quand il ne sait pas. Un RAG répond à partir des documents, **cite ses sources** et dit « je ne sais pas » quand l'information n'y est pas. Pour des données sensibles, un modèle **local** (Ollama) évite d'envoyer les documents à un service externe.

## Ce que fait le projet
- Découpe les documents, retrouve les passages pertinents, construit un prompt qui impose de répondre uniquement à partir du contexte, et renvoie la réponse avec les passages sources.
- N'appelle pas le LLM quand aucun passage pertinent n'est trouvé, et renvoie une erreur 503 claire si Ollama est indisponible.
- Mesure la qualité de la **recherche** sur un jeu de questions (hit@k, MRR).

## Ce que ça démontre (et ce que ça ne démontre pas)
RAG de bout en bout, API FastAPI testée, intégration Ollama, conteneurisation, évaluation de la recherche. Ce n'est **pas** un système de production : petit corpus, index en mémoire, génération testée avec un faux serveur.

### Exemple réel de recherche
Sortie de la recherche TF-IDF (voir `docs/example_search.json`, générée par le code du dépôt) :
```
Q : « Comment limiter les hallucinations d'un système RAG ? »
 → rag_principes.md#2  (score 0,176) ✔ le bon passage
Q : « Que faire si une clé d'API a été commitée ? »
 → architecture_api.md#0, qualite_donnees.md#3  ✘ le bon document (confidentialite.md) est raté
```
Le second cas est un **échec réel** : le texte parle de secrets « versionnés » et le mot « commitée » n'apparaît pas, TF-IDF ne reconnaît que les mots communs. C'est la raison d'être de l'option `RETRIEVER=ollama` (embeddings sémantiques), non évaluée ici.
Format d'une réponse `/ask` : `{"answer": "…[rag_principes.md#2]", "sources": [{"ref", "score", "text"}]}` (la génération nécessite un Ollama en marche).

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
