"""Tests de l'orchestration « Extraire l'audio » (plan pur + exécution factice)."""
from datetime import datetime
from pathlib import Path

from ytdlp_interactif.core.runner import RunResult
from ytdlp_interactif.intents.extract_audio import (
    AudioChoices,
    plan_extract_audio,
    run_extract_audio,
)


def test_plan_utilise_dossier_de_session_par_defaut():
    plan = plan_extract_audio(
        AudioChoices(url="URL"),
        base=Path("/dl"),
        now=datetime(2026, 7, 3, 15, 42),
    )
    assert plan.output_dir == Path("/dl/yt-dlp-interactif/audio_2026-07-03_15h42")
    assert plan.command[-1] == "URL"
    assert "-x" in plan.command
    o = plan.command.index("-o")
    assert plan.command[o + 1].startswith(str(plan.output_dir))


def test_plan_respecte_un_dossier_personnalise():
    plan = plan_extract_audio(AudioChoices(url="U", output_dir=Path("/mon/dossier")))
    assert plan.output_dir == Path("/mon/dossier")


def test_run_cree_le_dossier_paresseusement_et_streame(tmp_path):
    """L'exécution crée le dossier de session (pas avant) et streame les events."""
    plan = plan_extract_audio(
        AudioChoices(url="URL"),
        base=tmp_path,
        now=datetime(2026, 7, 3, 15, 42),
    )
    assert not plan.output_dir.exists()  # pas encore créé

    class FakeProc:
        def __init__(self):
            self.stdout = iter(["[download] 100% of 1MiB", "[ExtractAudio] Destination: a.mp3"])

        def wait(self):
            return 0

    events = list(run_extract_audio(plan, popen_factory=lambda cmd: FakeProc()))

    assert plan.output_dir.exists()  # créé au lancement
    assert isinstance(events[-1], RunResult) and events[-1].ok
