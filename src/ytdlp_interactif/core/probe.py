"""Inspection des formats réels d'une URL via `yt-dlp -J` (« regarder avant d'agir »).

`parse_formats` et les helpers sont PURS (dict -> données), testables sans réseau.
`probe_formats` lance yt-dlp ; son `check_output` est injectable pour les tests.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class FormatInfo:
    format_id: str
    ext: str
    height: int | None
    fps: float | None
    vcodec: str  # "none" si piste audio seule
    acodec: str  # "none" si piste vidéo seule
    filesize: int | None
    tbr: float | None
    note: str

    @property
    def has_video(self) -> bool:
        return self.vcodec != "none"

    @property
    def has_audio(self) -> bool:
        return self.acodec != "none"

    @property
    def is_audio_only(self) -> bool:
        return not self.has_video and self.has_audio


def parse_formats(info: dict) -> list[FormatInfo]:
    """Transforme le JSON `-J` en liste de FormatInfo (storyboards/images exclus)."""
    out: list[FormatInfo] = []
    for f in info.get("formats", []):
        vcodec = f.get("vcodec") or "none"
        acodec = f.get("acodec") or "none"
        if vcodec == "none" and acodec == "none":
            continue  # storyboard / image, sans intérêt
        out.append(
            FormatInfo(
                format_id=str(f.get("format_id", "")),
                ext=f.get("ext", ""),
                height=f.get("height"),
                fps=f.get("fps"),
                vcodec=vcodec,
                acodec=acodec,
                filesize=f.get("filesize") or f.get("filesize_approx"),
                tbr=f.get("tbr"),
                note=f.get("format_note", ""),
            )
        )
    return out


def video_heights(formats: list[FormatInfo]) -> list[int]:
    """Résolutions vidéo distinctes présentes, décroissantes."""
    heights = {f.height for f in formats if f.has_video and f.height}
    return sorted(heights, reverse=True)


def best_audio_size(formats: list[FormatInfo]) -> int | None:
    """Plus grande taille connue parmi les pistes audio seules."""
    sizes = [f.filesize for f in formats if f.is_audio_only and f.filesize]
    return max(sizes) if sizes else None


def approx_size_for_height(formats: list[FormatInfo], height: int) -> int | None:
    """Taille approximative du fichier final pour une résolution donnée.

    Format combiné (audio inclus) -> sa taille seule. Sinon vidéo + meilleur audio.
    None si la taille est inconnue.
    """
    vids = [f for f in formats if f.has_video and f.height == height]
    sizes = [f.filesize for f in vids if f.filesize]
    if not sizes:
        return None
    vsize = max(sizes)
    if any(f.has_audio for f in vids):
        return vsize
    audio = best_audio_size(formats)
    return vsize + audio if audio else None


def probe_formats(
    url: str,
    *,
    yt_dlp: str = "yt-dlp",
    check_output: Callable[[list[str]], str] | None = None,
) -> list[FormatInfo]:
    """Lance `yt-dlp -J` sur l'URL et renvoie les formats analysés."""
    if check_output is None:
        def check_output(cmd: list[str]) -> str:  # noqa: E306
            return subprocess.check_output(cmd, text=True)

    cmd = [yt_dlp, "-J", "--no-warnings", "--no-playlist", url]
    raw = check_output(cmd)
    return parse_formats(json.loads(raw))
