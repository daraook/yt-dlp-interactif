"""Recherche via yt-dlp (natif) : renvoie vidéos ET playlists ET chaînes.

On passe l'URL de résultats YouTube à yt-dlp (`--flat-playlist`), son extracteur
`YoutubeSearchURL` renvoie toutes les entrées de la page. `parse_search_results`
est pur (dict -> résultats) ; `search` lance yt-dlp (check_output injectable).
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Callable
from urllib.parse import quote_plus

_RESULTS_URL = "https://www.youtube.com/results?search_query={q}"


@dataclass(frozen=True)
class SearchResult:
    kind: str  # "video" | "playlist" | "channel"
    title: str
    url: str
    subtitle: str  # infos secondaires (chaîne, nb de vidéos, durée…)
    ident: str


def _classify(entry: dict) -> str:
    ie = str(entry.get("ie_key") or entry.get("_type") or "").lower()
    url = entry.get("url") or ""
    ident = entry.get("id") or ""
    if "/channel/" in url or "/@" in url or "/user/" in url or ident.startswith("UC"):
        return "channel"
    if "list=" in url or "playlist" in ie or ident.startswith(
        ("PL", "OLAK", "RD", "FL", "UU", "LL")
    ):
        return "playlist"
    return "video"


def _fmt_duration(sec) -> str:
    if not sec:
        return ""
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def parse_search_results(info: dict) -> list[SearchResult]:
    """Transforme les entrées d'une page de résultats en SearchResult classés."""
    out: list[SearchResult] = []
    for e in info.get("entries") or []:
        if not (e.get("title") and e.get("url")):
            continue
        kind = _classify(e)
        if kind == "playlist":
            n = e.get("playlist_count") or e.get("video_count")
            subtitle = f"Playlist · {n} vidéos" if n else "Playlist"
        elif kind == "channel":
            subtitle = "Chaîne" + (f" · {e['uploader']}" if e.get("uploader") else "")
        else:
            up = e.get("uploader") or e.get("channel") or ""
            dur = _fmt_duration(e.get("duration"))
            subtitle = " · ".join(x for x in (up, dur) if x)
        out.append(SearchResult(
            kind=kind, title=e["title"], url=e["url"],
            subtitle=subtitle, ident=e.get("id", ""),
        ))
    return out


def search(
    query: str,
    *,
    limit: int = 25,
    yt_dlp: str = "yt-dlp",
    check_output: Callable[[list[str]], str] | None = None,
) -> list[SearchResult]:
    """Lance la recherche et renvoie les résultats classés (au plus `limit`)."""
    if check_output is None:
        def check_output(cmd: list[str]) -> str:  # noqa: E306
            return subprocess.check_output(cmd, text=True)

    url = _RESULTS_URL.format(q=quote_plus(query))
    cmd = [yt_dlp, "--flat-playlist", "--no-warnings", "-J",
           "--playlist-end", str(limit), url]
    return parse_search_results(json.loads(check_output(cmd)))
