"""Test 6 : détection des dépendances (pur, sans réseau)."""
from ytdlp_interactif.core.environment import check_dependencies, js_runtime_tip


def _which_sans_ffmpeg(name):
    """Simule un système où ffmpeg est absent mais yt-dlp présent."""
    return None if name == "ffmpeg" else f"/usr/bin/{name}"


def test_ffmpeg_absent_est_signale_clairement():
    """Test 6 — ffmpeg absent -> report explicite mentionnant ffmpeg."""
    report = check_dependencies(which=_which_sans_ffmpeg)
    assert report.ffmpeg_ok is False
    assert report.yt_dlp_ok is True
    assert "ffmpeg" in report.missing
    assert report.ok is False
    assert "ffmpeg" in report.message.lower()


def test_tout_present_est_ok():
    report = check_dependencies(which=lambda name: f"/usr/bin/{name}")
    assert report.ok is True
    assert report.missing == []


def test_astuce_deno_si_absent():
    tip = js_runtime_tip(which=lambda name: None)
    assert tip is not None
    assert "deno" in tip.lower()
    assert "deno.land/install" in tip


def test_pas_dastuce_si_deno_present():
    assert js_runtime_tip(which=lambda name: "/usr/bin/deno") is None
