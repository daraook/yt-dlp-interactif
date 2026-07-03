"""Tests de la commande playlist + orchestration (purs)."""
from datetime import datetime
from pathlib import Path

from ytdlp_interactif.core.command_builder import build_playlist_command
from ytdlp_interactif.core.runner import RunResult
from ytdlp_interactif.intents.download_playlist import (
    PlaylistChoices,
    plan_download_playlist,
    run_download_playlist,
)


def test_video_defaut_range_archive_et_rangement():
    cmd = build_playlist_command("URL", "/base")
    assert "--yes-playlist" in cmd
    assert "-S" in cmd and "--merge-output-format" in cmd
    # archive persistante
    i = cmd.index("--download-archive")
    assert cmd[i + 1] == "/base/archive.txt"
    # rangement numéroté par playlist
    o = cmd.index("-o")
    assert cmd[o + 1] == "/base/%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s"
    assert cmd[-1] == "URL"


def test_audio_playlist_utilise_extraction():
    cmd = build_playlist_command("URL", "/base", media="audio")
    assert "-x" in cmd and "--audio-format" in cmd
    assert "--merge-output-format" not in cmd


def test_plage_ditems():
    cmd = build_playlist_command("URL", "/base", items="1-5")
    i = cmd.index("--playlist-items")
    assert cmd[i + 1] == "1-5"


def test_sans_archive():
    cmd = build_playlist_command("URL", "/base", archive=False)
    assert "--download-archive" not in cmd


def test_plan_utilise_dossier_stable_playlists():
    plan = plan_download_playlist(PlaylistChoices(url="URL"), base=Path("/dl"))
    # dossier STABLE (pas horodaté) pour que l'archive persiste
    assert plan.output_dir == Path("/dl/yt-dlp-interactif/playlists")
    assert "yt-dlp-interactif/playlists" in " ".join(plan.command)


def test_run_cree_dossier_et_streame(tmp_path):
    plan = plan_download_playlist(PlaylistChoices(url="URL"), base=tmp_path)
    assert not plan.output_dir.exists()

    class FakeProc:
        def __init__(self):
            self.stdout = iter(["[download] 100% of 5MiB", "[Merger] Merging"])

        def wait(self):
            return 0

    events = list(run_download_playlist(plan, popen_factory=lambda cmd: FakeProc()))
    assert plan.output_dir.exists()
    assert isinstance(events[-1], RunResult) and events[-1].ok
