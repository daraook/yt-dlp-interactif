"""Tests de la commande « extrait / découpe » + orchestration (purs)."""
from datetime import datetime
from pathlib import Path

from ytdlp_interactif.core.command_builder import build_section_command
from ytdlp_interactif.core.runner import RunResult
from ytdlp_interactif.intents.sections import (
    SectionChoices,
    plan_section,
    run_section,
)


def test_video_extrait_par_defaut():
    cmd = build_section_command("URL", "/out", start="0:30", end="1:00")
    i = cmd.index("--download-sections")
    assert cmd[i + 1] == "*0:30-1:00"
    assert "--force-keyframes-at-cuts" in cmd  # coupe précise en vidéo
    assert "-f" in cmd and "--merge-output-format" in cmd
    assert cmd[-1] == "URL"


def test_audio_extrait_sans_keyframes():
    cmd = build_section_command("URL", "/out", start="10", end="20", media="audio")
    assert "-x" in cmd and "--audio-format" in cmd
    assert "--force-keyframes-at-cuts" not in cmd
    assert "--merge-output-format" not in cmd
    i = cmd.index("--download-sections")
    assert cmd[i + 1] == "*10-20"


def test_plan_dossier_session_prefixe_extrait():
    plan = plan_section(
        SectionChoices(url="URL", start="0:00", end="0:10"),
        base=Path("/dl"), now=datetime(2026, 7, 4, 5, 0),
    )
    assert plan.output_dir == Path("/dl/yt-dlp-interactif/extrait_2026-07-04_05h00")


def test_run_cree_dossier_et_streame(tmp_path):
    plan = plan_section(
        SectionChoices(url="URL", start="0:00", end="0:10"),
        base=tmp_path, now=datetime(2026, 7, 4, 5, 0),
    )

    class FakeProc:
        def __init__(self):
            self.stdout = iter(["[download] 100% of 1MiB"])

        def wait(self):
            return 0

    events = list(run_section(plan, popen_factory=lambda cmd: FakeProc()))
    assert plan.output_dir.exists()
    assert isinstance(events[-1], RunResult) and events[-1].ok
