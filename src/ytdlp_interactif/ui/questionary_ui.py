"""Interface interactive « prompts » (piste B, questionary).

Ne contient AUCUNE logique yt-dlp : elle orchestre les questions, appelle le
noyau (environment / intents / runner) et affiche les événements.
"""
from __future__ import annotations

import questionary

from ..core.environment import check_dependencies
from ..core.progress import ProgressEvent
from ..core.runner import LogLine, RunResult
from ..intents.extract_audio import (
    AudioChoices,
    plan_extract_audio,
    run_extract_audio,
)
from .explain import explain_command

_QUALITES = {
    "128 kbps (léger)": "128K",
    "192 kbps (recommandé)": "192K",
    "256 kbps (haute)": "256K",
    "320 kbps (maximale)": "320K",
    "Meilleure disponible": "0",
}


def _cancelled(value) -> bool:
    """questionary renvoie None si l'utilisateur fait Ctrl+C / Échap."""
    return value is None


def run_app() -> None:
    """Point d'entrée de l'interface questionary."""
    print("\n🎬  yt-dlp interactif — rendre yt-dlp accessible\n")

    report = check_dependencies()
    if not report.ok:
        print("⛔ " + report.message)
        return

    action = questionary.select(
        "Que veux-tu faire ?",
        choices=[
            "🎵  Extraire l'audio (MP3, …)",
            questionary.Choice("📥  Autres intentions", disabled="bientôt disponible"),
            "🚪  Quitter",
        ],
    ).ask()

    if _cancelled(action) or action.startswith("🚪"):
        print("À bientôt 👋")
        return

    _flow_extract_audio()


def _flow_extract_audio() -> None:
    url = questionary.text(
        "URL de la vidéo :",
        validate=lambda v: True if v.strip() else "Entre une URL.",
    ).ask()
    if _cancelled(url):
        return
    url = url.strip()

    mode = questionary.select(
        "Réglages :",
        choices=[
            "⚡ Rapide (MP3 192 kbps, pochette + tags, dossier auto)",
            "🎛️  Personnaliser",
        ],
    ).ask()
    if _cancelled(mode):
        return

    choices = AudioChoices(url=url)
    if mode.startswith("🎛️"):
        choices = _customize(url)
        if choices is None:
            return

    plan = plan_extract_audio(choices)

    print("\n── Récapitulatif ──")
    print(f"  Format  : {choices.audio_format}  ·  Qualité : {choices.audio_quality}")
    print(f"  Pochette: {'oui' if choices.embed_thumbnail else 'non'}  ·  "
          f"Tags : {'oui' if choices.embed_metadata else 'non'}")
    print(f"  Dossier : {plan.output_dir}")

    if questionary.confirm(
        "Voir la commande yt-dlp exécutée (et son explication) ?", default=False
    ).ask():
        print("\n  $ " + " ".join(plan.command) + "\n")
        for line in explain_command(plan.command):
            print(line)
        print()

    if not questionary.confirm("Lancer maintenant ?", default=True).ask():
        print("Annulé.")
        return

    _execute(plan)


def _customize(url: str) -> AudioChoices | None:
    fmt = questionary.select(
        "Format audio :",
        choices=["mp3", "m4a", "opus", "flac", "wav"],
        default="mp3",
    ).ask()
    if _cancelled(fmt):
        return None

    q_label = questionary.select(
        "Qualité :", choices=list(_QUALITES), default="192 kbps (recommandé)"
    ).ask()
    if _cancelled(q_label):
        return None

    thumb = questionary.confirm("Incruster la pochette ?", default=True).ask()
    if _cancelled(thumb):
        return None
    meta = questionary.confirm("Écrire les tags (métadonnées) ?", default=True).ask()
    if _cancelled(meta):
        return None

    output_dir = None
    if questionary.confirm(
        "Choisir un dossier de sortie ? (sinon dossier auto daté)", default=False
    ).ask():
        chosen = questionary.path("Dossier :").ask()
        if not _cancelled(chosen) and chosen.strip():
            output_dir = chosen.strip()

    return AudioChoices(
        url=url,
        audio_format=fmt,
        audio_quality=_QUALITES[q_label],
        embed_thumbnail=thumb,
        embed_metadata=meta,
        output_dir=output_dir,
    )


def _execute(plan) -> None:
    print()
    logs: list[str] = []
    postproc_announced = False
    result: RunResult | None = None

    try:
        for ev in run_extract_audio(plan):
            if isinstance(ev, ProgressEvent):
                if ev.phase == "download" and ev.percent is not None:
                    print(f"\r  ⬇️  Téléchargement… {ev.percent:5.1f}%", end="", flush=True)
                elif ev.phase == "postproc" and not postproc_announced:
                    postproc_announced = True
                    print("\r  🎧  Conversion audio…                    ")
            elif isinstance(ev, LogLine):
                logs.append(ev.text)
            elif isinstance(ev, RunResult):
                result = ev
    except KeyboardInterrupt:
        print("\n⏹️  Interrompu.")
        return

    print()
    if result is not None and result.ok:
        files = sorted(p.name for p in plan.output_dir.glob("*")) if plan.output_dir.exists() else []
        print("✅  Terminé !")
        print(f"   📁 {plan.output_dir}")
        for f in files:
            print(f"   • {f}")
    else:
        print("❌  Échec du téléchargement.")
        errors = result.errors if result else []
        for e in errors[:3]:
            print("   " + e)
        if questionary.confirm("Voir les détails techniques ?", default=False).ask():
            for line in logs[-25:]:
                print("   " + line)
