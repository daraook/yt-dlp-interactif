"""Tests du constructeur « superset » composable (combos arbitraires)."""
from datetime import datetime
from pathlib import Path

from ytdlp_interactif.core.command_builder import build_custom_command
from ytdlp_interactif.core.runner import RunResult
from ytdlp_interactif.intents.custom import CustomChoices, plan_custom, run_custom


def test_combo_playlist_audio():
    """Playlist complète mais en audio seul -> -x + --yes-playlist + rangement playlist."""
    cmd = build_custom_command("URL", "/o", media="audio", playlist=True)
    assert "-x" in cmd and "--yes-playlist" in cmd
    o = cmd.index("-o")
    assert "%(playlist_index)02d" in cmd[o + 1]


def test_combo_video_sponsorblock_extrait_soustitres():
    cmd = build_custom_command(
        "URL", "/o", media="video",
        sponsorblock_categories="sponsor,intro",
        section=("0:30", "1:00"),
        sub_langs="fr,en", embed_subs=True,
    )
    assert cmd[cmd.index("--sponsorblock-remove") + 1] == "sponsor,intro"
    assert cmd[cmd.index("--download-sections") + 1] == "*0:30-1:00"
    assert "--force-keyframes-at-cuts" in cmd  # vidéo
    assert cmd[cmd.index("--sub-langs") + 1] == "fr,en"
    assert "--embed-subs" in cmd


def test_combo_cookies_et_reseau():
    cmd = build_custom_command(
        "URL", "/o", cookies_browser="firefox", limit_rate="2M", concurrent=8
    )
    assert cmd[cmd.index("--cookies-from-browser") + 1] == "firefox"
    assert cmd[cmd.index("-r") + 1] == "2M"
    assert cmd[cmd.index("-N") + 1] == "8"


def test_audio_extrait_sans_keyframes():
    cmd = build_custom_command("URL", "/o", media="audio", section=("10", "20"))
    assert "--force-keyframes-at-cuts" not in cmd
    assert cmd[cmd.index("--download-sections") + 1] == "*10-20"


def test_defaut_simple_video():
    cmd = build_custom_command("URL", "/o")
    assert cmd[:1] == ["yt-dlp"]
    assert "--no-playlist" in cmd
    assert cmd[-1] == "URL"


def test_plan_et_run(tmp_path):
    plan = plan_custom(
        CustomChoices(url="URL", media="audio", playlist=True),
        base=tmp_path, now=datetime(2026, 7, 4, 7, 0),
    )
    assert plan.output_dir == tmp_path / "yt-dlp-interactif" / "perso_2026-07-04_07h00"

    class FakeProc:
        def __init__(self):
            self.stdout = iter(["[download] 100% of 1MiB"])

        def wait(self):
            return 0

    events = list(run_custom(plan, popen_factory=lambda cmd: FakeProc()))
    assert plan.output_dir.exists()
    assert isinstance(events[-1], RunResult) and events[-1].ok
