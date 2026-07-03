"""Tests des helpers purs de l'UI questionary."""
from ytdlp_interactif.ui.questionary_ui import _hide_hidden


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
