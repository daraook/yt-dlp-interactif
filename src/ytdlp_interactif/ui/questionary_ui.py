"""Interface interactive « prompts » (piste B, questionary).

Ne contient AUCUNE logique yt-dlp : elle orchestre les questions, appelle le
noyau (environment / intents / runner) et affiche les événements.
"""
from __future__ import annotations

import os

import questionary

from ..core.environment import check_dependencies, js_runtime_tip
from ..core.progress import ProgressEvent
from ..core.runner import LogLine, RunResult, run
from ..intents.extract_audio import (
    AudioChoices,
    plan_extract_audio,
    run_extract_audio,
)
from ..intents.download_video import (
    VideoChoices,
    plan_download_video,
    run_download_video,
)
from ..intents.download_playlist import (
    PlaylistChoices,
    plan_download_playlist,
    run_download_playlist,
)
from ..intents.subtitles import (
    SubtitleChoices,
    plan_subtitles,
    run_subtitles,
)
from ..intents.batch import BatchChoices, plan_batch, run_batch
from ..intents.sponsorblock import (
    SponsorBlockChoices,
    plan_sponsorblock,
    run_sponsorblock,
)
from ..intents.sections import SectionChoices, plan_section, run_section
from ..intents.convert import ConvertChoices, plan_convert, run_convert
from ..intents.extras import ExtrasChoices, plan_extras, run_extras
from ..intents.live import LiveChoices, plan_live, run_live
from ..intents.unlock import UnlockChoices, plan_unlock, run_unlock
from ..intents.network import NetworkChoices, plan_network, run_network
from ..intents.custom import CustomChoices, plan_custom, run_custom
from ..core.search import search
from ..core.probe import (
    approx_size_for_height,
    probe_formats,
    probe_info,
    video_heights,
)
from .explain import explain_command

# Débit -> valeur yt-dlp (None = illimité).
_RATES = {
    "Illimité": None,
    "5 Mo/s": "5M",
    "2 Mo/s": "2M",
    "1 Mo/s": "1M",
    "500 Ko/s": "500K",
}
_BROWSERS = ["firefox", "chrome", "chromium", "edge", "brave", "opera", "vivaldi", "safari"]

# Libellé -> code de catégorie SponsorBlock.
_SB_CATEGORIES = {
    "Sponsors (pubs intégrées)": "sponsor",
    "Auto-promotion": "selfpromo",
    "Rappels d'abonnement / interaction": "interaction",
    "Intro": "intro",
    "Outro / cartes de fin": "outro",
    "Aperçu / récap": "preview",
    "Hors-sujet musical (clips)": "music_offtopic",
    "Remplissage (digressions)": "filler",
}

_SUB_LANGS = {
    "Français (fr)": "fr",
    "Anglais (en)": "en",
    "Français + Anglais": "fr,en",
    "Toutes les langues (all)": "all",
    "Autre (saisir les codes)": None,
}

_QUALITES = {
    "128 kbps (léger)": "128K",
    "192 kbps (recommandé)": "192K",
    "256 kbps (haute)": "256K",
    "320 kbps (maximale)": "320K",
    "Meilleure disponible": "0",
}

# Libellé de résolution -> hauteur max (None = meilleure).
_RESOLUTIONS = {
    "Meilleure disponible": None,
    "1080p (Full HD)": 1080,
    "720p (HD)": 720,
    "480p (léger)": 480,
}


def _cancelled(value) -> bool:
    """questionary renvoie None si l'utilisateur fait Ctrl+C / Échap."""
    return value is None


def _hide_hidden(path: str) -> bool:
    """Filtre d'autocomplétion : masque les entrées cachées (nom commençant par '.').

    Renvoie True pour AFFICHER l'entrée. '.' et '..' restent visibles (navigation).
    """
    name = os.path.basename(os.path.normpath(path))
    if name in (".", ".."):
        return True
    return not name.startswith(".")


def run_app() -> None:
    """Point d'entrée de l'interface questionary."""
    print("\n🎬  yt-dlp interactif — rendre yt-dlp accessible\n")

    report = check_dependencies()
    if not report.ok:
        print("⛔ " + report.message)
        return

    tip = js_runtime_tip()
    if tip:
        print(tip + "\n")

    # (libellé, handler, description affichée sous le curseur). Groupé par séparateurs.
    menu = [
        ("🎬  Télécharger une vidéo", _flow_download_video,
         "La vidéo complète (image + son). Format compatible H.264/AAC par défaut : lit partout."),
        ("🎵  Extraire l'audio (MP3, …)", _flow_extract_audio,
         "Récupère seulement le son, converti en MP3 (ou m4a/opus/flac/wav), pochette + tags."),
        ("🎚️  Choisir la qualité (formats réels)", _flow_choose_quality,
         "Analyse la vidéo et propose un menu des résolutions réellement disponibles, avec tailles."),
        ("📃  Télécharger une playlist / chaîne", _flow_download_playlist,
         "Toute une playlist/chaîne, rangée par dossier et numérotée. Reprend sans re-télécharger."),
        ("🗂️  Fichier de liens (lot)", _flow_batch,
         "Plusieurs liens d'un coup : collés un par un, ou depuis un fichier .txt."),
        ("✂️  Découper un extrait", _flow_section,
         "Ne récupère qu'une portion temporelle (ex. 1:30 → 2:45), coupe précise."),
        ("🔄  Convertir / changer de format", _flow_convert,
         "Change le conteneur (mp4/mkv/webm…). Remux = rapide sans perte ; réencoder = change le codec."),
        ("🚫  SponsorBlock", _flow_sponsorblock,
         "Retire (ou marque en chapitres) les segments sponsors, intros, outros, auto-promo…"),
        ("💬  Sous-titres", _flow_subtitles,
         "Récupère les sous-titres (avec ou sans la vidéo), par langue, incrustables, en .srt."),
        ("🖼️  Miniature & métadonnées", _flow_extras,
         "Gère la miniature (enregistrer/incruster) et les métadonnées (tags, fichier .json d'infos)."),
        ("🔓  Débloquer (privé / géo / âge)", _flow_unlock,
         "Utilise les cookies de ton navigateur pour les vidéos privées/membres/âge, + contournement géo."),
        ("📺  Live / première", _flow_live,
         "Enregistre un direct ou une première : depuis le début, et/ou en attendant qu'il commence."),
        ("⚡  Vitesse / réseau", _flow_network,
         "Règle le débit (brider) et le nombre de téléchargements en parallèle."),
        ("🔍  Inspecter (infos sans télécharger)", _flow_inspect,
         "Affiche titre, durée, qualités et sous-titres disponibles. Ne télécharge rien."),
        ("⬆️  Mettre à jour yt-dlp", _flow_update,
         "Vérifie et installe la dernière version de yt-dlp."),
        ("🧩  Personnalisé (tout combiner)", _flow_custom,
         "Empile les options à la carte : audio+playlist, sponsors+extrait+sous-titres, cookies, réseau…"),
        ("🔎  Chercher (vidéos & playlists)", _flow_search,
         "Cherche par mots-clés, liste vidéos ET playlists trouvées, puis télécharge ton choix."),
    ]
    handlers = {label: fn for label, fn, _ in menu}

    def C(i):
        return questionary.Choice(menu[i][0], description=menu[i][2])
    choices = [
        questionary.Separator("── Sur mesure ──"),
        C(15), C(16),
        questionary.Separator("── Télécharger ──"),
        *[C(i) for i in range(0, 5)],
        questionary.Separator("── Transformer ──"),
        *[C(i) for i in range(5, 10)],
        questionary.Separator("── Cas particuliers ──"),
        *[C(i) for i in range(10, 13)],
        questionary.Separator("── Outils ──"),
        *[C(i) for i in range(13, 15)],
        questionary.Separator(" "),
        "🚪  Quitter",
    ]

    action = questionary.select(
        "Que veux-tu faire ?", choices=choices, show_description=True
    ).ask()

    if _cancelled(action) or action.startswith("🚪"):
        print("À bientôt 👋")
        return
    handlers[action]()


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

    _confirm_and_run(plan, run_extract_audio)


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
        chosen = questionary.path(
            "Dossier :",
            only_directories=True,
            file_filter=_hide_hidden,
        ).ask()
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


def _fmt_size(nbytes: int | None) -> str:
    return f"  (~{round(nbytes / 1_000_000)} Mo)" if nbytes else ""


def _flow_choose_quality() -> None:
    url = questionary.text(
        "URL de la vidéo :",
        validate=lambda v: True if v.strip() else "Entre une URL.",
    ).ask()
    if _cancelled(url):
        return
    url = url.strip()

    print("\n🔍  Analyse des formats disponibles…")
    try:
        formats = probe_formats(url)
    except Exception:
        print("❌  Impossible d'analyser cette URL (voir le message ci-dessus).")
        return

    heights = video_heights(formats)
    if not heights:
        print("Aucun format vidéo exploitable trouvé pour cette URL.")
        return

    audio_label = "🎵  Audio seulement (meilleur, MP3)"
    label_to_height: dict[str, int] = {}
    menu: list[str] = []
    for h in heights:
        label = f"{h}p{_fmt_size(approx_size_for_height(formats, h))}"
        label_to_height[label] = h
        menu.append(label)
    menu.append(audio_label)

    sel = questionary.select("Qualité disponible :", choices=menu).ask()
    if _cancelled(sel):
        return

    if sel == audio_label:
        plan = plan_extract_audio(AudioChoices(url=url))
        print(f"\n  Dossier : {plan.output_dir}")
        _confirm_and_run(plan, run_extract_audio)
        return

    height = label_to_height[sel]
    plan = plan_download_video(
        VideoChoices(url=url, max_height=height, prefer_compatible=True)
    )
    print(f"\n  Qualité : {height}p (compatible H.264/AAC)  ·  Dossier : {plan.output_dir}")
    _confirm_and_run(plan, run_download_video)


def _flow_batch() -> None:
    source = questionary.select(
        "Source des liens :",
        choices=[
            "📋  Coller les liens un par un",
            "📄  Charger un fichier .txt (un lien par ligne)",
        ],
    ).ask()
    if _cancelled(source):
        return

    urls: list[str] | None = None
    batch_file: str | None = None

    if source.startswith("📋"):
        urls = []
        while True:
            u = questionary.text(f"Lien #{len(urls) + 1} (vide pour terminer) :").ask()
            if _cancelled(u):
                return
            u = u.strip()
            if not u:
                if urls:
                    break
                print("  Ajoute au moins un lien.")
                continue
            urls.append(u)
    else:
        chosen = questionary.path(
            "Fichier de liens :", file_filter=_hide_hidden
        ).ask()
        if _cancelled(chosen) or not chosen.strip():
            return
        batch_file = chosen.strip()

    media_sel = questionary.select(
        "Type de contenu :", choices=["🎬  Vidéos", "🎵  Audios (MP3)"]
    ).ask()
    if _cancelled(media_sel):
        return
    media = "audio" if media_sel.startswith("🎵") else "video"

    max_height = None
    if media == "video":
        res_label = questionary.select(
            "Qualité (résolution) :", choices=list(_RESOLUTIONS),
            default="Meilleure disponible",
        ).ask()
        if _cancelled(res_label):
            return
        max_height = _RESOLUTIONS[res_label]

    plan = plan_batch(
        BatchChoices(urls=urls, batch_file=batch_file, media=media, max_height=max_height)
    )

    combien = f"{len(urls)} lien(s)" if urls else f"fichier {batch_file}"
    print("\n── Récapitulatif ──")
    print(f"  Source  : {combien}  ·  Contenu : {'audios MP3' if media == 'audio' else 'vidéos'}")
    print(f"  Dossier : {plan.output_dir}")

    _confirm_and_run(plan, run_batch)


def _flow_section() -> None:
    url = questionary.text(
        "URL de la vidéo :",
        validate=lambda v: True if v.strip() else "Entre une URL.",
    ).ask()
    if _cancelled(url):
        return
    url = url.strip()

    def _valid_time(v):
        return True if v.strip() else "Indique un temps (ex. 1:30, 0:01:30 ou 90)."

    start = questionary.text("Début (ex. 1:30) :", validate=_valid_time).ask()
    if _cancelled(start):
        return
    end = questionary.text("Fin (ex. 2:45) :", validate=_valid_time).ask()
    if _cancelled(end):
        return

    media_sel = questionary.select(
        "Extrait en :", choices=["🎬  Vidéo", "🎵  Audio (MP3)"]
    ).ask()
    if _cancelled(media_sel):
        return
    media = "audio" if media_sel.startswith("🎵") else "video"

    max_height = None
    if media == "video":
        res_label = questionary.select(
            "Qualité (résolution) :", choices=list(_RESOLUTIONS),
            default="Meilleure disponible",
        ).ask()
        if _cancelled(res_label):
            return
        max_height = _RESOLUTIONS[res_label]

    choices = SectionChoices(
        url=url, start=start.strip(), end=end.strip(),
        media=media, max_height=max_height,
    )
    plan = plan_section(choices)

    print("\n── Récapitulatif ──")
    print(f"  Extrait : {start.strip()} → {end.strip()}  ·  "
          f"{'audio MP3' if media == 'audio' else 'vidéo'}")
    print(f"  Dossier : {plan.output_dir}")

    _confirm_and_run(plan, run_section)


def _flow_sponsorblock() -> None:
    url = questionary.text(
        "URL de la vidéo :",
        validate=lambda v: True if v.strip() else "Entre une URL.",
    ).ask()
    if _cancelled(url):
        return
    url = url.strip()

    action_sel = questionary.select(
        "Que faire des segments ?",
        choices=[
            questionary.Choice(
                "✂️  Les couper (retirer de la vidéo)",
                description="Les segments sont supprimés du fichier final."),
            questionary.Choice(
                "🔖  Les marquer en chapitres",
                description="La vidéo reste entière, mais les segments deviennent des chapitres repérables."),
        ],
        show_description=True,
    ).ask()
    if _cancelled(action_sel):
        return
    action = "mark" if action_sel.startswith("🔖") else "remove"

    cat_choices = [
        questionary.Choice(label, checked=(code == "sponsor"))
        for label, code in _SB_CATEGORIES.items()
    ]
    selected = questionary.checkbox(
        "Catégories à traiter (espace pour cocher) :", choices=cat_choices
    ).ask()
    if _cancelled(selected):
        return
    codes = [_SB_CATEGORIES[label] for label in selected] if selected else ["sponsor"]
    categories = ",".join(codes)

    res_label = questionary.select(
        "Qualité (résolution) :", choices=list(_RESOLUTIONS),
        default="Meilleure disponible",
    ).ask()
    if _cancelled(res_label):
        return

    choices = SponsorBlockChoices(
        url=url, action=action, categories=categories,
        max_height=_RESOLUTIONS[res_label],
    )
    plan = plan_sponsorblock(choices)

    print("\n── Récapitulatif ──")
    print(f"  Action    : {'couper' if action == 'remove' else 'marquer'}")
    print(f"  Catégories: {categories}")
    print(f"  Dossier   : {plan.output_dir}")

    _confirm_and_run(plan, run_sponsorblock)


def _flow_subtitles() -> None:
    url = questionary.text(
        "URL de la vidéo :",
        validate=lambda v: True if v.strip() else "Entre une URL.",
    ).ask()
    if _cancelled(url):
        return
    url = url.strip()

    mode_sel = questionary.select(
        "Que veux-tu ?",
        choices=[
            questionary.Choice(
                "🎬  La vidéo AVEC ses sous-titres",
                description="Télécharge la vidéo et ses sous-titres (incrustables)."),
            questionary.Choice(
                "💬  Les sous-titres seulement",
                description="Juste les fichiers .srt, sans télécharger la vidéo."),
        ],
        show_description=True,
    ).ask()
    if _cancelled(mode_sel):
        return
    mode = "subs_only" if mode_sel.startswith("💬") else "video"

    lang_label = questionary.select(
        "Langue(s) des sous-titres :", choices=list(_SUB_LANGS),
        default="Français + Anglais",
    ).ask()
    if _cancelled(lang_label):
        return
    langs = _SUB_LANGS[lang_label]
    if langs is None:  # « Autre »
        langs = questionary.text(
            "Codes de langue (ex. fr,en,es) :",
            validate=lambda v: True if v.strip() else "Indique au moins une langue.",
        ).ask()
        if _cancelled(langs):
            return
        langs = langs.strip()

    auto = questionary.confirm(
        "Inclure les sous-titres auto-générés ?", default=True
    ).ask()
    if _cancelled(auto):
        return

    embed = False
    if mode == "video":
        embed = questionary.confirm(
            "Incruster les sous-titres dans la vidéo ?", default=False
        ).ask()
        if _cancelled(embed):
            return

    plan = plan_subtitles(
        SubtitleChoices(url=url, mode=mode, langs=langs, auto=auto, embed=embed)
    )

    print("\n── Récapitulatif ──")
    print(f"  Cible   : {'sous-titres seuls' if mode == 'subs_only' else 'vidéo + sous-titres'}")
    print(f"  Langues : {langs}  ·  Auto-générés : {'oui' if auto else 'non'}"
          + (f"  ·  Incrustés : {'oui' if embed else 'non'}" if mode == 'video' else ""))
    print(f"  Dossier : {plan.output_dir}")

    _confirm_and_run(plan, run_subtitles)


def _flow_download_playlist() -> None:
    url = questionary.text(
        "URL de la playlist / chaîne :",
        validate=lambda v: True if v.strip() else "Entre une URL.",
    ).ask()
    if _cancelled(url):
        return
    url = url.strip()

    media_sel = questionary.select(
        "Type de contenu :",
        choices=["🎬  Vidéos", "🎵  Audios (MP3)"],
    ).ask()
    if _cancelled(media_sel):
        return
    media = "audio" if media_sel.startswith("🎵") else "video"

    scope = questionary.select(
        "Étendue :",
        choices=["Toute la playlist", "Une plage d'éléments (ex. 1-10)"],
    ).ask()
    if _cancelled(scope):
        return
    items = None
    if scope.startswith("Une plage"):
        items = questionary.text(
            "Éléments (ex. 1-10, 1,3,5, 5:) :",
            validate=lambda v: True if v.strip() else "Indique au moins un élément.",
        ).ask()
        if _cancelled(items):
            return
        items = items.strip()

    max_height = None
    if media == "video":
        res_label = questionary.select(
            "Qualité (résolution) :",
            choices=list(_RESOLUTIONS),
            default="Meilleure disponible",
        ).ask()
        if _cancelled(res_label):
            return
        max_height = _RESOLUTIONS[res_label]

    choices = PlaylistChoices(url=url, media=media, max_height=max_height, items=items)
    plan = plan_download_playlist(choices)

    print("\n── Récapitulatif ──")
    print(f"  Contenu : {'audios MP3' if media == 'audio' else 'vidéos'}  ·  "
          f"Étendue : {'plage ' + items if items else 'toute la playlist'}")
    print(f"  Dossier : {plan.output_dir}  (un sous-dossier par playlist)")
    print("  Reprise : activée (archive anti-doublon — relancer reprend sans doublon)")

    _confirm_and_run(plan, run_download_playlist)


def _ask_resolution():
    """(ok, max_height). ok=False si annulé."""
    label = questionary.select(
        "Qualité (résolution) :", choices=list(_RESOLUTIONS),
        default="Meilleure disponible",
    ).ask()
    if _cancelled(label):
        return False, None
    return True, _RESOLUTIONS[label]


def _ask_media():
    """(ok, media) parmi video/audio."""
    sel = questionary.select(
        "Type de contenu :",
        choices=[
            questionary.Choice("🎬  Vidéo", description="Image + son."),
            questionary.Choice("🎵  Audio (MP3)", description="Le son seul, converti en MP3."),
        ],
        show_description=True,
    ).ask()
    if _cancelled(sel):
        return False, None
    return True, ("audio" if sel.startswith("🎵") else "video")


def _fmt_duration(sec) -> str:
    if not sec:
        return "?"
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _ask_url(prompt="URL de la vidéo :") -> str | None:
    url = questionary.text(
        prompt, validate=lambda v: True if v.strip() else "Entre une URL."
    ).ask()
    return None if _cancelled(url) else url.strip()


def _flow_convert() -> None:
    url = _ask_url()
    if url is None:
        return
    fmt = questionary.select(
        "Format cible :", choices=["mp4", "mkv", "webm", "mov", "avi"], default="mp4"
    ).ask()
    if _cancelled(fmt):
        return
    mode = questionary.select(
        "Méthode :",
        choices=[
            questionary.Choice(
                "⚡ Remux (rapide, sans perte)",
                description="Change seulement l'emballage (conteneur). Instantané, qualité identique."),
            questionary.Choice(
                "🔁 Réencoder",
                description="Recompresse la vidéo dans le nouveau codec. Plus lent, peut perdre un peu de qualité."),
        ],
        show_description=True,
    ).ask()
    if _cancelled(mode):
        return
    recode = mode.startswith("🔁")

    plan = plan_convert(ConvertChoices(url=url, target_ext=fmt, recode=recode))
    print("\n── Récapitulatif ──")
    print(f"  Format : {fmt}  ·  {'réencodage' if recode else 'remux (sans perte)'}")
    print(f"  Dossier: {plan.output_dir}")
    _confirm_and_run(plan, run_convert)


def _flow_extras() -> None:
    url = _ask_url()
    if url is None:
        return
    scope = questionary.select(
        "Portée :",
        choices=[
            "🎬  La vidéo + ses annexes (miniature/tags)",
            "🖼️  Les annexes seules (sans télécharger la vidéo)",
        ],
    ).ask()
    if _cancelled(scope):
        return
    skip = scope.startswith("🖼️")

    write_thumb = questionary.confirm("Enregistrer la miniature (fichier image) ?",
                                      default=skip).ask()
    if _cancelled(write_thumb):
        return
    write_json = questionary.confirm("Enregistrer les infos (fichier .json) ?",
                                     default=False).ask()
    if _cancelled(write_json):
        return
    embed_thumb = embed_meta = False
    if not skip:
        embed_thumb = questionary.confirm("Incruster la miniature dans le fichier ?",
                                          default=True).ask()
        if _cancelled(embed_thumb):
            return
        embed_meta = questionary.confirm("Incruster les métadonnées (tags) ?",
                                         default=True).ask()
        if _cancelled(embed_meta):
            return

    plan = plan_extras(ExtrasChoices(
        url=url, skip_download=skip, write_thumbnail=write_thumb,
        write_info_json=write_json, embed_thumbnail=embed_thumb,
        embed_metadata=embed_meta,
    ))
    print("\n── Récapitulatif ──")
    print(f"  {'Annexes seules' if skip else 'Vidéo + annexes'}  ·  Dossier : {plan.output_dir}")
    _confirm_and_run(plan, run_extras)


def _flow_live() -> None:
    url = _ask_url("URL du live / de la première :")
    if url is None:
        return
    from_start = questionary.confirm(
        "Démarrer depuis le début du live ?", default=True
    ).ask()
    if _cancelled(from_start):
        return
    wait = questionary.confirm(
        "Attendre que la vidéo commence si elle est programmée ?", default=False
    ).ask()
    if _cancelled(wait):
        return
    ok, max_height = _ask_resolution()
    if not ok:
        return

    plan = plan_live(LiveChoices(url=url, from_start=from_start, wait=wait,
                                 max_height=max_height))
    print("\n── Récapitulatif ──")
    print(f"  Depuis le début : {'oui' if from_start else 'non'}  ·  "
          f"Attente : {'oui' if wait else 'non'}")
    print("  ⚠️  Un live peut durer longtemps — Ctrl+C pour arrêter proprement.")
    print(f"  Dossier : {plan.output_dir}")
    _confirm_and_run(plan, run_live)


def _flow_unlock() -> None:
    url = _ask_url()
    if url is None:
        return
    print("  ℹ️  On réutilise les cookies de ton navigateur (session ouverte = accès "
          "à tes vidéos privées/membres/âge). Ferme le navigateur si l'accès échoue.")
    browser = questionary.select("Navigateur où tu es connecté :", choices=_BROWSERS,
                                 default="firefox").ask()
    if _cancelled(browser):
        return
    geo = questionary.confirm("Tenter aussi de contourner un blocage géographique ?",
                              default=False).ask()
    if _cancelled(geo):
        return
    ok, media = _ask_media()
    if not ok:
        return
    max_height = None
    if media == "video":
        ok, max_height = _ask_resolution()
        if not ok:
            return

    plan = plan_unlock(UnlockChoices(url=url, browser=browser, geo_bypass=geo,
                                     media=media, max_height=max_height))
    print("\n── Récapitulatif ──")
    print(f"  Cookies : {browser}  ·  Géo-bypass : {'oui' if geo else 'non'}  ·  "
          f"{'audio' if media == 'audio' else 'vidéo'}")
    print(f"  Dossier : {plan.output_dir}")
    _confirm_and_run(plan, run_unlock)


def _flow_network() -> None:
    url = _ask_url()
    if url is None:
        return
    rate_label = questionary.select("Limite de débit :", choices=list(_RATES),
                                    default="Illimité").ask()
    if _cancelled(rate_label):
        return
    conc_label = questionary.select(
        "Téléchargements parallèles (fragments) :",
        choices=["1 (doux)", "4 (recommandé)", "8 (rapide)", "16 (agressif)"],
        default="4 (recommandé)",
    ).ask()
    if _cancelled(conc_label):
        return
    concurrent = int(conc_label.split()[0])
    ok, media = _ask_media()
    if not ok:
        return
    max_height = None
    if media == "video":
        ok, max_height = _ask_resolution()
        if not ok:
            return

    plan = plan_network(NetworkChoices(
        url=url, limit_rate=_RATES[rate_label], concurrent=concurrent,
        media=media, max_height=max_height,
    ))
    print("\n── Récapitulatif ──")
    print(f"  Débit : {rate_label}  ·  Parallèle : {concurrent}  ·  "
          f"{'audio' if media == 'audio' else 'vidéo'}")
    print(f"  Dossier : {plan.output_dir}")
    _confirm_and_run(plan, run_network)


def _flow_inspect() -> None:
    url = _ask_url()
    if url is None:
        return
    print("\n🔍  Analyse en cours…")
    try:
        info = probe_info(url)
    except Exception:
        print("❌  Impossible d'analyser cette URL (voir le message ci-dessus).")
        return

    print("\n── Fiche vidéo ──")
    print(f"  Titre   : {info.title}")
    print(f"  Chaîne  : {info.uploader}")
    print(f"  Durée   : {_fmt_duration(info.duration)}"
          + ("   🔴 EN DIRECT" if info.is_live else ""))
    heights = info.heights
    print(f"  Qualités: {', '.join(str(h) + 'p' for h in heights) if heights else '—'}")
    print(f"  Sous-titres      : {', '.join(info.sub_langs) if info.sub_langs else '—'}")
    print(f"  ST auto-générés  : {', '.join(info.auto_sub_langs) if info.auto_sub_langs else '—'}")
    print("\n(Aucun téléchargement effectué.)")


def _flow_update() -> None:
    if not questionary.confirm(
        "Vérifier et installer les mises à jour de yt-dlp ?", default=True
    ).ask():
        return
    print("\n⏳  Mise à jour…")
    logs: list[str] = []
    result = None
    try:
        for ev in run(["yt-dlp", "-U"]):
            if isinstance(ev, LogLine):
                logs.append(ev.text)
                print("  " + ev.text)
            elif isinstance(ev, RunResult):
                result = ev
    except KeyboardInterrupt:
        print("Interrompu.")
        return
    if result and result.ok:
        print("✅  Terminé.")
    else:
        print("⚠️  Si yt-dlp a été installé via pip, mets-le à jour ainsi :")
        print("     pip install -U yt-dlp   (ou : .venv/bin/pip install -U yt-dlp)")


def _ask_sub_langs():
    """(ok, langs) — sélection de langue de sous-titres avec option personnalisée."""
    label = questionary.select("Langue(s) :", choices=list(_SUB_LANGS),
                               default="Français + Anglais").ask()
    if _cancelled(label):
        return False, None
    langs = _SUB_LANGS[label]
    if langs is None:
        langs = questionary.text("Codes (ex. fr,en,es) :",
                                 validate=lambda v: bool(v.strip()) or "Au moins une langue.").ask()
        if _cancelled(langs):
            return False, None
        langs = langs.strip()
    return True, langs


def _flow_search() -> None:
    query = questionary.text(
        "Rechercher (mots-clés) :",
        validate=lambda v: True if v.strip() else "Tape quelque chose à chercher.",
    ).ask()
    if _cancelled(query):
        return

    print("\n🔎  Recherche en cours…")
    try:
        results = search(query.strip())
    except Exception:
        print("❌  Recherche impossible (voir le message ci-dessus).")
        return
    if not results:
        print("Aucun résultat.")
        return

    icons = {"playlist": "📃", "video": "🎬", "channel": "📺"}
    order = {"playlist": 0, "video": 1, "channel": 2}
    ordered = sorted(results, key=lambda r: order.get(r.kind, 3))
    choices = [
        questionary.Choice(f"{icons[r.kind]}  {r.title[:70]}",
                           description=r.subtitle, value=i)
        for i, r in enumerate(ordered)
    ]
    choices.append(questionary.Choice("↩  Annuler", value=-1))

    sel = questionary.select(
        f"{len(ordered)} résultats (playlists en tête) :",
        choices=choices, show_description=True,
    ).ask()
    if _cancelled(sel) or sel == -1:
        return
    r = ordered[sel]

    if r.kind in ("playlist", "channel"):
        ok, media = _ask_media()
        if not ok:
            return
        max_height = None
        if media == "video":
            ok, max_height = _ask_resolution()
            if not ok:
                return
        plan = plan_download_playlist(
            PlaylistChoices(url=r.url, media=media, max_height=max_height))
        print(f"\n  {r.title}  ·  {'audios MP3' if media == 'audio' else 'vidéos'}")
        print(f"  Dossier : {plan.output_dir}")
        _confirm_and_run(plan, run_download_playlist)
    else:  # vidéo
        ok, media = _ask_media()
        if not ok:
            return
        if media == "audio":
            plan = plan_extract_audio(AudioChoices(url=r.url))
            print(f"\n  {r.title}  ·  Dossier : {plan.output_dir}")
            _confirm_and_run(plan, run_extract_audio)
        else:
            ok, max_height = _ask_resolution()
            if not ok:
                return
            plan = plan_download_video(VideoChoices(url=r.url, max_height=max_height))
            print(f"\n  {r.title}  ·  Dossier : {plan.output_dir}")
            _confirm_and_run(plan, run_download_video)


def _flow_custom() -> None:
    """Empile n'importe quelle combinaison d'options en un seul téléchargement."""
    url = _ask_url()
    if url is None:
        return
    ok, media = _ask_media()
    if not ok:
        return

    max_height = None
    if media == "video":
        ok, max_height = _ask_resolution()
        if not ok:
            return

    resume: list[str] = ["audio MP3" if media == "audio" else "vidéo"]
    kw: dict = {"url": url, "media": media, "max_height": max_height}

    # Playlist entière ?
    if questionary.confirm("Si c'est une playlist/chaîne, tout prendre ?",
                           default=False).ask():
        kw["playlist"] = True
        resume.append("playlist entière")
        if questionary.confirm("Limiter à une plage d'éléments ?", default=False).ask():
            items = questionary.text("Éléments (ex. 1-10) :",
                                     validate=lambda v: bool(v.strip()) or "…").ask()
            if _cancelled(items):
                return
            kw["playlist_items"] = items.strip()
            resume[-1] = f"playlist {items.strip()}"

    # Extrait temporel ?
    if questionary.confirm("Ne prendre qu'un extrait temporel ?", default=False).ask():
        s = questionary.text("Début (ex. 1:30) :", validate=lambda v: bool(v.strip()) or "…").ask()
        if _cancelled(s):
            return
        e = questionary.text("Fin (ex. 2:45) :", validate=lambda v: bool(v.strip()) or "…").ask()
        if _cancelled(e):
            return
        kw["section"] = (s.strip(), e.strip())
        resume.append(f"extrait {s.strip()}-{e.strip()}")

    # SponsorBlock ?
    if questionary.confirm("Retirer les segments SponsorBlock (sponsors, intros…) ?",
                           default=False).ask():
        cats = questionary.checkbox(
            "Catégories :",
            choices=[questionary.Choice(label, checked=(code == "sponsor"))
                     for label, code in _SB_CATEGORIES.items()],
        ).ask()
        if _cancelled(cats):
            return
        codes = [_SB_CATEGORIES[label] for label in cats] if cats else ["sponsor"]
        kw["sponsorblock_categories"] = ",".join(codes)
        resume.append("sans sponsors")

    # Sous-titres ?
    if questionary.confirm("Ajouter des sous-titres ?", default=False).ask():
        ok, langs = _ask_sub_langs()
        if not ok:
            return
        kw["sub_langs"] = langs
        resume.append(f"sous-titres {langs}")
        if media == "video" and questionary.confirm("Les incruster dans la vidéo ?",
                                                    default=False).ask():
            kw["embed_subs"] = True

    # Cookies (contenu privé) ?
    if questionary.confirm("Utiliser les cookies d'un navigateur (privé/membre) ?",
                           default=False).ask():
        browser = questionary.select("Navigateur :", choices=_BROWSERS,
                                     default="firefox").ask()
        if _cancelled(browser):
            return
        kw["cookies_browser"] = browser
        resume.append(f"cookies {browser}")

    # Réseau ?
    if questionary.confirm("Régler le débit / le parallélisme ?", default=False).ask():
        rate_label = questionary.select("Limite de débit :", choices=list(_RATES),
                                        default="Illimité").ask()
        if _cancelled(rate_label):
            return
        kw["limit_rate"] = _RATES[rate_label]
        conc = questionary.select("Parallèle :", choices=["1", "4", "8", "16"],
                                  default="4").ask()
        if _cancelled(conc):
            return
        kw["concurrent"] = int(conc)
        resume.append(f"réseau {rate_label}/{conc}x")

    plan = plan_custom(CustomChoices(**kw))
    print("\n── Récapitulatif (combo) ──")
    print("  " + "  ·  ".join(resume))
    print(f"  Dossier : {plan.output_dir}")
    _confirm_and_run(plan, run_custom)


def _confirm_and_run(plan, run_fn) -> None:
    """Toggle « voir la commande » (Q3) + confirmation + exécution, commun à tous les flows."""
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

    _execute(run_fn(plan), plan.output_dir)


def _execute(events, output_dir) -> None:
    print()
    logs: list[str] = []
    postproc_announced = False
    result: RunResult | None = None

    try:
        for ev in events:
            if isinstance(ev, ProgressEvent):
                if ev.phase == "download" and ev.percent is not None:
                    print(f"\r  ⬇️  Téléchargement… {ev.percent:5.1f}%", end="", flush=True)
                elif ev.phase == "postproc" and not postproc_announced:
                    postproc_announced = True
                    print("\r  ⚙️  Finalisation (fusion / conversion)…        ")
            elif isinstance(ev, LogLine):
                logs.append(ev.text)
            elif isinstance(ev, RunResult):
                result = ev
    except KeyboardInterrupt:
        print("\n⏹️  Interrompu.")
        return

    print()
    if result is not None and result.ok:
        # Listing récursif (les playlists rangent dans des sous-dossiers).
        files = sorted(p for p in output_dir.rglob("*") if p.is_file()) \
            if output_dir.exists() else []
        print("✅  Terminé !")
        print(f"   📁 {output_dir}")
        for p in files[:10]:
            print(f"   • {p.relative_to(output_dir)}")
        if len(files) > 10:
            print(f"   … et {len(files) - 10} autres fichiers")
    else:
        print("❌  Échec du téléchargement.")
        errors = result.errors if result else []
        for e in errors[:3]:
            print("   " + e)
        if questionary.confirm("Voir les détails techniques ?", default=False).ask():
            for line in logs[-25:]:
                print("   " + line)


def _flow_download_video() -> None:
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
            "⚡ Rapide (meilleure qualité, MP4, tags, dossier auto)",
            "🎛️  Personnaliser",
        ],
    ).ask()
    if _cancelled(mode):
        return

    choices = VideoChoices(url=url)
    if mode.startswith("🎛️"):
        choices = _customize_video(url)
        if choices is None:
            return

    plan = plan_download_video(choices)

    res_label = next(
        (k for k, v in _RESOLUTIONS.items() if v == choices.max_height),
        "Meilleure disponible",
    )
    prio = "compatible (H.264/AAC)" if choices.prefer_compatible else "qualité max"
    print("\n── Récapitulatif ──")
    print(f"  Qualité : {res_label}  ·  Conteneur : {choices.merge_format}  ·  Priorité : {prio}")
    print(f"  Pochette: {'oui' if choices.embed_thumbnail else 'non'}  ·  "
          f"Tags : {'oui' if choices.embed_metadata else 'non'}")
    print(f"  Dossier : {plan.output_dir}")

    _confirm_and_run(plan, run_download_video)


def _customize_video(url: str) -> VideoChoices | None:
    res_label = questionary.select(
        "Qualité (résolution) :",
        choices=list(_RESOLUTIONS),
        default="Meilleure disponible",
    ).ask()
    if _cancelled(res_label):
        return None

    priorite = questionary.select(
        "Priorité :",
        choices=[
            questionary.Choice(
                "🛡️  Compatibilité maximale",
                description="H.264/AAC : se lit sur tous les appareils/lecteurs. Plafonne vers 1080p."),
            questionary.Choice(
                "💎  Qualité maximale",
                description="Meilleure image possible (AV1/VP9, jusqu'en 4K/8K) mais illisible sur vieux lecteurs."),
        ],
        show_description=True,
    ).ask()
    if _cancelled(priorite):
        return None
    prefer_compatible = priorite.startswith("🛡️")

    container = questionary.select(
        "Conteneur :", choices=["mp4", "mkv", "webm"], default="mp4"
    ).ask()
    if _cancelled(container):
        return None

    thumb = questionary.confirm("Incruster la miniature ?", default=False).ask()
    if _cancelled(thumb):
        return None
    meta = questionary.confirm("Écrire les tags (métadonnées) ?", default=True).ask()
    if _cancelled(meta):
        return None

    output_dir = None
    if questionary.confirm(
        "Choisir un dossier de sortie ? (sinon dossier auto daté)", default=False
    ).ask():
        chosen = questionary.path(
            "Dossier :", only_directories=True, file_filter=_hide_hidden
        ).ask()
        if not _cancelled(chosen) and chosen.strip():
            output_dir = chosen.strip()

    return VideoChoices(
        url=url,
        max_height=_RESOLUTIONS[res_label],
        merge_format=container,
        prefer_compatible=prefer_compatible,
        embed_thumbnail=thumb,
        embed_metadata=meta,
        output_dir=output_dir,
    )
