"""Orchestration de l'intention « Débloquer (cookies navigateur / géo / âge) »."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_unlock_command
from ..core.paths import session_dir
from ..core.runner import RunEvent, run


@dataclass
class UnlockChoices:
    url: str
    browser: str = "firefox"
    geo_bypass: bool = False
    media: str = "video"
    max_height: int | None = None
    output_dir: Path | None = None


@dataclass(frozen=True)
class UnlockPlan:
    command: list[str]
    output_dir: Path


def plan_unlock(
    choices: UnlockChoices, *, base: Path | None = None,
    now: datetime | None = None, yt_dlp: str = "yt-dlp",
) -> UnlockPlan:
    outdir = (Path(choices.output_dir) if choices.output_dir is not None
              else session_dir("prive", base=base, now=now))
    command = build_unlock_command(
        choices.url, outdir, browser=choices.browser,
        geo_bypass=choices.geo_bypass, media=choices.media,
        max_height=choices.max_height, yt_dlp=yt_dlp,
    )
    return UnlockPlan(command=command, output_dir=outdir)


def run_unlock(
    plan: UnlockPlan, *, popen_factory: Callable | None = None,
    create_dir: bool = True,
) -> Iterator[RunEvent]:
    if create_dir:
        plan.output_dir.mkdir(parents=True, exist_ok=True)
    yield from (run(plan.command) if popen_factory is None
                else run(plan.command, popen_factory=popen_factory))
