# Cartographie yt-dlp — Fondation du wrapper interactif

> **Source de vérité** : `yt-dlp --version` = **2026.06.09** · `docs/reference/yt-dlp-help-2026.06.09.txt`
> **Carte machine-readable** : `docs/reference/yt-dlp-options.json` (17 groupes · 255 options)
> **Doc officielle croisée** : README yt-dlp (chapitres FORMAT SELECTION, OUTPUT TEMPLATE, CONFIGURATION…)
> **Date cartographie** : 2026-07-03

Ce document est la **couche humaine** de la carte. La liste exhaustive des 255 options
vit dans le JSON ; ici on garde la structure, les options-clés et surtout la
**traduction usages → options**, qui deviendra l'arbre de menus de l'outil.

---

## 1. Vue d'ensemble

- **255 options** réparties en **17 groupes fonctionnels**.
- **104 options prennent un argument** (metavar), **151 sont des drapeaux booléens** (souvent en paire `--x` / `--no-x`).
- 2 options structurent 90 % des usages : **`-f/--format`** (quoi télécharger) et **`-o/--output`** (où/comment nommer).
- Dépendance externe clé : **ffmpeg** (extraction audio, fusion vidéo+audio, incrustation sous-titres/miniatures). Présent sur la machine ✓

| # | Groupe | Options | Rôle en une phrase |
|---|--------|:------:|--------------------|
| 1 | General Options | 33 | Comportement global : aide, update, gestion d'erreurs, config |
| 2 | Network Options | 8 | Proxy, timeout, source IP, forçage IPv4/IPv6 |
| 3 | Geo-restriction | 2 | Contourner blocages géographiques |
| 4 | Video Selection | 21 | *Quelles* vidéos d'une URL/playlist prendre (filtres, plage, dates) |
| 5 | Download Options | 23 | *Comment* télécharger : vitesse, fragments, reprise, portions |
| 6 | Filesystem Options | 37 | Chemins, nommage (`-o`), archive, cookies, fichiers annexes |
| 7 | Thumbnail Options | 4 | Écrire / incruster / lister les miniatures |
| 8 | Internet Shortcut Options | 4 | Créer des raccourcis `.url`/`.webloc`/`.desktop` |
| 9 | Verbosity and Simulation | 23 | Inspecter sans télécharger, logs, `--print`, `-F`, `-j` |
| 10 | Workarounds | 10 | User-agent, headers, encodage, contournements divers |
| 11 | Video Format Options | 16 | Sélection/tri de format (`-f`, `-S`, `-F`), conteneur de fusion |
| 12 | Subtitle Options | 7 | Sous-titres : écrire, auto-générés, langues, incruster, convertir |
| 13 | Authentication Options | 14 | Login, mot de passe, `.netrc`, cookies navigateur, certificats |
| 14 | Post-Processing Options | 37 | Après téléchargement : extraire audio, remux, incruster, métadonnées |
| 15 | SponsorBlock Options | 5 | Marquer / retirer segments sponsors, intros, etc. |
| 16 | Extractor Options | 6 | Réglages spécifiques aux extracteurs, retries, arguments avancés |
| 17 | Preset Aliases | 5 | Raccourcis prêts à l'emploi (`-t mp3`, `-t mp4`, `-t sleep`…) |

---

## 2. Les 17 groupes — options-clés

> Liste **curatée** (les plus utiles pour un utilisateur non-technique).
> Exhaustivité → `yt-dlp-options.json`.

### 1. General Options
- `-U, --update` / `--update-to CHANNEL@TAG` — mettre à jour yt-dlp
- `-i, --ignore-errors` / `--abort-on-error` — continuer malgré les erreurs
- `--flat-playlist` — lister les entrées d'une playlist sans les extraire
- `--live-from-start` / `--wait-for-video` — gestion des lives
- `--config-location PATH` / `--ignore-config` — fichier de configuration

### 2. Network Options
- `--proxy URL` — proxy HTTP/HTTPS/SOCKS
- `--socket-timeout SEC`, `--source-address IP`
- `-4/--force-ipv4`, `-6/--force-ipv6`

### 3. Geo-restriction
- `--geo-verification-proxy URL`
- `--xff VALUE` — en-tête X-Forwarded-For (contournement géo)

### 4. Video Selection *(quelles vidéos)*
- `-I, --playlist-items ITEMSPEC` — ex. `1:5,8,10:` (plage d'éléments)
- `--min-filesize` / `--max-filesize`
- `--date`, `--datebefore`, `--dateafter` — filtrer par date de publication
- `--match-filters FILTER` — filtre générique (ex. `"duration>60 & view_count>1000"`)
- `--no-playlist` / `--yes-playlist` — 1 vidéo vs playlist entière
- `--max-downloads N`, `--break-on-existing`

### 5. Download Options *(comment télécharger)*
- `-N, --concurrent-fragments N` — parallélisme (accélère)
- `-r, --limit-rate RATE` — brider la bande passante (ex. `2M`)
- `-R, --retries N`, `--file-access-retries`, `--fragment-retries`
- `--download-sections REGEX` — ne prendre qu'une portion (ex. `"*10:00-15:00"`)
- `-c, --continue` / `--no-continue` — reprise de téléchargement
- `--throttled-rate`, `--buffer-size`

### 6. Filesystem Options *(où / comment nommer)*
- `-o, --output [TYPES:]TEMPLATE` — **modèle de nom** (voir §4)
- `-P, --paths [TYPES:]PATH` — dossiers de destination par type
- `--restrict-filenames` — noms ASCII sûrs
- `-w, --no-overwrites`, `--force-overwrites`
- `--download-archive FILE` — ne pas re-télécharger ce qui est déjà pris
- `--cookies FILE`, `--cookies-from-browser BROWSER`
- `--write-info-json`, `--write-description`

### 7. Thumbnail Options
- `--write-thumbnail` — enregistrer la miniature à part
- `--embed-thumbnail` — l'incruster dans le fichier (via post-processing)
- `--list-thumbnails`

### 8. Internet Shortcut Options
- `--write-link` / `--write-url-link` / `--write-webloc-link` / `--write-desktop-link`

### 9. Verbosity and Simulation *(inspecter sans télécharger)*
- `-s, --simulate` — tout simuler, rien écrire
- `-F, --list-formats` — **lister les formats disponibles** (clé pour choisir la qualité)
- `--print TEMPLATE`, `-j/--dump-json`, `-J/--dump-single-json`
- `-g, --get-url`, `--list-subs`, `--list-thumbnails`
- `-v, --verbose`, `--quiet`, `--no-warnings`, `--progress`

### 10. Workarounds
- `--user-agent UA`, `--referer URL`, `--add-headers FIELD:VALUE`
- `--sleep-requests`, `--sleep-interval` / `--max-sleep-interval` — anti-blocage
- `--encoding`, `--no-check-certificates`

### 11. Video Format Options *(sélection de qualité)*
- `-f, --format FORMAT` — **sélecteur de format** (voir §3)
- `-S, --format-sort SORTORDER` — trier les formats (ex. `res,fps,vcodec`)
- `-F, --list-formats` — lister (doublon logique de §9)
- `--merge-output-format EXT` — conteneur de fusion (mp4, mkv…)
- `--check-formats`, `--prefer-free-formats`

### 12. Subtitle Options
- `--write-subs` / `--write-auto-subs` — sous-titres manuels / auto-générés
- `--sub-langs LANGS` — ex. `"en,fr,es"` ou `"all"`
- `--embed-subs` — incruster (post-processing)
- `--convert-subs FORMAT` — srt, vtt, ass…
- `--list-subs`

### 13. Authentication Options
- `-u/--username`, `-p/--password`, `-2/--twofactor`
- `-n, --netrc`, `--netrc-location`
- `--cookies-from-browser BROWSER[+KEYRING][:PROFILE]` — réutiliser sa session
- `--video-password`, `--client-certificate`

### 14. Post-Processing Options *(après téléchargement — nécessite ffmpeg)*
- `-x, --extract-audio` — **extraire l'audio uniquement**
- `--audio-format FORMAT` — mp3, m4a, opus, flac, wav… (`best` par défaut)
- `--audio-quality Q` — 0 (meilleur) à 10, ou bitrate (ex. `192K`)
- `--remux-video EXT` / `--recode-video EXT` — changer de conteneur / réencoder
- `--embed-metadata`, `--embed-chapters`, `--embed-thumbnail`, `--embed-subs`
- `--split-chapters`, `--sponsorblock-remove`
- `--postprocessor-args ARGS`

### 15. SponsorBlock Options
- `--sponsorblock-mark CATS` / `--sponsorblock-remove CATS` — catégories : `sponsor,intro,outro,selfpromo,interaction,music_offtopic…`
- `--sponsorblock-api URL`

### 16. Extractor Options
- `--extractor-retries N`
- `--extractor-args KEY:ARGS` — réglages avancés par site (ex. `"youtube:player_client=web"`)
- `--allow-dynamic-mpd`, `--mark-watched`

### 17. Preset Aliases *(raccourcis tout-en-un)*
- `-t mp3` — audio MP3 rapide
- `-t mp4` — vidéo mp4 compatible
- `-t sleep` — délais anti-blocage préconfigurés
- (5 presets au total — pratiques pour boutons « 1 clic » dans l'UI)

---

## 3. Concept clé — FORMAT SELECTION (`-f`)

**Sélecteurs spéciaux** : `best`/`b`, `worst`/`w`, `bestvideo`/`bv`, `bestaudio`/`ba`.

| Syntaxe | Sens |
|---------|------|
| `bestvideo+bestaudio` | **fusionne** meilleure vidéo + meilleur audio (nécessite ffmpeg) |
| `format1/format2` | **fallback** : format2 si format1 indisponible |
| `fmt1,fmt2` | sélection **multiple** (télécharge plusieurs) |
| `best[height<=720]` | **filtre** par attribut |

Filtres courants : `[height<=720]`, `[ext=mp4]`, `[filesize<50M]`, `[fps>30]`, `[vcodec^=avc]`.
Tri via `-S` : champs `res, ext, size, br, fps, codec, vcodec, acodec, hdr` (préfixe `-` = décroissant).

Exemples de référence :
```
-f "bestvideo+bestaudio/best"
-f "best[height<=720]"
-f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
-S "res,fps,vcodec:h264" -f best
```

> **Pour l'UI** : `-F` liste les formats réels → on peut présenter un menu de qualités
> concrètes plutôt que d'exiger la syntaxe. Fallback intelligent par défaut : `bestvideo+bestaudio/best`.

---

## 4. Concept clé — OUTPUT TEMPLATE (`-o`)

Syntaxe : `%(champ)s`, avec formatage type printf (`%(playlist_index)02d`), traversée (`%(formats.0.format_id)s`).

Champs utiles : `title, id, ext, uploader, channel, upload_date` (YYYYMMDD), `playlist_title, playlist_index, resolution, duration`.
Modificateurs : `>%Y-%m-%d` (format date), `|Défaut` (valeur si vide), `&remplacement` (si non-vide).

Exemples de référence :
```
-o "%(title)s.%(ext)s"                                              # défaut lisible
-o "%(upload_date)s_%(title)s.%(ext)s"                              # préfixe date
-o "%(uploader)s/%(playlist_title)s/%(playlist_index)02d-%(title)s.%(ext)s"  # rangement playlist
-o "%(channel)s-%(title)s-%(id)s.%(ext)s"                          # anti-collision
```

> **Pour l'UI** : proposer 3-4 modèles préfaits (« titre simple », « rangé par chaîne »,
> « préfixé date », « playlist numérotée ») + mode personnalisé pour experts.

---

## 5. Couche INTENTIONS UTILISATEUR → options (squelette des menus)

C'est le cœur du wrapper : traduire ce que l'utilisateur **veut faire** en options yt-dlp.
Chaque intention = une entrée du menu principal. Les options masquées par défaut (Q3),
dévoilables avec explication tirée de la doc.

| Intention (menu) | Options yt-dlp mobilisées | Défaut intelligent |
|------------------|---------------------------|--------------------|
| **Télécharger une vidéo (simple)** | URL + `-f` | `bestvideo+bestaudio/best`, `-o "%(title)s.%(ext)s"` |
| **Choisir la qualité** | `-F` (lister) → `-f`, `-S`, `--merge-output-format` | menu de résolutions réelles |
| **Extraire l'audio (MP3…)** | `-x`, `--audio-format`, `--audio-quality`, `--embed-thumbnail`, `--embed-metadata` | mp3 192K + pochette + tags |
| **Télécharger une playlist / chaîne** | `--yes-playlist`, `-I`, `--playlist-start/end`, `-o` rangé, `--download-archive` | archive activée, dossier par playlist |
| **Télécharger depuis une liste de liens (lot)** | `-a/--batch-file`, `-o`, `--download-archive` | archive ON, un dossier par source |
| **Sous-titres** | `--write-subs`, `--write-auto-subs`, `--sub-langs`, `--embed-subs`, `--convert-subs` | langue système, incrustation optionnelle |
| **Miniature & métadonnées** | `--embed-thumbnail`, `--embed-metadata`, `--embed-chapters`, `--write-thumbnail` | incruster dans le fichier |
| **Convertir / changer de format** | `--remux-video`, `--recode-video`, `--merge-output-format` | remux sans réencoder (rapide) ; réencodage si demandé |
| **Nommage / dossier de sortie** | `-o`, `-P`, `--restrict-filenames` | modèles préfaits (§4) |
| **Portion d'une vidéo** | `--download-sections`, `--split-chapters` | saisie plage `HH:MM-HH:MM` |
| **Lives & premières** | `--live-from-start`, `--wait-for-video`, `--no-live-from-start` | démarrer au début du live |
| **Contourner un blocage géo / âge** | `--cookies-from-browser`, `--proxy`, `--xff`, `--geo-verification-proxy` | cookies navigateur en 1er recours |
| **Contenu privé / abonné (connexion)** | `-u/-p`, `-2/--twofactor`, `-n/--netrc`, `--video-password`, `--cookies-from-browser` | proposer cookies navigateur avant login manuel |
| **Régler vitesse / réseau** | `-N`, `-r`, `-R`, `-c`, `--sleep-interval` | reprise ON, parallélisme modéré |
| **Retirer les sponsors** | `--sponsorblock-remove`, `--sponsorblock-mark` | catégories sponsor+intro+outro |
| **Inspecter sans télécharger** | `-s`, `-F`, `--list-subs`, `--print`, `-j` | mode « aperçu » |
| **Presets 1 clic** | `-t mp3`, `-t mp4`, `-t sleep` | boutons rapides |
| **Mettre à jour yt-dlp** | `-U`, `--update-to CHANNEL@TAG` | vérifier + appliquer la mise à jour |
| **Config / avancé** | `--config-location`, `--extractor-args`, `--user-agent` | zone experts |

---

## 6. Points d'attention pour le build

- **ffmpeg requis** pour : `-x`, `bestvideo+bestaudio` (fusion), `--embed-*`, `--recode/remux`, `--convert-subs`. → Vérifier sa présence au lancement de l'outil, prévenir sinon.
- **`-F` avant `-f`** : on ne devine pas les formats, on les liste puis on propose. Menu qualité = données réelles.
- **Options en paires** `--x` / `--no-x` : dans l'UI = un simple toggle, pas deux entrées.
- **Preset Aliases** : syntaxe spéciale (`-t nom`), à traiter hors du parseur d'options standard.
- **Sections conceptuelles** (FORMAT SELECTION, OUTPUT TEMPLATE, CONFIGURATION, EXTRACTOR ARGS) : ce sont les textes à ré-exposer pour la pédagogie (Q3) quand l'utilisateur dévoile une commande.
- **Robustesse** : yt-dlp renvoie des codes de sortie + logs → l'UI doit parser stdout/stderr pour la progression et les erreurs, pas juste lancer et attendre.

---

## Annexes (fichiers)
- `yt-dlp-help-2026.06.09.txt` — `--help` brut (source de vérité gelée)
- `yt-dlp-options.json` — 255 options structurées (flags/short/metavar/description)
- `tools/parse_help.py` — régénère le JSON depuis un nouveau `--help` (montée de version)
