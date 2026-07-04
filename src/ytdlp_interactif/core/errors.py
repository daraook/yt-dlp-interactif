"""Traduction des erreurs brutes de yt-dlp en messages clairs pour l'utilisateur.

Fonction PURE : (lignes d'erreur) -> message compréhensible (ou None si inconnu).
Testable sans réseau. L'interface affiche ce message et garde le détail technique
disponible à la demande.
"""
from __future__ import annotations

import re

# (motif recherché dans les lignes d'erreur, message clair). Ordre = priorité.
_RULES: list[tuple[str, str]] = [
    (r"is not installed|ffmpeg.*not found|ffprobe.*not found",
     "ffmpeg est requis mais introuvable. Installe-le, puis réessaie."),
    (r"private video|this video is private",
     "Cette vidéo est privée. Essaie l'option « Débloquer » avec les cookies de ton navigateur."),
    (r"members-only|available to this channel's members|join this channel",
     "Contenu réservé aux membres de la chaîne. Essaie « Débloquer » (cookies du navigateur)."),
    (r"confirm your age|age-restricted|inappropriate for some users",
     "Vidéo avec restriction d'âge. Essaie « Débloquer » (cookies du navigateur)."),
    (r"available in your country|geo.?restrict|blocked it in your country|"
     r"not available from your location",
     "Cette vidéo est bloquée dans ta région. Essaie « Débloquer » (contournement géographique)."),
    (r"sign in to confirm|not a bot|cookies",
     "YouTube demande une connexion. Essaie « Débloquer » (cookies du navigateur)."),
    (r"video unavailable|this video is unavailable|has been removed",
     "Cette vidéo n'est pas disponible (supprimée, privée ou bloquée)."),
    (r"requested format is not available|no video formats found",
     "Le format demandé n'est pas disponible pour cette vidéo. Réessaie en « Meilleure qualité »."),
    (r"unsupported url|no video could be found|unable to extract",
     "Ce lien n'est pas reconnu ou ne contient pas de média. Vérifie l'URL."),
    (r"name resolution|failed to resolve|getaddrinfo|network is unreachable|timed out|connection",
     "Problème de connexion réseau. Vérifie ta connexion internet et réessaie."),
    (r"http error 40[13]|forbidden|403|401",
     "Accès refusé par le serveur. Le contenu est peut-être protégé ou nécessite une connexion."),
    (r"http error 404|not found",
     "Contenu introuvable (404). Le lien est peut-être expiré ou incorrect."),
    (r"unable to download webpage",
     "Impossible de charger la page. Vérifie l'URL et ta connexion."),
]


def humanize_error(lines: list[str]) -> str | None:
    """Retourne un message clair correspondant à la première règle qui matche, sinon None."""
    blob = "\n".join(lines).lower()
    for pattern, message in _RULES:
        if re.search(pattern, blob):
            return message
    return None
