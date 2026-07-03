"""Tests du module d'inspection des formats (pur + probe injecté)."""
import json

from ytdlp_interactif.core.probe import (
    approx_size_for_height,
    best_audio_size,
    parse_formats,
    probe_formats,
    video_heights,
)

# Extrait réaliste de la sortie `yt-dlp -J` (champ formats).
_INFO = {
    "formats": [
        {"format_id": "sb0", "ext": "mhtml", "vcodec": "none", "acodec": "none",
         "height": 180},  # storyboard -> ignoré
        {"format_id": "140", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2",
         "height": None, "filesize": 3_500_000, "tbr": 130},
        {"format_id": "135", "ext": "mp4", "vcodec": "avc1", "acodec": "none",
         "height": 480, "fps": 30, "filesize": 13_000_000},
        {"format_id": "137", "ext": "mp4", "vcodec": "avc1", "acodec": "none",
         "height": 1080, "filesize": 50_000_000},
        {"format_id": "18", "ext": "mp4", "vcodec": "avc1", "acodec": "mp4a.40.2",
         "height": 360, "filesize": 9_000_000},
    ]
}


def test_parse_ignore_storyboards():
    formats = parse_formats(_INFO)
    assert all(f.format_id != "sb0" for f in formats)
    assert len(formats) == 4


def test_video_heights_distinctes_decroissantes():
    formats = parse_formats(_INFO)
    assert video_heights(formats) == [1080, 480, 360]


def test_classification_audio_only():
    formats = parse_formats(_INFO)
    a = next(f for f in formats if f.format_id == "140")
    assert a.is_audio_only is True
    v = next(f for f in formats if f.format_id == "137")
    assert v.is_audio_only is False


def test_taille_approx_video_only_ajoute_audio():
    formats = parse_formats(_INFO)
    # 1080 (video seule 50M) + meilleur audio (3.5M)
    assert approx_size_for_height(formats, 1080) == 53_500_000


def test_taille_approx_format_combine_est_autonome():
    formats = parse_formats(_INFO)
    # 360 est un format combiné (audio inclus) -> pas d'ajout audio
    assert approx_size_for_height(formats, 360) == 9_000_000


def test_best_audio_size():
    assert best_audio_size(parse_formats(_INFO)) == 3_500_000


def test_probe_formats_injecte():
    """probe_formats parse la sortie JSON d'un runner injecté (sans réseau)."""
    captured = {}

    def fake_check_output(cmd):
        captured["cmd"] = cmd
        return json.dumps(_INFO)

    formats = probe_formats("URL", check_output=fake_check_output)
    assert video_heights(formats) == [1080, 480, 360]
    assert "-J" in captured["cmd"] and "URL" in captured["cmd"]
