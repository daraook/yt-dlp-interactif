# yt-dlp interactif

Rendre **yt-dlp** (puissant mais complexe, ~255 options) accessible à tout le monde.
Au lieu d'un terminal vide qui attend une commande cryptique, l'outil se présente,
propose des choix guidés, demande les infos au bon moment, et exécute à ta place.

> Premier d'une série visant à rendre n'importe quel outil en ligne de commande interactif.

## Prérequis

- **yt-dlp** et **ffmpeg** dans le PATH (obligatoires — l'outil le vérifie au lancement).
- **Python ≥ 3.11**.
- *(Facultatif)* **Deno** : débloque tous les formats YouTube (4K/AV1) et retire un
  avertissement. L'outil marche sans ; il te propose l'install si absent, sans l'imposer.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Lancement

```bash
.venv/bin/ytdlp-interactif
# ou : .venv/bin/python -m ytdlp_interactif
```

## Intentions disponibles

**Télécharger** — 🎬 Vidéo (H.264/AAC compatible par défaut) · 🎵 Audio (MP3…) ·
🎚️ Choisir la qualité (menu des formats réels avec tailles) · 📃 Playlist / chaîne
(rangée + reprise anti-doublon) · 🗂️ Fichier de liens (lot).

**Transformer** — ✂️ Découper un extrait (HH:MM-HH:MM) · 🔄 Convertir (remux/recode) ·
🚫 SponsorBlock (retirer sponsors/intros…) · 💬 Sous-titres · 🖼️ Miniature & métadonnées.

**Cas particuliers** — 🔓 Débloquer (cookies navigateur / géo / âge) · 📺 Live / première ·
⚡ Vitesse / réseau.

**Outils** — 🔍 Inspecter (infos sans télécharger) · ⬆️ Mettre à jour yt-dlp.

Chaque écran offre un toggle **« voir la commande »** : la commande yt-dlp exécutée est
affichée et **chaque option expliquée** (apprentissage actif, masqué par défaut).

## Où atterrissent les fichiers

Dans `~/Téléchargements/yt-dlp-interactif/` (dossier Téléchargements détecté selon l'OS :
Linux/Windows/macOS), un sous-dossier daté par session. Les playlists vont dans un dossier
stable `playlists/` pour que la reprise anti-doublon persiste.

## Développement

```bash
.venv/bin/python -m pytest -q      # 85 tests (purs, sans réseau)
```

Architecture : un **noyau** interface-agnostique (`core/` : construction de commande,
exécution/streaming, parsing progression, chemins, inspection) et des **intentions**
(`intents/`) qui n'assemblent que des choix. L'UI (`ui/`) ne fait que présenter.
Une seconde interface (Textual) est envisagée sans toucher au noyau.
