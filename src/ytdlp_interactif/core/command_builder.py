"""Construction de la commande yt-dlp pour l'intention « Extraire l'audio ».

Fonction PURE : (choix) -> list[str]. Aucun effet de bord, aucun réseau.
C'est le cœur testable ; les interfaces se contentent de l'appeler.
"""
from __future__ import annotations

from pathlib import Path

# Conteneurs audio qui ne portent pas de pochette incrustée.
_SANS_POCHETTE = {"wav", "flac"}


def build_extract_audio_command(
    url: str,
    output_dir: str | Path,
    *,
    audio_format: str = "mp3",
    audio_quality: str = "192K",
    embed_thumbnail: bool = True,
    embed_metadata: bool = True,
    playlist: bool = False,
    format_selector: str | None = "bestaudio/best",
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Retourne la liste d'arguments prête pour subprocess (voir spec §3).

    `format_selector` (défaut `bestaudio/best`) : ne télécharge que la piste audio
    au lieu de la vidéo complète pour n'en garder que le son. None => yt-dlp décide.
    """
    cmd: list[str] = [yt_dlp, "-x"]
    if format_selector:
        cmd += ["-f", format_selector]
    cmd += ["--audio-format", audio_format]
    cmd += ["--audio-quality", audio_quality]

    # La pochette n'a de sens que pour les formats qui la supportent.
    if embed_thumbnail and audio_format not in _SANS_POCHETTE:
        cmd.append("--embed-thumbnail")
    if embed_metadata:
        cmd.append("--embed-metadata")

    cmd.append("--yes-playlist" if playlist else "--no-playlist")

    template = str(Path(output_dir) / "%(title)s.%(ext)s")
    cmd += ["-o", template, url]
    return cmd
