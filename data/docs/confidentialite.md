# Confidentialité et données sensibles

Les données bancaires ou médicales sont sensibles. On applique le principe de minimisation : ne collecter et ne conserver que ce qui est nécessaire. Les environnements de développement et de démonstration utilisent des données synthétiques ou publiques, jamais des extraits de production.

Les identifiants, mots de passe et clés d'API ne doivent jamais être versionnés. Un secret commité reste lisible dans l'historique du dépôt : il faut le révoquer, pas seulement le supprimer du dernier commit. Un fichier de configuration d'exemple (.env.example) documente les variables sans contenir de valeur réelle.
