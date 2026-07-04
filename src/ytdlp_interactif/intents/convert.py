"""Orchestration de l'intention « Convertir / changer de format »."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_convert_command
from ..core.paths import session_dir
from ..core.runner import RunEvent, run


@dataclass
class ConvertChoices:
    url: str
    target_ext: str = "mp4"
    recode: bool = False
    max_height: int | None = None
    output_dir: Path | None = None


@dataclass(frozen=True)
class ConvertPlan:
    command: list[str]
    output_dir: Path


def plan_convert(
    choices: ConvertChoices, *, base: Path | None = None,
    now: datetime | None = None, yt_dlp: str = "yt-dlp",
) -> ConvertPlan:
    outdir = (Path(choices.output_dir) if choices.output_dir is not None
              else session_dir("converti", base=base, now=now))
    command = build_convert_command(
        choices.url, outdir, target_ext=choices.target_ext,
        recode=choices.recode, max_height=choices.max_height, yt_dlp=yt_dlp,
    )
    return ConvertPlan(command=command, output_dir=outdir)


def run_convert(
    plan: ConvertPlan, *, popen_factory: Callable | None = None,
    create_dir: bool = True,
) -> Iterator[RunEvent]:
    if create_dir:
        plan.output_dir.mkdir(parents=True, exist_ok=True)
    yield from (run(plan.command) if popen_factory is None
                else run(plan.command, popen_factory=popen_factory))
