"""Explications pédagogiques des options yt-dlp (Q3 : « voir la commande »).

Dictionnaire curaté depuis la doc officielle / cartographie. Partagé par toutes
les interfaces : on n'invente pas les textes, on explique les options réellement
présentes dans la commande construite.
"""
from __future__ import annotations

# flag -> (prend_un_argument, explication)
_EXPLAIN: dict[str, tuple[bool, str]] = {
    "-x": (False, "Extraire uniquement la piste audio (la vidéo est jetée)."),
    "-f": (True, "Sélecteur de format : quelle(s) piste(s) télécharger."),
    "--audio-format": (True, "Convertir l'audio dans ce format (mp3, m4a, opus, flac, wav)."),
    "--audio-quality": (True, "Qualité audio cible : un débit (192K) ou 0 = meilleure."),
    "--merge-output-format": (True, "Conteneur de fusion vidéo+audio (mp4, mkv…)."),
    "-S": (True, "Tri des formats : ici préférer H.264/AAC pour une lecture universelle."),
    "--embed-thumbnail": (False, "Incruster la miniature comme pochette d'album."),
    "--embed-metadata": (False, "Écrire les tags (titre, artiste, date…) dans le fichier."),
    "--no-playlist": (False, "Ne traiter que cette vidéo, pas la playlist entière."),
    "--yes-playlist": (False, "Traiter toute la playlist du lien."),
    "--playlist-items": (True, "Ne prendre que certains éléments (ex. 1-10, 1,3,5, 5:)."),
    "--download-archive": (True, "Journal des vidéos déjà prises : évite de les re-télécharger."),
    "--batch-file": (True, "Lire les liens à télécharger depuis un fichier texte."),
    "--sponsorblock-remove": (True, "Couper les segments SponsorBlock choisis (sponsors, intros…)."),
    "--sponsorblock-mark": (True, "Marquer les segments SponsorBlock en chapitres (sans couper)."),
    "--download-sections": (True, "Ne télécharger qu'un extrait temporel (ex. *1:30-2:45)."),
    "--force-keyframes-at-cuts": (False, "Recouper précisément aux temps demandés (réencodage léger)."),
    "--remux-video": (True, "Changer de conteneur sans réencoder (rapide, sans perte)."),
    "--recode-video": (True, "Réencoder la vidéo dans ce format (plus lent, change le codec)."),
    "--write-thumbnail": (False, "Enregistrer la miniature dans un fichier image séparé."),
    "--write-info-json": (False, "Écrire toutes les infos de la vidéo dans un fichier .json."),
    "--live-from-start": (False, "Télécharger un live depuis son tout début."),
    "--wait-for-video": (True, "Attendre qu'une vidéo/première programmée démarre (intervalle en s)."),
    "--cookies-from-browser": (True, "Réutiliser la session (cookies) d'un navigateur pour l'accès."),
    "--geo-bypass": (False, "Tenter de contourner les blocages géographiques."),
    "--remote-components": (True, "Télécharger le solveur JS officiel (résout le défi anti-robot YouTube)."),
    "--replace-in-metadata": (True, "Nettoyer un champ (ici retirer une extension résiduelle du titre)."),
    "-r": (True, "Limiter le débit de téléchargement (ex. 2M = 2 Mo/s)."),
    "-N": (True, "Nombre de fragments téléchargés en parallèle (plus vite)."),
    "--skip-download": (False, "Ne pas télécharger la vidéo (récupérer seulement les annexes)."),
    "--write-subs": (False, "Récupérer les sous-titres (fichiers séparés)."),
    "--write-auto-subs": (False, "Inclure aussi les sous-titres auto-générés."),
    "--sub-langs": (True, "Langues de sous-titres à récupérer (ex. fr,en ou all)."),
    "--convert-subs": (True, "Convertir les sous-titres dans ce format (srt, vtt…)."),
    "--embed-subs": (False, "Incruster les sous-titres dans le fichier vidéo."),
    "-o": (True, "Modèle de nom/chemin du fichier de sortie."),
}

# Options qui consomment plus d'un argument (défaut : 1 si takes_arg, sinon 0).
_ARG_COUNT = {"--replace-in-metadata": 3}


def explain_command(command: list[str]) -> list[str]:
    """Retourne des lignes 'fragment -> explication' pour la commande donnée."""
    lines: list[str] = []
    i = 1  # on saute le nom du programme (yt-dlp)
    n = len(command)
    while i < n:
        tok = command[i]
        info = _EXPLAIN.get(tok)
        if info is None:
            # Argument positionnel restant (l'URL) ou inconnu.
            if tok.startswith("-"):
                lines.append(f"  {tok}")
            else:
                lines.append(f"  {tok}  →  l'URL à télécharger.")
            i += 1
            continue
        takes_arg, text = info
        nargs = _ARG_COUNT.get(tok, 1 if takes_arg else 0)
        if nargs and i + nargs < n:
            args = " ".join(command[i + 1 : i + 1 + nargs])
            lines.append(f"  {tok} {args}  →  {text}")
            i += 1 + nargs
        else:
            lines.append(f"  {tok}  →  {text}")
            i += 1
    return lines
