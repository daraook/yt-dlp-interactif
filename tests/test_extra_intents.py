"""Tests des intentions restantes : convert, extras, live, unlock, network, probe_info."""
from datetime import datetime
from pathlib import Path

from ytdlp_interactif.core.command_builder import (
    build_convert_command,
    build_extras_command,
    build_live_command,
    build_network_command,
    build_unlock_command,
)
from ytdlp_interactif.core.probe import parse_info, probe_info
from ytdlp_interactif.intents.convert import ConvertChoices, plan_convert
from ytdlp_interactif.intents.extras import ExtrasChoices, plan_extras
from ytdlp_interactif.intents.live import LiveChoices, plan_live
from ytdlp_interactif.intents.network import NetworkChoices, plan_network
from ytdlp_interactif.intents.unlock import UnlockChoices, plan_unlock


# --- Convert ---
def test_convert_remux_par_defaut():
    cmd = build_convert_command("URL", "/o")
    assert "--remux-video" in cmd and cmd[cmd.index("--remux-video") + 1] == "mp4"
    assert "--recode-video" not in cmd


def test_convert_recode():
    cmd = build_convert_command("URL", "/o", target_ext="mkv", recode=True)
    assert cmd[cmd.index("--recode-video") + 1] == "mkv"


# --- Extras (miniature & métadonnées) ---
def test_extras_video_defaut_incruste():
    cmd = build_extras_command("URL", "/o")
    assert "--embed-thumbnail" in cmd and "--embed-metadata" in cmd
    assert "--skip-download" not in cmd


def test_extras_annexes_seules():
    cmd = build_extras_command("URL", "/o", skip_download=True, write_thumbnail=True,
                               write_info_json=True)
    assert "--skip-download" in cmd
    assert "--write-thumbnail" in cmd and "--write-info-json" in cmd
    assert "--embed-thumbnail" not in cmd  # rien à incruster sans fichier


# --- Live ---
def test_live_depuis_le_debut():
    cmd = build_live_command("URL", "/o")
    assert "--live-from-start" in cmd


def test_live_attente():
    cmd = build_live_command("URL", "/o", wait=True, wait_interval="60")
    i = cmd.index("--wait-for-video")
    assert cmd[i + 1] == "60"


# --- Unlock (cookies / géo) ---
def test_unlock_cookies_navigateur():
    cmd = build_unlock_command("URL", "/o", browser="chrome")
    assert cmd[cmd.index("--cookies-from-browser") + 1] == "chrome"
    assert "--geo-bypass" not in cmd


def test_unlock_geo_et_audio():
    cmd = build_unlock_command("URL", "/o", geo_bypass=True, media="audio")
    assert "--geo-bypass" in cmd and "-x" in cmd


# --- Network ---
def test_network_bride_et_parallelisme():
    cmd = build_network_command("URL", "/o", limit_rate="2M", concurrent=8)
    assert cmd[cmd.index("-r") + 1] == "2M"
    assert cmd[cmd.index("-N") + 1] == "8"


def test_network_sans_bride_pas_de_r():
    cmd = build_network_command("URL", "/o", concurrent=1)
    assert "-r" not in cmd and "-N" not in cmd


# --- Plans : dossiers de session ---
def test_plans_dossiers_de_session():
    now = datetime(2026, 7, 4, 6, 0)
    assert plan_convert(ConvertChoices(url="U"), base=Path("/d"), now=now).output_dir \
        == Path("/d/yt-dlp-interactif/converti_2026-07-04_06h00")
    assert plan_extras(ExtrasChoices(url="U"), base=Path("/d"), now=now).output_dir \
        == Path("/d/yt-dlp-interactif/extras_2026-07-04_06h00")
    assert plan_live(LiveChoices(url="U"), base=Path("/d"), now=now).output_dir \
        == Path("/d/yt-dlp-interactif/live_2026-07-04_06h00")
    assert plan_unlock(UnlockChoices(url="U"), base=Path("/d"), now=now).output_dir \
        == Path("/d/yt-dlp-interactif/prive_2026-07-04_06h00")
    assert plan_network(NetworkChoices(url="U"), base=Path("/d"), now=now).output_dir \
        == Path("/d/yt-dlp-interactif/reseau_2026-07-04_06h00")


# --- probe_info ---
_INFO = {
    "title": "Ma vidéo", "uploader": "Chaîne X", "duration": 213, "is_live": False,
    "subtitles": {"en": [{}], "fr": [{}]},
    "automatic_captions": {"es": [{}]},
    "formats": [
        {"format_id": "137", "ext": "mp4", "vcodec": "avc1", "acodec": "none",
         "height": 1080, "filesize": 50_000_000},
    ],
}


def test_parse_info_resume():
    info = parse_info(_INFO)
    assert info.title == "Ma vidéo" and info.duration == 213
    assert info.sub_langs == ["en", "fr"]
    assert info.auto_sub_langs == ["es"]
    assert info.heights == [1080]


def test_probe_info_injecte():
    import json
    info = probe_info("URL", check_output=lambda cmd: json.dumps(_INFO))
    assert info.uploader == "Chaîne X"
