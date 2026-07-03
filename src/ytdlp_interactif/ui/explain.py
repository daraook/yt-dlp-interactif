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
    "-o": (True, "Modèle de nom/chemin du fichier de sortie."),
}


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
        if takes_arg and i + 1 < n:
            lines.append(f"  {tok} {command[i + 1]}  →  {text}")
            i += 2
        else:
            lines.append(f"  {tok}  →  {text}")
            i += 1
    return lines
