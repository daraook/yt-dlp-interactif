"""Vérification des dépendances externes (yt-dlp, ffmpeg) avant tout lancement.

`which` est injectable pour permettre des tests déterministes sans toucher au PATH.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from typing import Callable

# Message d'installation par dépendance (affiché à l'utilisateur si manquante).
_INSTALL_HINT = {
    "ffmpeg": "ffmpeg est requis pour l'audio. "
              "Linux : sudo apt install ffmpeg · macOS : brew install ffmpeg · "
              "Windows : winget install ffmpeg",
    "yt-dlp": "yt-dlp est requis. Installation : pip install -U yt-dlp",
}


@dataclass(frozen=True)
class EnvReport:
    yt_dlp_ok: bool
    ffmpeg_ok: bool
    missing: list[str]
    message: str

    @property
    def ok(self) -> bool:
        return not self.missing


def js_runtime_tip(
    which: Callable[[str], str | None] = shutil.which,
) -> str | None:
    """Astuce FACULTATIVE (non bloquante) : runtime JS pour YouTube.

    Renvoie None si Deno (utilisé par défaut par yt-dlp) est présent, sinon un
    message informatif proposant — sans imposer — de l'installer.
    """
    if which("deno") is not None:
        return None
    return (
        "💡 Astuce facultative : installer Deno débloque tous les formats YouTube "
        "(4K, AV1) et retire l'avertissement JS. L'outil fonctionne déjà sans.\n"
        "   → curl -fsSL https://deno.land/install.sh | sh"
    )


def check_dependencies(
    which: Callable[[str], str | None] = shutil.which,
) -> EnvReport:
    """Contrôle la présence de yt-dlp et ffmpeg ; renvoie un rapport explicite."""
    yt_dlp_ok = which("yt-dlp") is not None
    ffmpeg_ok = which("ffmpeg") is not None

    missing = [
        name
        for name, present in (("yt-dlp", yt_dlp_ok), ("ffmpeg", ffmpeg_ok))
        if not present
    ]
    if missing:
        message = "Dépendance(s) manquante(s) :\n" + "\n".join(
            f"  - {_INSTALL_HINT[name]}" for name in missing
        )
    else:
        message = "Toutes les dépendances sont présentes."

    return EnvReport(
        yt_dlp_ok=yt_dlp_ok,
        ffmpeg_ok=ffmpeg_ok,
        missing=missing,
        message=message,
    )
