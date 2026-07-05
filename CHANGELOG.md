# Journal des modifications

Toutes les modifications notables de ce projet sont consignées ici.

Le format s'inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et le projet suit le [versionnage sémantique](https://semver.org/lang/fr/).

## [1.0.0] — 2026-07-05

Première version stable. Consolidation de la fiabilité et de la clarté à partir de
retours d'usage réels (dont le téléchargement d'une longue playlist sur connexion instable).

### Ajouté
- **Récupération du défi anti-robot YouTube** : quand un téléchargement échoue avec
  « Sign in to confirm you're not a bot », l'outil l'explique et propose en un clic de
  relancer avec le solveur officiel (`--remote-components ejs:github`). Prévient si Deno
  est requis mais absent.
- **Compte rendu de lot** : un téléchargement de playlist/lot partiellement réussi n'est
  plus présenté comme un échec total. Les éléments en échec sont listés, et une reprise
  sûre (sans re-télécharger les réussis, grâce à l'archive anti-doublon) est proposée.
- **Message d'échec repensé** : on explique toujours *pourquoi* ; si aucune cause connue
  ne correspond, on rassure l'utilisateur et on le renvoie vers le projet officiel yt-dlp
  (avec le réflexe « mettre à jour yt-dlp »).
- Sections de documentation explicitant le **périmètre** (l'outil est une interface, le
  téléchargement est fait par yt-dlp), les **fonctions spécifiques à YouTube**, et le fait
  que l'outil **ne transcrit pas** l'audio (il récupère les sous-titres existants).
- Fichiers de dépôt : `CHANGELOG.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, gabarit de
  pull request, `.editorconfig`, `.gitattributes`.

### Modifié
- **Repli de format audio** : le sélecteur passe de `bestaudio/best` à `bestaudio/18/best`.
  Quand une vidéo n'a pas de piste audio seule, on télécharge un flux muxé léger (itag 18,
  ~300 Mo côté YouTube) plutôt qu'un flux HLS d'~1 Go pour le même son final.
- **Nettoyage des titres** : une extension vidéo résiduelle en fin de titre est retirée
  (`--replace-in-metadata`) pour éviter les doubles extensions (ex. `clip.mp4.mp3`).
- Métadonnées de packaging enrichies (classifiers, URLs, version stable).

## [0.1.0] — 2026-07-04

- Première mouture publiée : 16 intentions couvrant les usages réels de yt-dlp,
  menus guidés avec descriptions, réglages par défaut intelligents, commande yt-dlp
  expliquée à la demande, traduction des erreurs, vérification des dépendances,
  intégration continue (Python 3.11–3.13).

[1.0.0]: https://github.com/daraook/yt-dlp-interactif/releases/tag/v1.0.0
[0.1.0]: https://github.com/daraook/yt-dlp-interactif/releases/tag/v0.1.0
