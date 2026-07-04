"""Orchestration de l'intention « Live / première »."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_live_command
from ..core.paths import session_dir
from ..core.runner import RunEvent, run


@dataclass
class LiveChoices:
    url: str
    from_start: bool = True
    wait: bool = False
    wait_interval: str = "30"
    max_height: int | None = None
    output_dir: Path | None = None


@dataclass(frozen=True)
class LivePlan:
    command: list[str]
    output_dir: Path


def plan_live(
    choices: LiveChoices, *, base: Path | None = None,
    now: datetime | None = None, yt_dlp: str = "yt-dlp",
) -> LivePlan:
    outdir = (Path(choices.output_dir) if choices.output_dir is not None
              else session_dir("live", base=base, now=now))
    command = build_live_command(
        choices.url, outdir, from_start=choices.from_start,
        wait=choices.wait, wait_interval=choices.wait_interval,
        max_height=choices.max_height, yt_dlp=yt_dlp,
    )
    return LivePlan(command=command, output_dir=outdir)


def run_live(
    plan: LivePlan, *, popen_factory: Callable | None = None,
    create_dir: bool = True,
) -> Iterator[RunEvent]:
    if create_dir:
        plan.output_dir.mkdir(parents=True, exist_ok=True)
    yield from (run(plan.command) if popen_factory is None
                else run(plan.command, popen_factory=popen_factory))
