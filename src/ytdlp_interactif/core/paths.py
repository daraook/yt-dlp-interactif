"""Résolution cross-platform du dossier Téléchargements + dossier de session.

Objectif : un dossier de session dédié et daté sous
`<Téléchargements>/yt-dlp-interactif/<intention>_<date>_<heure>/`, identique de
comportement sous Linux / Windows / macOS. Les entrées externes (OS, home, contenu
XDG, registre) sont injectables pour des tests déterministes.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

_APP_DIR = "yt-dlp-interactif"
_XDG_RE = re.compile(r'^\s*XDG_DOWNLOAD_DIR\s*=\s*"(.*)"\s*$', re.MULTILINE)


def parse_xdg_download(content: str, home: Path) -> Path | None:
    """Extrait XDG_DOWNLOAD_DIR d'un contenu user-dirs.dirs, $HOME résolu."""
    m = _XDG_RE.search(content)
    if not m:
        return None
    raw = m.group(1)
    raw = raw.replace("$HOME", str(home)).replace("${HOME}", str(home))
    return Path(raw)


def _read_xdg_file(home: Path) -> str | None:
    path = home / ".config" / "user-dirs.dirs"
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def downloads_dir(
    *,
    system: str | None = None,
    home: Path | None = None,
    xdg_content: str | None = None,
    win_query: Callable[[], Path | None] | None = None,
) -> Path:
    """Retourne le dossier Téléchargements de l'utilisateur selon l'OS."""
    system = system if system is not None else sys.platform
    home = home if home is not None else Path.home()

    if system.startswith("win"):
        if win_query is not None:
            found = win_query()
            if found is not None:
                return found
        else:
            found = _windows_downloads()
            if found is not None:
                return found
        return home / "Downloads"

    if system == "darwin":
        return home / "Downloads"

    # Linux / autres : XDG en priorité, puis fallbacks localisés.
    content = xdg_content if xdg_content is not None else _read_xdg_file(home)
    if content:
        xdg = parse_xdg_download(content, home)
        if xdg is not None:
            return xdg
    for name in ("Downloads", "Téléchargements"):
        if (home / name).is_dir():
            return home / name
    return home / "Downloads"


def _windows_downloads() -> Path | None:
    """Dossier connu 'Downloads' via le registre Windows (repli si échec)."""
    try:
        import winreg  # noqa: PLC0415 (import spécifique Windows)

        sub = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        guid = "{374DE290-123F-4565-9164-39C4925E467B}"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub) as key:
            value, _ = winreg.QueryValueEx(key, guid)
        import os

        return Path(os.path.expandvars(value))
    except Exception:
        return None


def session_dir(
    intention: str = "audio",
    *,
    base: Path | None = None,
    now: datetime | None = None,
) -> Path:
    """Chemin du dossier de session (NON créé : création paresseuse au lancement)."""
    base = base if base is not None else downloads_dir()
    now = now if now is not None else datetime.now()
    name = f"{intention}_{now:%Y-%m-%d_%Hh%M}"
    return base / _APP_DIR / name


def library_dir(subdir: str, *, base: Path | None = None) -> Path:
    """Dossier STABLE (non horodaté) sous l'app — pour les archives persistantes.

    Ex. les playlists : re-télécharger la même playlist doit reprendre là où on
    s'était arrêté grâce à l'archive, donc le dossier ne doit pas changer.
    """
    base = base if base is not None else downloads_dir()
    return base / _APP_DIR / subdir
