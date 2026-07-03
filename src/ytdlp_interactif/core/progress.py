"""Parsing d'une ligne de sortie yt-dlp en événement de progression.

Le runner lance yt-dlp avec --newline (une mise à jour = une ligne). On ne parse
que les lignes utiles ; le reste renvoie None.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# [download]  42.3% of 10.00MiB at 1.00MiB/s ETA 00:10
_DOWNLOAD_RE = re.compile(r"^\[download\]\s+([\d.]+)%")
# Phases de post-traitement ffmpeg.
_POSTPROC_PREFIXES = ("[ExtractAudio]", "[Merger]", "[EmbedThumbnail]",
                      "[Metadata]", "[FixupM4a]", "[VideoConvertor]")


@dataclass(frozen=True)
class ProgressEvent:
    phase: str            # "download" | "postproc"
    percent: float | None
    raw: str


def parse_progress_line(line: str) -> ProgressEvent | None:
    """Retourne un ProgressEvent, ou None si la ligne n'est pas pertinente."""
    line = line.rstrip("\r\n")

    m = _DOWNLOAD_RE.match(line)
    if m:
        return ProgressEvent(phase="download", percent=float(m.group(1)), raw=line)

    if line.startswith(_POSTPROC_PREFIXES):
        return ProgressEvent(phase="postproc", percent=None, raw=line)

    return None
