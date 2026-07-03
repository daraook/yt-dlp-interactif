"""Tests 4-5 : parsing de la progression yt-dlp (pur, sans réseau)."""
from ytdlp_interactif.core.progress import parse_progress_line


def test_ligne_download_donne_phase_et_pourcentage():
    """Test 4 — '[download]  42.3% of ...' -> download, 42.3."""
    ev = parse_progress_line("[download]  42.3% of 10.00MiB at 1.00MiB/s ETA 00:10")
    assert ev is not None
    assert ev.phase == "download"
    assert ev.percent == 42.3


def test_ligne_extract_audio_donne_phase_postproc():
    """Test 5 — '[ExtractAudio] Destination: ...' -> postproc."""
    ev = parse_progress_line("[ExtractAudio] Destination: chanson.mp3")
    assert ev is not None
    assert ev.phase == "postproc"


def test_download_100_pourcent():
    ev = parse_progress_line("[download] 100% of 10.00MiB in 00:03")
    assert ev is not None and ev.phase == "download" and ev.percent == 100.0


def test_ligne_non_pertinente_renvoie_none():
    assert parse_progress_line("Bonjour, ceci n'est pas une ligne de progression") is None
