"""Orchestration de l'intention « Personnalisé » (combos arbitraires)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_custom_command
from ..core.paths import session_dir
from ..core.runner import RunEvent, run


@dataclass
class CustomChoices:
    url: str
    media: str = "video"
    max_height: int | None = None
    prefer_compatible: bool = True
    playlist: bool = False
    playlist_items: str | None = None
    section: tuple[str, str] | None = None
    sponsorblock_categories: str | None = None
    sub_langs: str | None = None
    embed_subs: bool = False
    cookies_browser: str | None = None
    limit_rate: str | None = None
    concurrent: int = 4
    output_dir: Path | None = None


@dataclass(frozen=True)
class CustomPlan:
    command: list[str]
    output_dir: Path


def plan_custom(
    choices: CustomChoices, *, base: Path | None = None,
    now: datetime | None = None, yt_dlp: str = "yt-dlp",
) -> CustomPlan:
    outdir = (Path(choices.output_dir) if choices.output_dir is not None
              else session_dir("perso", base=base, now=now))
    command = build_custom_command(
        choices.url, outdir,
        media=choices.media, max_height=choices.max_height,
        prefer_compatible=choices.prefer_compatible,
        playlist=choices.playlist, playlist_items=choices.playlist_items,
        section=choices.section,
        sponsorblock_categories=choices.sponsorblock_categories,
        sub_langs=choices.sub_langs, embed_subs=choices.embed_subs,
        cookies_browser=choices.cookies_browser,
        limit_rate=choices.limit_rate, concurrent=choices.concurrent,
        yt_dlp=yt_dlp,
    )
    return CustomPlan(command=command, output_dir=outdir)


def run_custom(
    plan: CustomPlan, *, popen_factory: Callable | None = None,
    create_dir: bool = True,
) -> Iterator[RunEvent]:
    if create_dir:
        plan.output_dir.mkdir(parents=True, exist_ok=True)
    yield from (run(plan.command) if popen_factory is None
                else run(plan.command, popen_factory=popen_factory))
