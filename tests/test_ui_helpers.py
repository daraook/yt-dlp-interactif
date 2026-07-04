"""Tests des helpers purs de l'UI questionary."""
from ytdlp_interactif.ui.questionary_ui import _fmt_duration, _fmt_size, _hide_hidden


def test_masque_les_dossiers_caches():
    assert _hide_hidden("/home/x/.config") is False
    assert _hide_hidden("/home/x/.ssh") is False
    assert _hide_hidden(".venv") is False


def test_affiche_les_dossiers_normaux():
    assert _hide_hidden("/home/x/Documents") is True
    assert _hide_hidden("Musique") is True


def test_navigation_point_et_double_point_visibles():
    assert _hide_hidden(".") is True
    assert _hide_hidden("..") is True


def test_fmt_duration():
    assert _fmt_duration(None) == "?"
    assert _fmt_duration(0) == "?"
    assert _fmt_duration(45) == "0:45"
    assert _fmt_duration(213) == "3:33"
    assert _fmt_duration(3661) == "1:01:01"


def test_fmt_size():
    assert _fmt_size(None) == ""
    assert _fmt_size(0) == ""
    assert "50 Mo" in _fmt_size(50_000_000)
    assert "~1 Mo" in _fmt_size(1_000_000)
