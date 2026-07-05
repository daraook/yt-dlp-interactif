"""Tests 1-3 : construction de la commande yt-dlp (pur, sans réseau)."""
from ytdlp_interactif.core.command_builder import build_extract_audio_command


def test_defauts_donnent_la_commande_de_reference():
    """Test 1 — choix par défaut = commande de référence exacte (spec §3)."""
    cmd = build_extract_audio_command("URL", output_dir="/out")
    assert cmd == [
        "yt-dlp",
        "-x",
        "-f", "bestaudio/18/best",
        "--audio-format", "mp3",
        "--audio-quality", "192K",
        "--embed-thumbnail",
        "--embed-metadata",
        "--no-playlist",
        "--replace-in-metadata", "title", r"\.(mp4|mkv|mov|avi|webm|flv|m4v|ts|3gp)$", "",
        "-o", "/out/%(title)s.%(ext)s",
        "URL",
    ]


def test_selecteur_format_desactivable():
    """format_selector=None -> pas de -f (yt-dlp choisit seul)."""
    cmd = build_extract_audio_command("URL", output_dir="/out", format_selector=None)
    assert "-f" not in cmd


def test_format_sans_pochette_omet_embed_thumbnail():
    """Test 2 — flac/wav ne portent pas de pochette : pas de --embed-thumbnail."""
    cmd = build_extract_audio_command("URL", output_dir="/out", audio_format="flac")
    assert "--embed-thumbnail" not in cmd
    assert "--audio-format" in cmd and cmd[cmd.index("--audio-format") + 1] == "flac"


def test_dossier_personnalise_reflete_dans_output():
    """Test 3 — le dossier choisi apparaît dans le template -o."""
    cmd = build_extract_audio_command("URL", output_dir="/home/x/Musique")
    i = cmd.index("-o")
    assert cmd[i + 1] == "/home/x/Musique/%(title)s.%(ext)s"


def test_playlist_utilise_yes_playlist():
    """Bonus — playlist=True force --yes-playlist au lieu de --no-playlist."""
    cmd = build_extract_audio_command("URL", output_dir="/out", playlist=True)
    assert "--yes-playlist" in cmd
    assert "--no-playlist" not in cmd


def test_selecteur_audio_replie_sur_muxe_leger():
    """Pas d'audio-only ? Repli sur itag 18 (léger) avant best, pas un HLS lourd."""
    cmd = build_extract_audio_command("URL", output_dir="/out")
    assert cmd[cmd.index("-f") + 1] == "bestaudio/18/best"


def test_nettoyage_extension_residuelle_du_titre():
    """Une extension vidéo en fin de titre est retirée avant nommage (anti double .ext)."""
    cmd = build_extract_audio_command("URL", output_dir="/out")
    i = cmd.index("--replace-in-metadata")
    assert cmd[i + 1] == "title"
    assert cmd[i + 2].endswith("$") and "mp4" in cmd[i + 2]
    assert cmd[i + 3] == ""
    # Le nettoyage précède le template de sortie.
    assert i < cmd.index("-o")
