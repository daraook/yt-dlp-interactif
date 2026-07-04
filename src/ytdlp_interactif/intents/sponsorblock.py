"""Orchestration de l'intention « SponsorBlock »."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_sponsorblock_command
from ..core.paths import session_dir
from ..core.runner import RunEvent, run


@dataclass
class SponsorBlockChoices:
    url: str
    action: str = "remove"  # "remove" | "mark"
    categories: str = "sponsor"
    max_height: int | None = None
    output_dir: Path | None = None


@dataclass(frozen=True)
class SponsorBlockPlan:
    command: list[str]
    output_dir: Path


def plan_sponsorblock(
    choices: SponsorBlockChoices,
    *,
    base: Path | None = None,
    now: datetime | None = None,
    yt_dlp: str = "yt-dlp",
) -> SponsorBlockPlan:
    outdir = (
        Path(choices.output_dir)
        if choices.output_dir is not None
        else session_dir("sponsorblock", base=base, now=now)
    )
    command = build_sponsorblock_command(
        choices.url,
        outdir,
        action=choices.action,
        categories=choices.categories,
        max_height=choices.max_height,
        yt_dlp=yt_dlp,
    )
    return SponsorBlockPlan(command=command, output_dir=outdir)


def run_sponsorblock(
    plan: SponsorBlockPlan,
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
