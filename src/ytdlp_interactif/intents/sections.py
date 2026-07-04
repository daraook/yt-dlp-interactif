"""Orchestration de l'intention « Découper un extrait »."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_section_command
from ..core.paths import session_dir
from ..core.runner import RunEvent, run


@dataclass
class SectionChoices:
    url: str
    start: str
    end: str
    media: str = "video"  # "video" | "audio"
    max_height: int | None = None
    output_dir: Path | None = None


@dataclass(frozen=True)
class SectionPlan:
    command: list[str]
    output_dir: Path


def plan_section(
    choices: SectionChoices,
    *,
    base: Path | None = None,
    now: datetime | None = None,
    yt_dlp: str = "yt-dlp",
) -> SectionPlan:
    outdir = (
        Path(choices.output_dir)
        if choices.output_dir is not None
        else session_dir("extrait", base=base, now=now)
    )
    command = build_section_command(
        choices.url,
        outdir,
        start=choices.start,
        end=choices.end,
        media=choices.media,
        max_height=choices.max_height,
        yt_dlp=yt_dlp,
    )
    return SectionPlan(command=command, output_dir=outdir)


def run_section(
    plan: SectionPlan,
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
