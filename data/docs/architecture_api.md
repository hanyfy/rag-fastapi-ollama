# Exposer un modèle ou un pipeline via une API

FastAPI permet de décrire des endpoints Python typés et génère automatiquement la documentation OpenAPI. Les schémas Pydantic valident les entrées et sorties. Un endpoint de santé (health) permet aux orchestrateurs de savoir si le service est prêt.

Le service est conteneurisé avec Docker pour garantir un environnement reproductible. Les secrets ne sont jamais écrits dans le code ni dans l'image : ils sont fournis par variables d'environnement. Les tests d'API utilisent un client de test et remplacent les dépendances externes par des doublures.

Un pipeline d'intégration continue exécute les tests à chaque commit. Un échec de test bloque la fusion de la branche.
