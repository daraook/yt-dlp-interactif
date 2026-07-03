# Contexte projet — yt-dlp interactif

Wrapper interactif rendant yt-dlp (outil CLI ~255 options) accessible à un non-technicien :
l'outil se présente, propose les options, guide le choix, demande les inputs au bon moment,
et exécute à la place de l'utilisateur. yt-dlp = 1er cas d'un concept réutilisable
(« rendre n'importe quel CLI interactif »), mais **la v1 reste 100 % dédiée yt-dlp**.

# Décisions de cadrage (2026-07-03)
- **Q1 Interface** : construire DEUX pistes — TUI Textual **et** prompts questionary — comparer au rendu, trancher ensuite.
- **Q2 Portée** : 100 % dédié yt-dlp pour la v1. Généralisation (archi réutilisable / moteur générique piloté par config) = exploration ultérieure, non bannie.
- **Q3 Pédagogie** : commande yt-dlp générée **masquée par défaut**, dévoilable à la demande, avec explications tirées de la doc officielle → apprentissage actif.
- **Q4 Départ** : cartographie de l'outil AVANT tout code. ✅ Fait.

# Stack
- Python 3.13.12 · yt-dlp 2026.06.09 · ffmpeg 8.1.1 (présents sur la machine)
- **Kali = PEP 668** : dépendances Python dans un venv projet `.venv/` (pip système bloqué). yt-dlp/ffmpeg restent appelés via le PATH, hors venv.
- venv installé : `questionary` 2.1.1 (piste B), `pytest` 9.1.1. Textual (piste A) à venir.
- Lancer les tests : `.venv/bin/python -m pytest -q`
- Exécution yt-dlp : subprocess + parsing stdout/stderr pour progression & erreurs

# Findings empiriques (voir mémoire projet)
- **YouTube fonctionne** (vérifié 2026-07-04, Rick Astley `dQw4w9WgXcQ`) : clients par défaut, sans runtime JS. Pipeline maison → vrai mp3 avec pochette incrustée. ✅
- Le message verbeux `node (unavailable)` et le `/etc/yt-dlp.conf` (option `--js-runtimes node` commentée) sont **inoffensifs**.
- **URLs à ne PAS utiliser en test** (indisponibles, faux négatifs) : `BaW_jenozKc`, `jNQXAC9WEvI`. Test fiable : `dQw4w9WgXcQ`.
- Piste d'optim à étudier : pour `-x` sans `-f`, forcer `-f "bestaudio/best"` pour ne pas télécharger la vidéo inutilement.

# Fichiers de référence (source de vérité)
- `docs/reference/cartographie-yt-dlp.md` — carte humaine + intentions→options (squelette menus)
- `docs/reference/yt-dlp-options.json` — 255 options structurées (généré)
- `docs/reference/yt-dlp-help-2026.06.09.txt` — `--help` brut gelé
- `tools/parse_help.py` — régénère le JSON à une nouvelle version

# Conventions
- On ne devine jamais les formats : `-F` liste → menu de qualités réelles.
- Options `--x`/`--no-x` = un toggle unique dans l'UI.
- Défauts intelligents par intention (voir §5 cartographie).
- Vérifier ffmpeg au lancement (requis pour audio/fusion/embed/convert).

# Interdictions explicites
- Pas de push/merge sans ordre explicite du MO.
- Ne pas exposer les 255 options brutes à l'utilisateur : passer par la couche intentions.
- Ne pas modifier ce CLAUDE.md unilatéralement (règle protocole Daraook).

# Points de contrôle MO
- Validation de la cartographie avant de figer l'arbre de menus.
- Choix TUI vs prompts après comparaison des deux prototypes.
