# Scoring de crédit

Un score de crédit estime la probabilité qu'un emprunteur ne rembourse pas son prêt. Les modèles classiques utilisent la régression logistique car elle est simple à interpréter et à expliquer à un régulateur. Les modèles à base d'arbres boostés sont souvent plus performants mais demandent des outils d'explicabilité.

La construction des variables (feature engineering) s'appuie sur des règles métier : taux d'endettement, stabilité des revenus, ancienneté de la relation bancaire, incidents de paiement passés. Il faut éviter les fuites de données (data leakage) : une variable calculée après la décision d'octroi ne doit jamais entrer dans le modèle.

La performance se mesure avec l'AUC et l'indice de Gini, mais aussi avec la stabilité dans le temps (PSI). Un modèle doit être surveillé après sa mise en production car la population des emprunteurs évolue.
