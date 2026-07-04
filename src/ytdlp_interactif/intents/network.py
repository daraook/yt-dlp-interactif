"""Orchestration de l'intention « Vitesse / réseau »."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_network_command
from ..core.paths import session_dir
from ..core.runner import RunEvent, run


@dataclass
class NetworkChoices:
    url: str
    limit_rate: str | None = None
    concurrent: int = 4
    media: str = "video"
    max_height: int | None = None
    output_dir: Path | None = None


@dataclass(frozen=True)
class NetworkPlan:
    command: list[str]
    output_dir: Path


def plan_network(
    choices: NetworkChoices, *, base: Path | None = None,
    now: datetime | None = None, yt_dlp: str = "yt-dlp",
) -> NetworkPlan:
    outdir = (Path(choices.output_dir) if choices.output_dir is not None
              else session_dir("reseau", base=base, now=now))
    command = build_network_command(
        choices.url, outdir, limit_rate=choices.limit_rate,
        concurrent=choices.concurrent, media=choices.media,
        max_height=choices.max_height, yt_dlp=yt_dlp,
    )
    return NetworkPlan(command=command, output_dir=outdir)


def run_network(
    plan: NetworkPlan, *, popen_factory: Callable | None = None,
    create_dir: bool = True,
) -> Iterator[RunEvent]:
    if create_dir:
        plan.output_dir.mkdir(parents=True, exist_ok=True)
    yield from (run(plan.command) if popen_factory is None
                else run(plan.command, popen_factory=popen_factory))
