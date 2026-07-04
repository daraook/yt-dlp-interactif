"""Construction de la commande yt-dlp pour l'intention « Extraire l'audio ».

Fonction PURE : (choix) -> list[str]. Aucun effet de bord, aucun réseau.
C'est le cœur testable ; les interfaces se contentent de l'appeler.
"""
from __future__ import annotations

from pathlib import Path

# Conteneurs audio qui ne portent pas de pochette incrustée.
_SANS_POCHETTE = {"wav", "flac"}


def build_extract_audio_command(
    url: str,
    output_dir: str | Path,
    *,
    audio_format: str = "mp3",
    audio_quality: str = "192K",
    embed_thumbnail: bool = True,
    embed_metadata: bool = True,
    playlist: bool = False,
    format_selector: str | None = "bestaudio/best",
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Retourne la liste d'arguments prête pour subprocess (voir spec §3).

    `format_selector` (défaut `bestaudio/best`) : ne télécharge que la piste audio
    au lieu de la vidéo complète pour n'en garder que le son. None => yt-dlp décide.
    """
    cmd: list[str] = [yt_dlp, "-x"]
    if format_selector:
        cmd += ["-f", format_selector]
    cmd += ["--audio-format", audio_format]
    cmd += ["--audio-quality", audio_quality]

    # La pochette n'a de sens que pour les formats qui la supportent.
    if embed_thumbnail and audio_format not in _SANS_POCHETTE:
        cmd.append("--embed-thumbnail")
    if embed_metadata:
        cmd.append("--embed-metadata")

    cmd.append("--yes-playlist" if playlist else "--no-playlist")

    template = str(Path(output_dir) / "%(title)s.%(ext)s")
    cmd += ["-o", template, url]
    return cmd


def _video_format_selector(max_height: int | None) -> str:
    if max_height:
        return (
            f"bestvideo[height<={max_height}]+bestaudio/"
            f"best[height<={max_height}]/best"
        )
    return "bestvideo+bestaudio/best"


def _media_prefix(
    cmd: list[str],
    *,
    media: str,
    max_height: int | None,
    prefer_compatible: bool,
    merge_format: str,
    audio_format: str,
    audio_quality: str,
    embed_thumbnail_audio: bool = True,
) -> None:
    """Ajoute à `cmd` la sélection vidéo (fusion) OU audio (extraction)."""
    if media == "audio":
        cmd += ["-x", "-f", "bestaudio/best"]
        cmd += ["--audio-format", audio_format, "--audio-quality", audio_quality]
        if embed_thumbnail_audio and audio_format not in _SANS_POCHETTE:
            cmd.append("--embed-thumbnail")
    else:
        cmd += ["-f", _video_format_selector(max_height)]
        if prefer_compatible:
            cmd += ["-S", "vcodec:h264,acodec:aac"]
        cmd += ["--merge-output-format", merge_format]


def _finish(cmd: list[str], output_dir: str | Path, url: str) -> list[str]:
    cmd.append("--no-playlist")
    cmd += ["-o", str(Path(output_dir) / "%(title)s.%(ext)s"), url]
    return cmd


def build_convert_command(
    url: str,
    output_dir: str | Path,
    *,
    target_ext: str = "mp4",
    recode: bool = False,
    max_height: int | None = None,
    prefer_compatible: bool = True,
    embed_metadata: bool = True,
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Télécharge puis change de format. remux = conteneur seul (rapide, sans
    perte) ; recode = réencodage (plus lent, change le codec)."""
    cmd: list[str] = [yt_dlp, "-f", _video_format_selector(max_height)]
    if prefer_compatible:
        cmd += ["-S", "vcodec:h264,acodec:aac"]
    cmd += ["--recode-video", target_ext] if recode else ["--remux-video", target_ext]
    if embed_metadata:
        cmd.append("--embed-metadata")
    return _finish(cmd, output_dir, url)


def build_extras_command(
    url: str,
    output_dir: str | Path,
    *,
    media: str = "video",
    write_thumbnail: bool = False,
    embed_thumbnail: bool = True,
    write_info_json: bool = False,
    embed_metadata: bool = True,
    skip_download: bool = False,
    max_height: int | None = None,
    prefer_compatible: bool = True,
    merge_format: str = "mp4",
    audio_format: str = "mp3",
    audio_quality: str = "192K",
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Gérer miniature et métadonnées : écrire/incruster la miniature, écrire le
    JSON d'infos, incruster les tags. `skip_download` = récupérer les annexes seules."""
    cmd: list[str] = [yt_dlp]
    if skip_download:
        cmd.append("--skip-download")
    else:
        _media_prefix(
            cmd, media=media, max_height=max_height,
            prefer_compatible=prefer_compatible, merge_format=merge_format,
            audio_format=audio_format, audio_quality=audio_quality,
            embed_thumbnail_audio=False,
        )
    if write_thumbnail:
        cmd.append("--write-thumbnail")
    if embed_thumbnail and not skip_download:
        cmd.append("--embed-thumbnail")
    if write_info_json:
        cmd.append("--write-info-json")
    if embed_metadata and not skip_download:
        cmd.append("--embed-metadata")
    return _finish(cmd, output_dir, url)


def build_live_command(
    url: str,
    output_dir: str | Path,
    *,
    from_start: bool = True,
    wait: bool = False,
    wait_interval: str = "30",
    max_height: int | None = None,
    prefer_compatible: bool = True,
    merge_format: str = "mp4",
    embed_metadata: bool = True,
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Télécharger un live/première : depuis le début, et/ou en attendant qu'il commence."""
    cmd: list[str] = [yt_dlp, "-f", _video_format_selector(max_height)]
    if prefer_compatible:
        cmd += ["-S", "vcodec:h264,acodec:aac"]
    cmd += ["--merge-output-format", merge_format]
    if from_start:
        cmd.append("--live-from-start")
    if wait:
        cmd += ["--wait-for-video", wait_interval]
    if embed_metadata:
        cmd.append("--embed-metadata")
    return _finish(cmd, output_dir, url)


def build_unlock_command(
    url: str,
    output_dir: str | Path,
    *,
    browser: str = "firefox",
    geo_bypass: bool = False,
    media: str = "video",
    max_height: int | None = None,
    prefer_compatible: bool = True,
    merge_format: str = "mp4",
    audio_format: str = "mp3",
    audio_quality: str = "192K",
    embed_metadata: bool = True,
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Débloquer une vidéo privée/membre/âge en réutilisant les cookies du
    navigateur, avec contournement géographique optionnel."""
    cmd: list[str] = [yt_dlp]
    _media_prefix(
        cmd, media=media, max_height=max_height,
        prefer_compatible=prefer_compatible, merge_format=merge_format,
        audio_format=audio_format, audio_quality=audio_quality,
    )
    cmd += ["--cookies-from-browser", browser]
    if geo_bypass:
        cmd.append("--geo-bypass")
    if embed_metadata:
        cmd.append("--embed-metadata")
    return _finish(cmd, output_dir, url)


def build_network_command(
    url: str,
    output_dir: str | Path,
    *,
    limit_rate: str | None = None,
    concurrent: int = 4,
    media: str = "video",
    max_height: int | None = None,
    prefer_compatible: bool = True,
    merge_format: str = "mp4",
    audio_format: str = "mp3",
    audio_quality: str = "192K",
    embed_metadata: bool = True,
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Télécharger avec réglages réseau : bride de débit (-r) et parallélisme (-N)."""
    cmd: list[str] = [yt_dlp]
    _media_prefix(
        cmd, media=media, max_height=max_height,
        prefer_compatible=prefer_compatible, merge_format=merge_format,
        audio_format=audio_format, audio_quality=audio_quality,
    )
    if limit_rate:
        cmd += ["-r", limit_rate]
    if concurrent and concurrent > 1:
        cmd += ["-N", str(concurrent)]
    if embed_metadata:
        cmd.append("--embed-metadata")
    return _finish(cmd, output_dir, url)


def build_playlist_command(
    url: str,
    base_dir: str | Path,
    *,
    media: str = "video",  # "video" | "audio"
    max_height: int | None = None,
    prefer_compatible: bool = True,
    merge_format: str = "mp4",
    audio_format: str = "mp3",
    audio_quality: str = "192K",
    embed_thumbnail: bool = True,
    embed_metadata: bool = True,
    items: str | None = None,  # ex. "1-10", "1,3,5", "5:"
    archive: bool = True,
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Commande pour télécharger une playlist/chaîne, rangée et sans doublon.

    Rangement : <base>/<playlist>/NN - titre.ext. Archive persistante
    (<base>/archive.txt) pour reprendre sans re-télécharger.
    """
    cmd: list[str] = [yt_dlp]

    if media == "audio":
        cmd += ["-x", "-f", "bestaudio/best"]
        cmd += ["--audio-format", audio_format, "--audio-quality", audio_quality]
        if embed_thumbnail and audio_format not in _SANS_POCHETTE:
            cmd.append("--embed-thumbnail")
    else:
        cmd += ["-f", _video_format_selector(max_height)]
        if prefer_compatible:
            cmd += ["-S", "vcodec:h264,acodec:aac"]
        cmd += ["--merge-output-format", merge_format]
        if embed_thumbnail:
            cmd.append("--embed-thumbnail")
    if embed_metadata:
        cmd.append("--embed-metadata")

    cmd.append("--yes-playlist")
    if items:
        cmd += ["--playlist-items", items]
    if archive:
        cmd += ["--download-archive", str(Path(base_dir) / "archive.txt")]

    template = str(
        Path(base_dir) / "%(playlist_title)s" / "%(playlist_index)02d - %(title)s.%(ext)s"
    )
    cmd += ["-o", template, url]
    return cmd


def build_section_command(
    url: str,
    output_dir: str | Path,
    *,
    start: str,
    end: str,
    media: str = "video",  # "video" | "audio"
    max_height: int | None = None,
    prefer_compatible: bool = True,
    merge_format: str = "mp4",
    audio_format: str = "mp3",
    audio_quality: str = "192K",
    embed_metadata: bool = True,
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Télécharge seulement un extrait temporel [start-end].

    `start`/`end` acceptent les formats yt-dlp : secondes (90) ou horodatage
    (1:30, 0:01:30). En vidéo, --force-keyframes-at-cuts assure une coupe précise.
    """
    cmd: list[str] = [yt_dlp]
    if media == "audio":
        cmd += ["-x", "-f", "bestaudio/best"]
        cmd += ["--audio-format", audio_format, "--audio-quality", audio_quality]
        if audio_format not in _SANS_POCHETTE:
            cmd.append("--embed-thumbnail")
    else:
        cmd += ["-f", _video_format_selector(max_height)]
        if prefer_compatible:
            cmd += ["-S", "vcodec:h264,acodec:aac"]
        cmd += ["--merge-output-format", merge_format]

    cmd += ["--download-sections", f"*{start}-{end}"]
    if media != "audio":
        cmd.append("--force-keyframes-at-cuts")
    if embed_metadata:
        cmd.append("--embed-metadata")

    cmd.append("--no-playlist")
    template = str(Path(output_dir) / "%(title)s.%(ext)s")
    cmd += ["-o", template, url]
    return cmd


def build_sponsorblock_command(
    url: str,
    output_dir: str | Path,
    *,
    action: str = "remove",  # "remove" (couper) | "mark" (chapitres)
    categories: str = "sponsor",
    max_height: int | None = None,
    prefer_compatible: bool = True,
    merge_format: str = "mp4",
    embed_metadata: bool = True,
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Télécharge une vidéo en retirant (ou marquant) les segments SponsorBlock.

    `categories` : liste séparée par des virgules (sponsor, intro, outro,
    selfpromo, interaction, preview, music_offtopic, filler) ou "all"/"default".
    """
    cmd: list[str] = [yt_dlp, "-f", _video_format_selector(max_height)]
    if prefer_compatible:
        cmd += ["-S", "vcodec:h264,acodec:aac"]
    cmd += ["--merge-output-format", merge_format]

    flag = "--sponsorblock-mark" if action == "mark" else "--sponsorblock-remove"
    cmd += [flag, categories]
    if embed_metadata:
        cmd.append("--embed-metadata")

    cmd.append("--no-playlist")
    template = str(Path(output_dir) / "%(title)s.%(ext)s")
    cmd += ["-o", template, url]
    return cmd


def build_batch_command(
    output_dir: str | Path,
    *,
    urls: list[str] | None = None,
    batch_file: str | Path | None = None,
    media: str = "video",  # "video" | "audio"
    max_height: int | None = None,
    prefer_compatible: bool = True,
    merge_format: str = "mp4",
    audio_format: str = "mp3",
    audio_quality: str = "192K",
    embed_metadata: bool = True,
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Commande pour télécharger plusieurs liens d'un coup.

    Source : `urls` (liens en positionnel) OU `batch_file` (fichier .txt, un lien
    par ligne). Chaque lien est traité comme une vidéo seule (--no-playlist).
    """
    if not urls and not batch_file:
        raise ValueError("Fournir au moins `urls` ou `batch_file`.")

    cmd: list[str] = [yt_dlp]
    if media == "audio":
        cmd += ["-x", "-f", "bestaudio/best"]
        cmd += ["--audio-format", audio_format, "--audio-quality", audio_quality]
        if audio_format not in _SANS_POCHETTE:
            cmd.append("--embed-thumbnail")
    else:
        cmd += ["-f", _video_format_selector(max_height)]
        if prefer_compatible:
            cmd += ["-S", "vcodec:h264,acodec:aac"]
        cmd += ["--merge-output-format", merge_format]
    if embed_metadata:
        cmd.append("--embed-metadata")

    cmd.append("--no-playlist")
    if batch_file:
        cmd += ["--batch-file", str(batch_file)]

    template = str(Path(output_dir) / "%(title)s.%(ext)s")
    cmd += ["-o", template]
    if urls:
        cmd += list(urls)
    return cmd


def build_subtitles_command(
    url: str,
    output_dir: str | Path,
    *,
    mode: str = "video",  # "video" (vidéo + ST) | "subs_only" (ST seuls)
    langs: str = "fr,en",
    auto: bool = True,  # inclure les ST auto-générés
    sub_format: str = "srt",
    embed: bool = False,  # incruster dans la vidéo (mode "video" seulement)
    max_height: int | None = None,
    prefer_compatible: bool = True,
    merge_format: str = "mp4",
    embed_metadata: bool = True,
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Commande pour récupérer les sous-titres, avec ou sans la vidéo.

    `mode="subs_only"` ne télécharge que les fichiers de sous-titres.
    `embed` incruste les ST dans la vidéo (ignoré en subs_only).
    """
    cmd: list[str] = [yt_dlp]

    if mode == "subs_only":
        cmd.append("--skip-download")
    else:
        cmd += ["-f", _video_format_selector(max_height)]
        if prefer_compatible:
            cmd += ["-S", "vcodec:h264,acodec:aac"]
        cmd += ["--merge-output-format", merge_format]

    cmd.append("--write-subs")
    if auto:
        cmd.append("--write-auto-subs")
    cmd += ["--sub-langs", langs]
    if sub_format:
        cmd += ["--convert-subs", sub_format]
    if mode != "subs_only":
        if embed:
            cmd.append("--embed-subs")
        if embed_metadata:
            cmd.append("--embed-metadata")

    cmd.append("--no-playlist")
    template = str(Path(output_dir) / "%(title)s.%(ext)s")
    cmd += ["-o", template, url]
    return cmd


def build_download_video_command(
    url: str,
    output_dir: str | Path,
    *,
    max_height: int | None = None,
    merge_format: str = "mp4",
    prefer_compatible: bool = True,
    embed_thumbnail: bool = False,
    embed_metadata: bool = True,
    playlist: bool = False,
    yt_dlp: str = "yt-dlp",
) -> list[str]:
    """Commande pour télécharger la vidéo (image + son fusionnés).

    `max_height` limite la résolution (720, 1080…) ; None = meilleure disponible.
    `merge_format` = conteneur de fusion vidéo+audio (mp4 par défaut).
    `prefer_compatible` (défaut True) : trie les formats pour préférer H.264/AAC,
    qui se lisent partout (repli gracieux si indisponibles). False = qualité max
    brute (peut donner AV1/VP9, moins compatible mais 4K/8K possible).
    """
    if max_height:
        fmt = (
            f"bestvideo[height<={max_height}]+bestaudio/"
            f"best[height<={max_height}]/best"
        )
    else:
        fmt = "bestvideo+bestaudio/best"

    cmd: list[str] = [yt_dlp, "-f", fmt, "--merge-output-format", merge_format]
    if prefer_compatible:
        cmd += ["-S", "vcodec:h264,acodec:aac"]
    if embed_metadata:
        cmd.append("--embed-metadata")
    if embed_thumbnail:
        cmd.append("--embed-thumbnail")
    cmd.append("--yes-playlist" if playlist else "--no-playlist")

    template = str(Path(output_dir) / "%(title)s.%(ext)s")
    cmd += ["-o", template, url]
    return cmd
