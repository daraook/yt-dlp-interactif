"""Orchestration de l'intention « Télécharger une vidéo (simple) ».

Même structure que extract_audio : `plan_...` pur, `run_...` impur (dossier +
streaming). Préfixe de dossier de session : `video_`.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_download_video_command
from ..core.paths import session_dir
from ..core.runner import RunEvent, run


@dataclass
class VideoChoices:
    url: str
    max_height: int | None = None  # None = meilleure qualité
    merge_format: str = "mp4"
    prefer_compatible: bool = True  # True = H.264/AAC (lit partout)
    embed_thumbnail: bool = False
    embed_metadata: bool = True
    playlist: bool = False
    output_dir: Path | None = None


@dataclass(frozen=True)
class VideoPlan:
    command: list[str]
    output_dir: Path


def plan_download_video(
    choices: VideoChoices,
    *,
    base: Path | None = None,
    now: datetime | None = None,
    yt_dlp: str = "yt-dlp",
) -> VideoPlan:
    outdir = (
        Path(choices.output_dir)
        if choices.output_dir is not None
        else session_dir("video", base=base, now=now)
    )
    command = build_download_video_command(
        choices.url,
        output_dir=outdir,
        max_height=choices.max_height,
        merge_format=choices.merge_format,
        prefer_compatible=choices.prefer_compatible,
        embed_thumbnail=choices.embed_thumbnail,
        embed_metadata=choices.embed_metadata,
        playlist=choices.playlist,
        yt_dlp=yt_dlp,
    )
    return VideoPlan(command=command, output_dir=outdir)


def run_download_video(
    plan: VideoPlan,
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
