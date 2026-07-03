"""Test de l'explication pédagogique de la commande (Q3, pur)."""
from ytdlp_interactif.core.command_builder import build_extract_audio_command
from ytdlp_interactif.ui.explain import explain_command


def test_chaque_option_est_expliquee_et_url_identifiee():
    cmd = build_extract_audio_command("https://x/v", output_dir="/out")
    lines = explain_command(cmd)
    joined = "\n".join(lines)
    assert "-x" in joined and "audio" in joined.lower()
    assert "-f bestaudio/best" in joined
    assert "--audio-quality 192K" in joined
    # L'URL est identifiée comme telle.
    assert any("l'URL à télécharger" in l and "https://x/v" in l for l in lines)
