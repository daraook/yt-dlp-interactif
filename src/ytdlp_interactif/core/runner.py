"""Exécution de yt-dlp en subprocess, transformée en flux d'événements.

Le runner ne connaît pas l'interface : il **yield** des événements
(ProgressEvent / LogLine / RunResult) que l'UI choisit d'afficher ou non.
`popen_factory` est injectable pour tester sans lancer de vrai processus.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import Callable, Iterator, Protocol

from .progress import ProgressEvent, parse_progress_line


class _Process(Protocol):
    stdout: Iterator[str]
    def wait(self) -> int: ...


@dataclass(frozen=True)
class LogLine:
    """Ligne brute non-progress (utile pour le mode « voir les détails »)."""
    text: str


@dataclass(frozen=True)
class RunResult:
    """Événement terminal : code de sortie + lignes d'erreur collectées."""
    returncode: int
    ok: bool
    errors: list[str] = field(default_factory=list)


RunEvent = ProgressEvent | LogLine | RunResult


def _default_popen(command: list[str]) -> _Process:
    """Lance yt-dlp en fusionnant stderr dans stdout (évite le deadlock de pipe)."""
    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


def run(
    command: list[str],
    *,
    popen_factory: Callable[[list[str]], _Process] = _default_popen,
) -> Iterator[RunEvent]:
    """Exécute la commande et émet le flux d'événements jusqu'au RunResult final."""
    # --newline force yt-dlp à écrire une ligne par mise à jour (parsing fiable).
    exec_command = [command[0], "--newline", *command[1:]]
    proc = popen_factory(exec_command)
    errors: list[str] = []

    for raw in proc.stdout:
        line = raw.rstrip("\r\n")
        if not line:
            continue
        if line.startswith("ERROR:"):
            errors.append(line)

        event = parse_progress_line(line)
        yield event if event is not None else LogLine(text=line)

    returncode = proc.wait()
    yield RunResult(returncode=returncode, ok=(returncode == 0), errors=errors)
