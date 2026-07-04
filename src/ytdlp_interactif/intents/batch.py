"""Orchestration de l'intention « Fichier de liens (lot) »."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_batch_command
from ..core.paths import session_dir
from ..core.runner import RunEvent, run


@dataclass
class BatchChoices:
    urls: list[str] | None = None
    batch_file: Path | None = None
    media: str = "video"  # "video" | "audio"
    max_height: int | None = None
    output_dir: Path | None = None


@dataclass(frozen=True)
class BatchPlan:
    command: list[str]
    output_dir: Path


def plan_batch(
    choices: BatchChoices,
    *,
    base: Path | None = None,
    now: datetime | None = None,
    yt_dlp: str = "yt-dlp",
) -> BatchPlan:
    outdir = (
        Path(choices.output_dir)
        if choices.output_dir is not None
        else session_dir("lot", base=base, now=now)
    )
    command = build_batch_command(
        outdir,
        urls=choices.urls,
        batch_file=choices.batch_file,
        media=choices.media,
        max_height=choices.max_height,
        yt_dlp=yt_dlp,
    )
    return BatchPlan(command=command, output_dir=outdir)


def run_batch(
    plan: BatchPlan,
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
