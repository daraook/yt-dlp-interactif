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
