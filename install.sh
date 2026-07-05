#!/usr/bin/env bash
# Installateur tout-en-un de yt-dlp interactif (Linux / macOS).
#
#   Lancer :  bash install.sh
#   Sans questions (auto « oui ») :  bash install.sh --yes
#
# Vérifie Python 3.11+, yt-dlp et ffmpeg, propose d'installer ce qui manque
# (apt / dnf / brew selon le système), puis installe l'outil et le rend
# lançable avec la commande « ytdlp-interactif ».
set -euo pipefail

REPO="daraook/yt-dlp-interactif"

YES=0
for a in "$@"; do case "$a" in -y|--yes) YES=1 ;; esac; done

# --- Détection du gestionnaire de paquets ---
PM=""
if command -v apt-get >/dev/null 2>&1; then PM="apt"
elif command -v dnf     >/dev/null 2>&1; then PM="dnf"
elif command -v brew    >/dev/null 2>&1; then PM="brew"
fi

have() { command -v "$1" >/dev/null 2>&1; }

ask() { # ask "question" -> 0 si oui. Lit sur le terminal (marche même via « curl | bash »).
    local r
    [[ $YES -eq 1 ]] && return 0
    if [[ -r /dev/tty ]]; then
        read -r -p "$1 [O/n] " r </dev/tty
    else
        read -r -p "$1 [O/n] " r
    fi
    [[ -z "$r" || "$r" =~ ^[OoYy] ]]
}

pkg_install() { # pkg_install <nom-de-paquet> <libellé>
    local pkg="$1" label="$2"
    case "$PM" in
        apt)  sudo apt-get update && sudo apt-get install -y "$pkg" ;;
        dnf)  sudo dnf install -y "$pkg" ;;
        brew) brew install "$pkg" ;;
        *)    echo "  Aucun gestionnaire de paquets reconnu — installe $label manuellement." >&2
              return 1 ;;
    esac
    hash -r 2>/dev/null || true  # rafraîchit le cache PATH de bash après l'install
}

echo
echo "=== yt-dlp interactif — installation (Linux/macOS) ==="
echo

# --- 1. Python 3.11+ ---
py_ok() { python3 -c 'import sys; raise SystemExit(0 if sys.version_info[:2] >= (3,11) else 1)' 2>/dev/null; }
if have python3 && py_ok; then
    echo "✓ Python 3.11+ présent."
else
    echo "Python 3.11+ est requis et n'a pas été trouvé."
    if ask "Installer Python maintenant ?"; then
        pkg_install python3 "Python 3"
    else
        echo "  (Requis pour fonctionner.)"; exit 1
    fi
fi

# --- 2. yt-dlp ---
if have yt-dlp; then
    echo "✓ yt-dlp présent."
else
    echo "yt-dlp (moteur de téléchargement) est requis."
    ask "Installer yt-dlp maintenant ?" && pkg_install yt-dlp "yt-dlp" || \
        echo "  (Requis pour fonctionner.)"
fi

# --- 3. ffmpeg ---
if have ffmpeg; then
    echo "✓ ffmpeg présent."
else
    echo "ffmpeg (audio, fusion, conversion) est requis."
    ask "Installer ffmpeg maintenant ?" && pkg_install ffmpeg "ffmpeg" || \
        echo "  (Requis pour l'audio/la fusion.)"
fi

# --- 4. Récupérer le wheel de la dernière release ---
echo
echo "Recherche de la dernière version publiée…"
WHEEL_URL="$(python3 - "$REPO" <<'PY'
import json, sys, urllib.request
repo = sys.argv[1]
url = f"https://api.github.com/repos/{repo}/releases/latest"
req = urllib.request.Request(url, headers={"User-Agent": "ytdlp-interactif-installer"})
data = json.load(urllib.request.urlopen(req))
for a in data.get("assets", []):
    if a["name"].endswith(".whl"):
        print(a["browser_download_url"]); break
PY
)"
if [[ -z "$WHEEL_URL" ]]; then
    echo "Aucun wheel trouvé dans la dernière release." >&2; exit 1
fi

# --- 5. Installer l'outil (pipx de préférence) ---
ensure_pipx() {
    have pipx && return 0
    python3 -m pipx --version >/dev/null 2>&1 && return 0
    echo "Installation de pipx…"
    pkg_install pipx "pipx" 2>/dev/null || python3 -m pip install --user pipx
    python3 -m pipx ensurepath >/dev/null 2>&1 || true
}

if ensure_pipx; then
    echo "Installation via pipx…"
    if have pipx; then pipx install --force "$WHEEL_URL"
    else python3 -m pipx install --force "$WHEEL_URL"; fi
else
    echo "Installation via pip (--user)…"
    python3 -m pip install --user --upgrade "$WHEEL_URL"
fi

echo
echo "✅ Terminé. Lance l'outil avec :  ytdlp-interactif"
echo "   (si la commande n'est pas trouvée, rouvre le terminal, ou lance :  python3 -m ytdlp_interactif )"
echo
