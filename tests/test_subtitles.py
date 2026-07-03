"""Tests de la commande sous-titres + orchestration (purs)."""
from datetime import datetime
from pathlib import Path

from ytdlp_interactif.core.command_builder import build_subtitles_command
from ytdlp_interactif.core.runner import RunResult
from ytdlp_interactif.intents.subtitles import (
    SubtitleChoices,
    plan_subtitles,
    run_subtitles,
)


def test_video_avec_sous_titres_par_defaut():
    cmd = build_subtitles_command("URL", "/out")
    assert cmd == [
        "yt-dlp",
        "-f", "bestvideo+bestaudio/best",
        "-S", "vcodec:h264,acodec:aac",
        "--merge-output-format", "mp4",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", "fr,en",
        "--convert-subs", "srt",
        "--embed-metadata",
        "--no-playlist",
        "-o", "/out/%(title)s.%(ext)s",
        "URL",
    ]


def test_sous_titres_seuls_skip_download():
    cmd = build_subtitles_command("URL", "/out", mode="subs_only")
    assert "--skip-download" in cmd
    assert "-f" not in cmd and "--merge-output-format" not in cmd
    assert "--write-subs" in cmd


def test_incrustation_ajoute_embed_subs():
    cmd = build_subtitles_command("URL", "/out", embed=True)
    assert "--embed-subs" in cmd


def test_embed_ignore_en_mode_subs_only():
    cmd = build_subtitles_command("URL", "/out", mode="subs_only", embed=True)
    assert "--embed-subs" not in cmd


def test_langues_et_format_personnalises():
    cmd = build_subtitles_command("URL", "/out", langs="all", sub_format="vtt")
    assert cmd[cmd.index("--sub-langs") + 1] == "all"
    assert cmd[cmd.index("--convert-subs") + 1] == "vtt"


def test_sans_auto_subs():
    cmd = build_subtitles_command("URL", "/out", auto=False)
    assert "--write-auto-subs" not in cmd


def test_plan_dossier_session_prefixe_subs():
    plan = plan_subtitles(
        SubtitleChoices(url="URL"), base=Path("/dl"), now=datetime(2026, 7, 4, 2, 0)
    )
    assert plan.output_dir == Path("/dl/yt-dlp-interactif/subs_2026-07-04_02h00")


def test_run_cree_dossier_et_streame(tmp_path):
    plan = plan_subtitles(
        SubtitleChoices(url="URL", mode="subs_only"),
        base=tmp_path, now=datetime(2026, 7, 4, 2, 0),
    )

    class FakeProc:
        def __init__(self):
            self.stdout = iter(["[info] Writing video subtitles"])

        def wait(self):
            return 0

    events = list(run_subtitles(plan, popen_factory=lambda cmd: FakeProc()))
    assert plan.output_dir.exists()
    assert isinstance(events[-1], RunResult) and events[-1].ok
