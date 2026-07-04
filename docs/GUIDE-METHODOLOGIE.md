# Guide — Donner une interface interactive à un outil en ligne de commande

Ce document décrit la **méthode** employée pour construire `yt-dlp interactif`, afin de la
**réappliquer à n'importe quel autre outil en ligne de commande** (ffmpeg, ImageMagick,
rsync, git, pandoc, un scanner réseau, un compilateur…). C'est un guide de démarche, pas
un manuel de yt-dlp.

---

## 1. Le problème

Les outils en ligne de commande sont puissants mais **intimidants** :

- beaucoup d'options, de drapeaux, de syntaxes à mémoriser ;
- un terminal vide ne guide pas : il faut *déjà savoir* quoi taper ;
- les combinaisons utiles ne sont pas découvrables.

Résultat : des outils excellents restent inaccessibles à la majorité.

## 2. La stratégie

On ne réécrit pas l'outil : on l'**enveloppe** dans un assistant qui parle le langage de
l'utilisateur (« ce que je veux faire ») et le traduit en commandes.

Trois idées directrices :

1. **Raisonner par intentions, pas par options.** L'utilisateur pense « extraire l'audio »,
   pas « `-x --audio-format mp3` ». On expose des *intentions*, chacune reliée à un sous-ensemble
   d'options avec des **valeurs par défaut intelligentes**.
2. **Séparer le cerveau de l'affichage.** Un *noyau* sans interface décide et exécute ; une
   *interface* se contente de poser des questions et d'afficher. On peut changer d'interface
   sans toucher au noyau.
3. **Vérité empirique.** On cartographie l'outil depuis sa doc/aide réelle, et on valide
   chaque intention par un vrai test (vrai fichier produit), pas par supposition.

## 3. La démarche, étape par étape

### Étape 1 — Cartographier l'outil (depuis la source de vérité)

Récupérer l'aide réelle de la version installée (`outil --help`, la doc officielle) et en
extraire une **carte** structurée : groupes de fonctionnalités, options, ce qui prend un
argument, ce qui est un simple drapeau. Idéalement, produire un fichier **machine-readable**
(JSON) en *parsant* l'aide plutôt qu'en recopiant à la main (zéro invention, régénérable à
chaque montée de version).

> Exemple ici : `tools/parse_help.py` transforme `yt-dlp --help` en
> `docs/reference/yt-dlp-options.json` (255 options, 17 groupes).

### Étape 2 — Définir la couche « intentions »

Traduire les groupes techniques en **intentions utilisateur**. Pour chacune : quelles options
elle mobilise, et quel est le **défaut intelligent** (le choix que 90 % des gens veulent).
Cette table est le squelette des menus.

> Exemple : « Extraire l'audio » → `-x --audio-format mp3 --audio-quality 192K` + pochette + tags.

### Étape 3 — Construire le noyau (sans interface)

Quatre briques réutilisables, toutes **testables sans l'outil réel** :

- **Constructeur de commande** : `(choix) -> list[str]` d'arguments. Fonction *pure*.
- **Exécuteur (runner)** : lance le processus, transforme sa sortie en **flux d'événements**
  (progression / étape / fin / erreur). Rend le sous-processus *injectable* pour les tests.
- **Parseur de progression** : une ligne de sortie -> un état d'avancement.
- **Environnement / chemins** : vérifier les dépendances, résoudre les dossiers cross-platform.

### Étape 4 — Une intention = un petit module d'orchestration

Chaque intention assemble : *choix par défaut* → *plan* (commande + dossier de sortie, pur)
→ *exécution* (crée le dossier, lance le runner). Ajouter une intention ne touche pas au reste.

### Étape 5 — L'interface (fine)

L'interface ne fait que **poser des questions et afficher des événements**. Aucune logique
de l'outil dedans. Elle appelle le noyau. On peut en avoir plusieurs (questionnaire simple,
TUI riche, web…) partageant le même noyau.

### Étape 6 — Valider en réel

Tests unitaires purs pour la logique (rapides, déterministes, hors réseau) **et** un test
de bout en bout avec un vrai lien / vrai fichier pour prouver que ça marche vraiment.

## 4. Principes transverses (ce qui fait la qualité)

- **Défauts intelligents** : l'utilisateur doit pouvoir tout valider par Entrée et obtenir
  un bon résultat. Les réglages fins sont en mode « avancé », repliés.
- **Pédagogie optionnelle** : proposer d'afficher la commande générée *et de l'expliquer*.
  L'utilisateur apprend s'il le souhaite, sans être noyé par défaut.
- **Inspecter avant d'agir** : quand l'outil peut lister l'état réel (formats, tailles…),
  s'en servir pour proposer des choix concrets plutôt que d'exiger une syntaxe.
- **Dépendances optionnelles : proposer, jamais imposer.** Une dépendance externe utile mais
  non bloquante → on la *propose* (avec la commande d'installation) et on explique son intérêt.
  L'outil doit fonctionner sans.
- **Sorties cross-platform** : détecter les dossiers standard selon l'OS ; ranger clairement
  (sous-dossier daté par session, nomenclature explicite).
- **Robustesse d'exécution** : parser stdout/stderr pour la progression et les erreurs ;
  message clair côté utilisateur, détail technique disponible à la demande.
- **Combinabilité** : au-delà des intentions figées, prévoir un mode « personnalisé » qui
  empile les options à la carte (c'est le pont vers un moteur générique).

## 5. Architecture type (à recopier)

```
src/<paquet>/
├── core/
│   ├── command_builder.py   # (choix) -> arguments — PUR
│   ├── runner.py            # exécution -> flux d'événements (sous-processus injectable)
│   ├── progress.py          # ligne de sortie -> avancement
│   ├── environment.py       # dépendances (dures) + astuces (optionnelles)
│   └── paths.py             # dossiers cross-platform
├── intents/                 # une intention = défauts + plan (pur) + exécution
└── ui/                      # présentation uniquement ; zéro logique métier
tests/                       # unitaires purs + au moins un test réel de bout en bout
docs/                        # cartographie de l'outil + specs + ce guide
tools/                       # utilitaires (ex. parseur d'aide -> JSON)
```

## 6. Checklist pour un nouvel outil

- [ ] Aide/doc de la version installée capturée et **parsée** en une carte structurée.
- [ ] Liste des **intentions** + défauts intelligents rédigée.
- [ ] Noyau : constructeur (pur) + runner (injectable) + progression + environnement + chemins.
- [ ] Chaque intention = module `plan`/`run` + test pur.
- [ ] Interface qui ne fait que présenter.
- [ ] Pédagogie « voir la commande » branchée sur la carte.
- [ ] Dépendances dures vérifiées au lancement ; dépendances utiles **proposées** sans imposer.
- [ ] Au moins un **test réel** de bout en bout par intention clé.
- [ ] Lint propre, pas de code mort, dossiers de sortie cross-platform.
- [ ] README clair + ce guide adapté + licence + dépôt installable.

## 7. Pourquoi ça tient à l'échelle

Sur `yt-dlp interactif`, le noyau n'a **pas changé** en passant de 1 à 16 intentions :
chaque nouvelle intention n'a ajouté qu'un constructeur + un module d'orchestration + un
écran. C'est le signe que la séparation *noyau / intentions / interface* est la bonne, et
c'est ce qui rend la méthode réutilisable d'un outil à l'autre.
