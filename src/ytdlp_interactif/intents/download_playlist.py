"""Orchestration de l'intention « Télécharger une playlist / chaîne ».

Particularité : dossier de sortie STABLE (`.../playlists`, non horodaté) pour que
l'archive anti-doublon persiste entre exécutions — relancer reprend là où on en était.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_playlist_command
from ..core.paths import library_dir
from ..core.runner import RunEvent, run


@dataclass
class PlaylistChoices:
    url: str
    media: str = "video"  # "video" | "audio"
    max_height: int | None = None
    prefer_compatible: bool = True
    merge_format: str = "mp4"
    audio_format: str = "mp3"
    audio_quality: str = "192K"
    items: str | None = None
    archive: bool = True
    output_dir: Path | None = None


@dataclass(frozen=True)
class PlaylistPlan:
    command: list[str]
    output_dir: Path


def plan_download_playlist(
    choices: PlaylistChoices,
    *,
    base: Path | None = None,
    yt_dlp: str = "yt-dlp",
) -> PlaylistPlan:
    outdir = (
        Path(choices.output_dir)
        if choices.output_dir is not None
        else library_dir("playlists", base=base)
    )
    command = build_playlist_command(
        choices.url,
        outdir,
        media=choices.media,
        max_height=choices.max_height,
        prefer_compatible=choices.prefer_compatible,
        merge_format=choices.merge_format,
        audio_format=choices.audio_format,
        audio_quality=choices.audio_quality,
        items=choices.items,
        archive=choices.archive,
        yt_dlp=yt_dlp,
    )
    return PlaylistPlan(command=command, output_dir=outdir)


def run_download_playlist(
    plan: PlaylistPlan,
    *,
    popen_factory: Callable | None = None,
    create_dir: bool = True,
) -> Iterator[RunEvent]:
    if create_dir:
        plan.output_dir.mkdir(parents=True, exist_ok=True)
    if popen_factory is None:
        yield from run(plan.command)
    else:
        yield from run(plan.command, popen_factory=popen_factory)
