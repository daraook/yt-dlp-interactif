# yt-dlp interactif

**Rendre `yt-dlp` utilisable par tout le monde.**

`yt-dlp` est un téléchargeur vidéo/audio extrêmement puissant — mais avec ~255 options
en ligne de commande, il est intimidant pour qui n'est pas à l'aise avec le terminal.
Cet outil le transforme en **assistant interactif** : au lieu d'un terminal vide qui
attend une commande cryptique, il se présente, propose des choix clairs, pose les bonnes
questions au bon moment, et exécute à ta place.

```
? Que veux-tu faire ?  (utilise ↑↓ puis Entrée)
 ── Sur mesure ──
 » 🧩  Personnalisé (tout combiner)
   🔎  Chercher (vidéos & playlists)
 ── Télécharger ──
   🎬  Télécharger une vidéo
   🎵  Extraire l'audio (MP3, …)
   🎚️  Choisir la qualité (formats réels)
   📃  Télécharger une playlist / chaîne
   🗂️  Fichier de liens (lot)
 ── Transformer ──
   ✂️  Découper un extrait  ·  🔄 Convertir  ·  🚫 SponsorBlock  ·  💬 Sous-titres  ·  🖼️ Miniature & métadonnées
   …
   La vidéo complète (image + son). Format compatible H.264/AAC par défaut : lit partout.
```

> Premier d'une série d'outils visant à donner une interface interactive à des programmes
> en ligne de commande. La méthode employée est documentée dans
> [`docs/GUIDE-METHODOLOGIE.md`](docs/GUIDE-METHODOLOGIE.md) pour être réappliquée.

---

## Fonctionnalités

L'outil couvre les usages réels de yt-dlp, regroupés par intention :

**Télécharger** — Vidéo (H.264/AAC compatible par défaut, lit partout) · Audio (MP3, m4a,
opus, flac, wav) · Choisir la qualité (menu des formats réellement disponibles, avec tailles) ·
Playlist / chaîne (rangée par dossier, numérotée, **reprise anti-doublon**) · Fichier de liens (lot).

**Transformer** — Découper un extrait (`HH:MM-HH:MM`, coupe précise) · Convertir
(remux sans perte ou réencodage) · SponsorBlock (retirer/marquer sponsors, intros, outros…) ·
Sous-titres (avec ou sans la vidéo, par langue, incrustables) · Miniature & métadonnées.

**Cas particuliers** — Débloquer (cookies du navigateur pour le contenu privé/membre/âge,
+ contournement géographique) · Live / première (depuis le début, ou en attente) ·
Vitesse / réseau (bride de débit, parallélisme).

**Outils** — Chercher (par mots-clés : liste vidéos **et** playlists, puis télécharge) ·
Inspecter (titre, durée, qualités, sous-titres — sans rien télécharger) · Mettre à jour yt-dlp.

**Sur mesure** — 🧩 **Personnalisé** : empile n'importe quelle combinaison en un seul
téléchargement (ex. *playlist entière + audio seul + retirer les sponsors + sous-titres FR*).

À chaque étape, un choix **« voir la commande »** affiche la commande `yt-dlp` exécutée
et **explique chaque option** — pour apprendre en faisant (masqué par défaut).

## Multi-plateforme

L'outil ne se limite pas à YouTube : les URLs sont passées telles quelles à yt-dlp, qui
gère **~1 800 sites** (Vimeo, Dailymotion, TikTok, SoundCloud, X/Twitter, Facebook, Twitch…),
plus les fichiers média directs via l'extracteur générique. Seul **SponsorBlock** est
spécifique à YouTube.

## Prérequis

| Dépendance | Rôle | Obligatoire |
|-----------|------|:-----------:|
| **yt-dlp** | moteur de téléchargement | ✅ (vérifié au lancement) |
| **ffmpeg** | audio, fusion vidéo+audio, incrustation, conversion | ✅ (vérifié au lancement) |
| **Python ≥ 3.11** | exécuter l'interface | ✅ |
| **Deno** | fiabilise l'extraction YouTube (voir plus bas) | ⚪ facultatif |

## Installation

```bash
git clone <url-du-depot> yt-dlp-interactif
cd yt-dlp-interactif
python3 -m venv .venv
.venv/bin/pip install -e .
```

> Sur les distributions « externally managed » (Debian/Ubuntu/Kali), le venv est la voie
> recommandée. yt-dlp et ffmpeg restent installés séparément (paquet système, `pip`, `brew`…).

## Utilisation

```bash
.venv/bin/ytdlp-interactif
# ou : .venv/bin/python -m ytdlp_interactif
```

Navigue avec ↑↓, valide avec Entrée. Les fichiers atterrissent dans
`~/Téléchargements/yt-dlp-interactif/` (dossier Téléchargements détecté selon l'OS —
Linux/Windows/macOS), dans un sous-dossier daté par session. Les playlists vont dans un
dossier stable `playlists/` pour que la reprise anti-doublon persiste entre deux lancements.

## À propos de Deno (facultatif)

YouTube protège l'accès à ses formats par un « défi JavaScript » (nsig). Pour le résoudre,
yt-dlp a besoin d'un **runtime JavaScript**.

- **Sans runtime JS** : yt-dlp se rabat sur des clients alternatifs. Ça fonctionne le plus
  souvent, mais avec un avertissement, des formats parfois manquants, et davantage de risques
  d'erreurs transitoires (« Video unavailable », throttling) sur certaines vidéos.
- **Avec Deno** (un runtime JS en un seul binaire) : yt-dlp peut résoudre le défi et obtenir
  l'accès complet et fiable aux formats YouTube.

Deno est **externe et optionnel** : il n'est pas embarqué, n'alourdit pas l'outil, et
n'affecte **que** YouTube (aucun effet sur les autres sites). L'outil fonctionne sans ;
s'il est absent, une astuce non bloquante propose de l'installer :

```bash
curl -fsSL https://deno.land/install.sh | sh
```

Pour que yt-dlp exploite pleinement Deno sur les défis récents, ajoute une fois pour toutes
`--remote-components ejs:github` à ta configuration yt-dlp (voir le
[wiki EJS de yt-dlp](https://github.com/yt-dlp/yt-dlp/wiki/EJS)).

## Développement

```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest -q      # tests unitaires (purs, hors réseau)
.venv/bin/ruff check src tests     # lint
```

### Architecture

```
src/ytdlp_interactif/
├── core/          # noyau, indépendant de toute interface
│   ├── command_builder.py   choix -> liste d'arguments yt-dlp (fonctions pures)
│   ├── runner.py            exécute yt-dlp, transforme la sortie en flux d'événements
│   ├── progress.py          parse une ligne de sortie -> progression
│   ├── probe.py             inspecte formats / infos (yt-dlp -J)
│   ├── search.py            recherche (natif yt-dlp)
│   ├── paths.py             dossiers cross-platform (Téléchargements, session)
│   └── environment.py       vérifie les dépendances
├── intents/       # une intention = un assemblage de choix (plan pur + exécution)
└── ui/            # interface questionary : ne fait que présenter (aucune logique yt-dlp)
```

Le noyau ne connaît pas l'interface : on peut lui brancher une autre présentation
(une interface TUI type Textual est envisagée) sans y toucher. La démarche complète
est décrite dans [`docs/GUIDE-METHODOLOGIE.md`](docs/GUIDE-METHODOLOGIE.md).

### Documentation de référence

- [`docs/GUIDE-METHODOLOGIE.md`](docs/GUIDE-METHODOLOGIE.md) — comment donner une interface
  interactive à n'importe quel outil en ligne de commande (méthode réutilisable).
- [`docs/reference/cartographie-yt-dlp.md`](docs/reference/cartographie-yt-dlp.md) —
  cartographie complète de yt-dlp (17 groupes, 255 options) et couche « intentions ».
- [`docs/spec-extraire-audio.md`](docs/spec-extraire-audio.md) — exemple de spécification
  comportementale (première intention).

## Feuille de route

- Interface TUI riche (Textual) en alternative à l'actuelle, sur le même noyau.
- Recherche multi-sites (au-delà de YouTube).
- Généralisation de l'approche à d'autres outils en ligne de commande.

## Licence

MIT — voir [`LICENSE`](LICENSE).
