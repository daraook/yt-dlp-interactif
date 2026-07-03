"""Orchestration de l'intention « Sous-titres »."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_subtitles_command
from ..core.paths import session_dir
from ..core.runner import RunEvent, run


@dataclass
class SubtitleChoices:
    url: str
    mode: str = "video"  # "video" | "subs_only"
    langs: str = "fr,en"
    auto: bool = True
    sub_format: str = "srt"
    embed: bool = False
    max_height: int | None = None
    output_dir: Path | None = None


@dataclass(frozen=True)
class SubtitlePlan:
    command: list[str]
    output_dir: Path


def plan_subtitles(
    choices: SubtitleChoices,
    *,
    base: Path | None = None,
    now: datetime | None = None,
    yt_dlp: str = "yt-dlp",
) -> SubtitlePlan:
    outdir = (
        Path(choices.output_dir)
        if choices.output_dir is not None
        else session_dir("subs", base=base, now=now)
    )
    command = build_subtitles_command(
        choices.url,
        outdir,
        mode=choices.mode,
        langs=choices.langs,
        auto=choices.auto,
        sub_format=choices.sub_format,
        embed=choices.embed,
        max_height=choices.max_height,
        yt_dlp=yt_dlp,
    )
    return SubtitlePlan(command=command, output_dir=outdir)


def run_subtitles(
    plan: SubtitlePlan,
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
