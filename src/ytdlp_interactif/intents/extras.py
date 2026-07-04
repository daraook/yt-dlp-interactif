"""Orchestration de l'intention « Miniature & métadonnées »."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_extras_command
from ..core.paths import session_dir
from ..core.runner import RunEvent, run


@dataclass
class ExtrasChoices:
    url: str
    media: str = "video"
    write_thumbnail: bool = False
    embed_thumbnail: bool = True
    write_info_json: bool = False
    embed_metadata: bool = True
    skip_download: bool = False
    max_height: int | None = None
    output_dir: Path | None = None


@dataclass(frozen=True)
class ExtrasPlan:
    command: list[str]
    output_dir: Path


def plan_extras(
    choices: ExtrasChoices, *, base: Path | None = None,
    now: datetime | None = None, yt_dlp: str = "yt-dlp",
) -> ExtrasPlan:
    outdir = (Path(choices.output_dir) if choices.output_dir is not None
              else session_dir("extras", base=base, now=now))
    command = build_extras_command(
        choices.url, outdir, media=choices.media,
        write_thumbnail=choices.write_thumbnail,
        embed_thumbnail=choices.embed_thumbnail,
        write_info_json=choices.write_info_json,
        embed_metadata=choices.embed_metadata,
        skip_download=choices.skip_download,
        max_height=choices.max_height, yt_dlp=yt_dlp,
    )
    return ExtrasPlan(command=command, output_dir=outdir)


def run_extras(
    plan: ExtrasPlan, *, popen_factory: Callable | None = None,
    create_dir: bool = True,
) -> Iterator[RunEvent]:
    if create_dir:
        plan.output_dir.mkdir(parents=True, exist_ok=True)
    yield from (run(plan.command) if popen_factory is None
                else run(plan.command, popen_factory=popen_factory))
