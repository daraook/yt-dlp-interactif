# Politique de sécurité

## Périmètre

`yt-dlp interactif` est une **interface** qui construit et exécute des commandes
`yt-dlp`. Il ne comporte ni serveur, ni authentification, ni stockage de données
personnelles. Son unique dépendance Python est `questionary` ; le téléchargement lui-même
est assuré par `yt-dlp` et `ffmpeg`, installés séparément.

Un problème lié au **téléchargement d'un site**, à l'extraction ou à la lecture des cookies
relève de [yt-dlp](https://github.com/yt-dlp/yt-dlp/security), pas de ce dépôt. Merci de le
signaler en amont, au bon endroit.

Relèvent en revanche de **ce** dépôt, par exemple :
- une commande `yt-dlp` construite de façon incorrecte ou dangereuse à partir des choix ;
- une entrée utilisateur mal gérée conduisant à un comportement inattendu ;
- une fuite d'information dans les messages affichés.

## Signaler une vulnérabilité

Merci de **ne pas** ouvrir d'issue publique pour une faille de sécurité.

Utilise l'onglet **Security → Report a vulnerability** du dépôt GitHub
(GitHub Private Vulnerability Reporting). Décris le problème, les étapes de reproduction et
l'impact envisagé. Une réponse est visée sous **7 jours**.

## Versions prises en charge

Seule la dernière version publiée est maintenue. Mets l'outil à jour avant tout signalement
(`pipx upgrade ytdlp-interactif`) et, pour un souci de téléchargement, mets aussi `yt-dlp`
à jour (menu « Mettre à jour yt-dlp »).
