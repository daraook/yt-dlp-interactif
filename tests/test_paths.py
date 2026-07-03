"""Test 7 : dossier Téléchargements cross-platform + dossier de session (pur)."""
from datetime import datetime
from pathlib import Path

from ytdlp_interactif.core.paths import (
    downloads_dir,
    parse_xdg_download,
    session_dir,
)


def test_parse_xdg_localise():
    """XDG en français -> Téléchargements ; $HOME est résolu."""
    home = Path("/home/x")
    content = 'XDG_DOWNLOAD_DIR="$HOME/Téléchargements"\n'
    assert parse_xdg_download(content, home) == home / "Téléchargements"


def test_parse_xdg_anglais():
    home = Path("/home/x")
    content = '# commentaire\nXDG_DOWNLOAD_DIR="$HOME/Downloads"\n'
    assert parse_xdg_download(content, home) == home / "Downloads"


def test_parse_xdg_absent_renvoie_none():
    assert parse_xdg_download("XDG_MUSIC_DIR=\"$HOME/Musique\"\n", Path("/home/x")) is None


def test_downloads_dir_linux_utilise_xdg():
    home = Path("/home/x")
    d = downloads_dir(system="linux", home=home,
                      xdg_content='XDG_DOWNLOAD_DIR="$HOME/Téléchargements"\n')
    assert d == home / "Téléchargements"


def test_downloads_dir_macos():
    home = Path("/Users/x")
    assert downloads_dir(system="darwin", home=home) == home / "Downloads"


def test_session_dir_nomenclature_et_paresseux():
    """Test 7 — nom = audio_AAAA-MM-JJ_HHhMM, sous yt-dlp-interactif/, non créé."""
    sd = session_dir("audio", base=Path("/dl"), now=datetime(2026, 7, 3, 15, 42))
    assert sd == Path("/dl/yt-dlp-interactif/audio_2026-07-03_15h42")
    assert sd.exists() is False  # création paresseuse
