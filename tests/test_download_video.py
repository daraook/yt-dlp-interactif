"""Tests de la commande « Télécharger une vidéo » + orchestration (purs)."""
from datetime import datetime
from pathlib import Path

from ytdlp_interactif.core.command_builder import build_download_video_command
from ytdlp_interactif.core.runner import RunResult
from ytdlp_interactif.intents.download_video import (
    VideoChoices,
    plan_download_video,
    run_download_video,
)


def test_defauts_compatible_mp4():
    cmd = build_download_video_command("URL", output_dir="/out")
    assert cmd == [
        "yt-dlp",
        "-f", "bestvideo+bestaudio/best",
        "--merge-output-format", "mp4",
        "-S", "vcodec:h264,acodec:aac",
        "--embed-metadata",
        "--no-playlist",
        "-o", "/out/%(title)s.%(ext)s",
        "URL",
    ]


def test_qualite_max_retire_le_tri_compatible():
    cmd = build_download_video_command("URL", output_dir="/out", prefer_compatible=False)
    assert "-S" not in cmd


def test_limite_de_hauteur_dans_le_selecteur():
    cmd = build_download_video_command("URL", output_dir="/out", max_height=720)
    f = cmd[cmd.index("-f") + 1]
    assert "[height<=720]" in f
    assert f.endswith("/best")


def test_pochette_optionnelle():
    sans = build_download_video_command("URL", output_dir="/o")
    avec = build_download_video_command("URL", output_dir="/o", embed_thumbnail=True)
    assert "--embed-thumbnail" not in sans
    assert "--embed-thumbnail" in avec


def test_playlist_force_yes_playlist():
    cmd = build_download_video_command("URL", output_dir="/o", playlist=True)
    assert "--yes-playlist" in cmd and "--no-playlist" not in cmd


def test_plan_utilise_dossier_session_prefixe_video():
    plan = plan_download_video(
        VideoChoices(url="URL"),
        base=Path("/dl"),
        now=datetime(2026, 7, 4, 1, 5),
    )
    assert plan.output_dir == Path("/dl/yt-dlp-interactif/video_2026-07-04_01h05")
    assert plan.command[-1] == "URL"


def test_run_cree_dossier_et_streame(tmp_path):
    plan = plan_download_video(
        VideoChoices(url="URL"), base=tmp_path, now=datetime(2026, 7, 4, 1, 5)
    )
    assert not plan.output_dir.exists()

    class FakeProc:
        def __init__(self):
            self.stdout = iter(["[download] 100% of 5MiB", "[Merger] Merging formats"])

        def wait(self):
            return 0

    events = list(run_download_video(plan, popen_factory=lambda cmd: FakeProc()))
    assert plan.output_dir.exists()
    assert isinstance(events[-1], RunResult) and events[-1].ok
