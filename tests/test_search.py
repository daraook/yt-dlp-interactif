"""Tests du parseur de recherche (pur) + search() injecté."""
import json

from ytdlp_interactif.core.search import parse_search_results, search

_INFO = {
    "entries": [
        {"ie_key": "Youtube", "id": "abcdefghijk", "title": "Une vidéo",
         "url": "https://www.youtube.com/watch?v=abcdefghijk",
         "uploader": "Chaîne A", "duration": 213},
        {"ie_key": "YoutubePlaylist", "id": "PLp8fd", "title": "SOUWENONSOUVO",
         "url": "https://www.youtube.com/playlist?list=PLp8fd",
         "playlist_count": 56},
        {"ie_key": "YoutubeTab", "id": "UCabc", "title": "Radio Cotonou",
         "url": "https://www.youtube.com/channel/UCabc", "uploader": "Radio Cotonou"},
        {"title": "", "url": ""},  # entrée vide -> ignorée
    ]
}


def test_classification_video_playlist_chaine():
    r = parse_search_results(_INFO)
    kinds = [x.kind for x in r]
    assert kinds == ["video", "playlist", "channel"]  # l'entrée vide est ignorée


def test_playlist_affiche_le_nombre():
    r = parse_search_results(_INFO)
    pl = next(x for x in r if x.kind == "playlist")
    assert "56 vidéos" in pl.subtitle
    assert pl.url == "https://www.youtube.com/playlist?list=PLp8fd"


def test_video_montre_chaine_et_duree():
    r = parse_search_results(_INFO)
    v = next(x for x in r if x.kind == "video")
    assert "Chaîne A" in v.subtitle and "3:33" in v.subtitle


def test_search_injecte_construit_la_bonne_commande():
    captured = {}

    def fake(cmd):
        captured["cmd"] = cmd
        return json.dumps(_INFO)

    res = search("souwenonsouvo", limit=10, check_output=fake)
    assert len(res) == 3
    assert "--flat-playlist" in captured["cmd"]
    assert "souwenonsouvo" in captured["cmd"][-1]  # requête encodée dans l'URL
    assert captured["cmd"][captured["cmd"].index("--playlist-end") + 1] == "10"
