# Spark et Airflow

Apache Spark distribue les traitements sur de gros volumes. Un DataFrame Spark est évalué paresseusement : les transformations ne s'exécutent qu'au moment d'une action comme count ou write. Il faut mettre en cache un DataFrame réutilisé plusieurs fois et surveiller le nombre de partitions lors des jointures et agrégations.

Apache Airflow orchestre des tâches dans des DAG. Chaque tâche doit être idempotente : la relancer ne doit pas dupliquer les résultats. La logique métier doit rester dans du code testé, le DAG se limite à enchaîner les étapes et à gérer les nouvelles tentatives.

Une valeur NaN et une valeur null sont deux choses différentes dans Spark : un contrôle de complétude doit traiter les deux cas.
