# Principes du RAG

Le RAG (Retrieval-Augmented Generation) combine un moteur de recherche et un modèle de langage. Les documents sont découpés en passages (chunks), transformés en représentations vectorielles, puis indexés. À chaque question, on retrouve les passages les plus proches et on les insère dans le prompt du modèle.

Pour limiter les hallucinations, le prompt demande de répondre uniquement à partir du contexte fourni, de citer les sources et d'indiquer explicitement quand l'information est absente. La taille des chunks est un compromis : trop petits, ils perdent le contexte ; trop grands, ils diluent l'information utile.

L'évaluation d'un système RAG se fait en deux temps. On mesure d'abord la recherche, par exemple la proportion de questions pour lesquelles le bon document figure parmi les k premiers résultats. On évalue ensuite la qualité des réponses générées, ce qui demande une relecture humaine ou un jeu de réponses de référence.
