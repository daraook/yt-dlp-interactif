"""Tests de la commande « lot » (plusieurs liens / fichier) + orchestration."""
from datetime import datetime
from pathlib import Path

import pytest

from ytdlp_interactif.core.command_builder import build_batch_command
from ytdlp_interactif.core.runner import RunResult
from ytdlp_interactif.intents.batch import (
    BatchChoices,
    plan_batch,
    run_batch,
)


def test_liens_colles_en_positionnel():
    cmd = build_batch_command("/out", urls=["U1", "U2"])
    assert "--batch-file" not in cmd
    assert cmd[-2:] == ["U1", "U2"]
    assert "-f" in cmd and "--merge-output-format" in cmd  # vidéo par défaut


def test_fichier_batch():
    cmd = build_batch_command("/out", batch_file="/tmp/liens.txt")
    i = cmd.index("--batch-file")
    assert cmd[i + 1] == "/tmp/liens.txt"
    # pas d'URL positionnelle
    assert cmd[-2] == "-o"


def test_media_audio():
    cmd = build_batch_command("/out", urls=["U1"], media="audio")
    assert "-x" in cmd and "--audio-format" in cmd
    assert "--merge-output-format" not in cmd


def test_exige_urls_ou_fichier():
    with pytest.raises(ValueError):
        build_batch_command("/out")


def test_plan_dossier_session_prefixe_lot():
    plan = plan_batch(
        BatchChoices(urls=["U1"]), base=Path("/dl"), now=datetime(2026, 7, 4, 3, 0)
    )
    assert plan.output_dir == Path("/dl/yt-dlp-interactif/lot_2026-07-04_03h00")


def test_run_cree_dossier_et_streame(tmp_path):
    plan = plan_batch(
        BatchChoices(urls=["U1"]), base=tmp_path, now=datetime(2026, 7, 4, 3, 0)
    )

    class FakeProc:
        def __init__(self):
            self.stdout = iter(["[download] 100% of 1MiB"])

        def wait(self):
            return 0

    events = list(run_batch(plan, popen_factory=lambda cmd: FakeProc()))
    assert plan.output_dir.exists()
    assert isinstance(events[-1], RunResult) and events[-1].ok
