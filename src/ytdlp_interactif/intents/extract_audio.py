"""Orchestration de l'intention « Extraire l'audio ».

Deux niveaux :
- `plan_extract_audio` : PUR — choix -> (commande, dossier de sortie). Testable offline.
- `run_extract_audio`  : impur — crée le dossier paresseusement puis streame le runner.

Les défauts intelligents (spec §4) vivent dans `AudioChoices`.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterator

from ..core.command_builder import build_extract_audio_command
from ..core.paths import session_dir
from ..core.runner import RunEvent, run


@dataclass
class AudioChoices:
    url: str
    audio_format: str = "mp3"
    audio_quality: str = "192K"
    embed_thumbnail: bool = True
    embed_metadata: bool = True
    playlist: bool = False
    output_dir: Path | None = None  # None -> dossier de session automatique


@dataclass(frozen=True)
class AudioPlan:
    command: list[str]
    output_dir: Path


def plan_extract_audio(
    choices: AudioChoices,
    *,
    base: Path | None = None,
    now: datetime | None = None,
    yt_dlp: str = "yt-dlp",
) -> AudioPlan:
    """Construit le plan d'exécution (commande + dossier) sans effet de bord."""
    outdir = (
        Path(choices.output_dir)
        if choices.output_dir is not None
        else session_dir("audio", base=base, now=now)
    )
    command = build_extract_audio_command(
        choices.url,
        output_dir=outdir,
        audio_format=choices.audio_format,
        audio_quality=choices.audio_quality,
        embed_thumbnail=choices.embed_thumbnail,
        embed_metadata=choices.embed_metadata,
        playlist=choices.playlist,
        yt_dlp=yt_dlp,
    )
    return AudioPlan(command=command, output_dir=outdir)


def run_extract_audio(
    plan: AudioPlan,
    *,
    popen_factory: Callable | None = None,
    create_dir: bool = True,
) -> Iterator[RunEvent]:
    """Crée le dossier de session (au dernier moment) puis exécute yt-dlp."""
    if create_dir:
        plan.output_dir.mkdir(parents=True, exist_ok=True)
    if popen_factory is None:
        yield from run(plan.command)
    else:
        yield from run(plan.command, popen_factory=popen_factory)
