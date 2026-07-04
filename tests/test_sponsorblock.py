"""Tests de la commande SponsorBlock + orchestration (purs)."""
from datetime import datetime
from pathlib import Path

from ytdlp_interactif.core.command_builder import build_sponsorblock_command
from ytdlp_interactif.core.runner import RunResult
from ytdlp_interactif.intents.sponsorblock import (
    SponsorBlockChoices,
    plan_sponsorblock,
    run_sponsorblock,
)


def test_defaut_retire_les_sponsors():
    cmd = build_sponsorblock_command("URL", "/out")
    assert "-f" in cmd and "--merge-output-format" in cmd
    i = cmd.index("--sponsorblock-remove")
    assert cmd[i + 1] == "sponsor"
    assert "--sponsorblock-mark" not in cmd
    assert cmd[-1] == "URL"


def test_mode_marquer_en_chapitres():
    cmd = build_sponsorblock_command("URL", "/out", action="mark")
    assert "--sponsorblock-mark" in cmd
    assert "--sponsorblock-remove" not in cmd


def test_categories_multiples():
    cmd = build_sponsorblock_command(
        "URL", "/out", categories="sponsor,intro,outro,selfpromo"
    )
    i = cmd.index("--sponsorblock-remove")
    assert cmd[i + 1] == "sponsor,intro,outro,selfpromo"


def test_plan_dossier_session_prefixe():
    plan = plan_sponsorblock(
        SponsorBlockChoices(url="URL"), base=Path("/dl"), now=datetime(2026, 7, 4, 4, 0)
    )
    assert plan.output_dir == Path("/dl/yt-dlp-interactif/sponsorblock_2026-07-04_04h00")


def test_run_cree_dossier_et_streame(tmp_path):
    plan = plan_sponsorblock(
        SponsorBlockChoices(url="URL"), base=tmp_path, now=datetime(2026, 7, 4, 4, 0)
    )

    class FakeProc:
        def __init__(self):
            self.stdout = iter(["[download] 100% of 1MiB", "[SponsorBlock] Found 1 segment"])

        def wait(self):
            return 0

    events = list(run_sponsorblock(plan, popen_factory=lambda cmd: FakeProc()))
    assert plan.output_dir.exists()
    assert isinstance(events[-1], RunResult) and events[-1].ok
