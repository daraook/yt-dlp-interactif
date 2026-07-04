"""Tests de la traduction des erreurs yt-dlp (pur)."""
from ytdlp_interactif.core.errors import humanize_error


def test_video_indisponible():
    m = humanize_error(["ERROR: [youtube] abc: Video unavailable"])
    assert m and "pas disponible" in m


def test_video_privee_suggere_debloquer():
    m = humanize_error(["ERROR: This video is private"])
    assert m and "Débloquer" in m


def test_restriction_age():
    m = humanize_error(["ERROR: Sign in to confirm your age"])
    assert m and ("âge" in m or "Débloquer" in m)


def test_geo_blocage():
    m = humanize_error(["ERROR: The uploader has not made this video available in your country"])
    assert m and "région" in m


def test_reseau():
    m = humanize_error(["ERROR: Unable to download webpage: <urlopen error "
                        "[Errno -3] Temporary failure in name resolution>"])
    assert m and "réseau" in m.lower()


def test_ffmpeg_absent():
    m = humanize_error(["ERROR: ffprobe and ffmpeg not found. Please install"])
    assert m and "ffmpeg" in m.lower()


def test_erreur_inconnue_renvoie_none():
    assert humanize_error(["ERROR: quelque chose de complètement inattendu 4271"]) is None


def test_liste_vide():
    assert humanize_error([]) is None
