# Spec comportementale — Tracer bullet « Extraire l'audio »

> Premier vertical slice. But : valider de bout en bout la chaîne complète
> (saisie → construction commande → exécution → progression → post-processing → résultat/erreur)
> réutilisable par toutes les autres intentions. Interface-agnostique : le **noyau**
> ne connaît ni Textual ni questionary.

---

## 1. Objectif utilisateur
Transformer une vidéo (URL) en fichier audio (MP3 par défaut), sans connaître yt-dlp,
avec pochette + tags, en quelques choix guidés.

## 2. Parcours nominal (interface-agnostique)

```
[Menu] → « Extraire l'audio »
  1. Saisir l'URL
  2. Format audio ?        (défaut MP3 ; sinon m4a / opus / flac / wav)
  3. Qualité ?             (défaut 192K ; sinon 128K / 256K / 320K / meilleure)
  4. Dossier de sortie ?   (défaut : ./ — dossier courant)
  5. [avancé, replié] Pochette d'album  (défaut ON)
                       Tags/métadonnées  (défaut ON)
  6. Récap + [V] voir la commande (masquée par défaut — Q3)
  7. Confirmer → exécution
  8. Progression en direct (%)  →  « Conversion audio… »  →  ✅ fichier créé : <chemin>
```

## 3. Mapping choix → commande yt-dlp

Commande de référence (défauts) :
```
yt-dlp -x -f bestaudio/best --audio-format mp3 --audio-quality 192K \
       --embed-thumbnail --embed-metadata \
       --no-playlist \
       -o "<OUTDIR>/%(title)s.%(ext)s" \
       "<URL>"
```
> `-f bestaudio/best` : ne télécharge que la piste audio (pas la vidéo complète qu'on jetterait). Optim validée empiriquement le 2026-07-04.

| Choix UI | Fragment commande |
|----------|-------------------|
| (toujours) | `-x` |
| Format audio | `--audio-format <mp3\|m4a\|opus\|flac\|wav\|best>` |
| Qualité | `--audio-quality <192K…>` (ou `0` pour « meilleure ») |
| Dossier | `-o "<OUTDIR>/%(title)s.%(ext)s"` |
| Pochette ON | `--embed-thumbnail` |
| Tags ON | `--embed-metadata` |
| 1 vidéo (défaut) | `--no-playlist` |

> `flac`/`wav` ne portent pas de pochette → si format sans pochette, ignorer silencieusement `--embed-thumbnail` (ne pas planter).

## 4. Défauts intelligents
- Format : **mp3** · Qualité : **192K** · Pochette : **ON** · Tags : **ON** · Playlist : **non** (1 vidéo).
- **Dossier de sortie** : dossier de session dédié, cross-platform :
  `<Téléchargements>/yt-dlp-interactif/audio_<AAAA-MM-JJ>_<HHhMM>/`
  - `<Téléchargements>` résolu selon l'OS (XDG sous Linux, registre sous Windows, `~/Downloads` sous macOS).
  - Préfixe `audio_` = l'intention (les futures : `video_`, `playlist_`…).
  - Créé **paresseusement** (au lancement réel uniquement).
  - L'utilisateur peut surcharger par un dossier de son choix (avancé).

## 5. Cas limites & comportements attendus

| Cas | Comportement |
|-----|--------------|
| **ffmpeg absent** | Détecter AVANT de lancer → message clair « ffmpeg requis pour l'audio », proposer la commande d'install, ne pas lancer. |
| **URL vide / manifestement invalide** | Redemander, ne pas appeler yt-dlp. |
| **URL = playlist** | Détecter → demander : « Playlist de N vidéos. [1] Première seule [2] Toutes [3] Annuler ». (défaut : première) |
| **Vidéo indisponible / privée / géo-bloquée** | Récupérer l'erreur yt-dlp → message humain + détail réel derrière un toggle. |
| **Fichier déjà présent** | Ne pas écraser (`--no-overwrites` implicite) → informer « déjà téléchargé ». |
| **Coupure réseau** | yt-dlp gère ses retries ; si échec final → message + proposer relance. |
| **Ctrl+C pendant le téléchargement** | Arrêt propre, signaler l'interruption, pas de crash Python. |
| **Titre à caractères spéciaux** | Laisser yt-dlp gérer ; option `--restrict-filenames` seulement si l'utilisateur la demande (avancé). |

## 6. Pédagogie (Q3)
- Commande **masquée** au récap. Action « voir la commande » → l'affiche + **explique chaque fragment** en s'appuyant sur la cartographie / doc officielle (ex. `-x` = extraire l'audio, `--audio-quality 192K` = débit cible…).
- L'explication vient d'un dictionnaire option→texte dérivé du JSON de cartographie (pas de texte inventé).

## 7. Découpage du noyau (réutilisable)

```
src/
├── core/
│   ├── command_builder.py   # dict de choix -> list[str] d'arguments (PUR, testable sans réseau)
│   ├── runner.py            # subprocess yt-dlp, yield events (progress/postproc/done/error)
│   ├── progress.py          # parse une ligne stdout yt-dlp -> % / phase
│   ├── paths.py             # dossier Téléchargements cross-platform + dossier de session
│   └── environment.py       # check yt-dlp + ffmpeg présents
└── intents/
    └── extract_audio.py     # défauts + mapping propre à l'intention
```

Les interfaces (Textual / questionary) ne font qu'orchestrer : poser les questions,
appeler `command_builder` puis `runner`, afficher les events. **Zéro logique yt-dlp dans l'UI.**

## 8. Critères de succès (→ tests comportementaux, étape 3)

1. `command_builder` : choix par défaut → liste d'arguments **exactement** égale à la commande de référence §3. (pur, offline)
2. `command_builder` : format `flac` → **pas** de `--embed-thumbnail`. (pur, offline)
3. `command_builder` : dossier personnalisé → `-o` reflète le bon chemin. (pur, offline)
4. `progress.py` : ligne `[download]  42.3% of ...` → renvoie phase=download, percent=42.3. (pur, offline)
5. `progress.py` : ligne `[ExtractAudio] Destination: ...` → phase=postproc. (pur, offline)
6. `environment.py` : ffmpeg absent (simulé) → renvoie erreur explicite. (pur, offline)
7. `paths.py` : contenu `user-dirs.dirs` simulé → renvoie le bon dossier Téléchargements ; nom de session = `audio_AAAA-MM-JJ_HHhMM`. (pur, offline)
8. **Intégration (réseau, marquée `@network`, hors CI)** : URL courte réelle → un `.mp3` avec tags apparaît dans le dossier de session.

> Les tests 1-6 sont la cible TDD (rapides, déterministes, sans réseau). Le 7 valide en réel à la fin.

## 9. Hors périmètre de ce slice (plus tard)
Batch/liste de liens · sélection de plage temporelle · sponsorblock · sous-titres ·
choix fin du client extracteur · reprise avancée. (Le noyau les accueillera sans refonte.)
