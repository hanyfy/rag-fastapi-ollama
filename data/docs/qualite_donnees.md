# Qualité des données

La qualité des données se décrit par plusieurs dimensions. La complétude mesure la part de valeurs renseignées dans les champs obligatoires. L'unicité vérifie l'absence de doublons : un même prêt ne doit apparaître qu'une fois. La validité contrôle que les valeurs respectent un format ou une plage, par exemple un âge compris entre 18 et 100 ans.

La cohérence vérifie les relations entre champs : une date d'échéance ne peut pas précéder la date d'émission d'un crédit. L'exactitude compare les données à une source de référence. La fraîcheur indique si les données sont assez récentes pour l'usage prévu.

Une bonne pratique consiste à écrire les contrôles comme du code versionné et testé, à les exécuter à chaque chargement, et à faire échouer le pipeline lorsque le taux d'anomalies dépasse un seuil convenu avec les métiers.
