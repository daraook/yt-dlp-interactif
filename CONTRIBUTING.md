# Contribuer

Merci de ton intérêt ! Les contributions — corrections, nouvelles fonctionnalités,
amélioration de l'interface ou de la documentation — sont les bienvenues.

## Signaler un problème ou proposer une idée

Ouvre une [issue](https://github.com/daraook/yt-dlp-interactif/issues) en décrivant :
- ce que tu faisais et l'URL/le site concerné (sans données personnelles) ;
- ce que tu attendais, et ce qui s'est réellement passé ;
- si possible, le message affiché par « voir les détails techniques ».

## Mettre en place l'environnement de développement

```bash
git clone https://github.com/daraook/yt-dlp-interactif.git
cd yt-dlp-interactif
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

Avant d'ouvrir une pull request :

```bash
.venv/bin/python -m pytest -q      # tous les tests doivent passer
.venv/bin/ruff check src tests     # lint propre
```

## Architecture (rappel)

Séparation stricte **noyau / intentions / interface** (voir
[`docs/GUIDE-METHODOLOGIE.md`](docs/GUIDE-METHODOLOGIE.md)) :

- `core/` — logique sans interface : construction de commande (pure), exécution,
  progression, inspection, chemins, environnement.
- `intents/` — une intention = défauts + `plan` (pur) + `run`.
- `ui/` — présentation uniquement (aucune logique yt-dlp).

## Ajouter une intention (recette)

1. **Constructeur** dans `core/command_builder.py` : une fonction pure
   `(choix) -> list[str]`. Ajoute des tests dans `tests/` (sortie exacte attendue).
2. **Orchestration** dans `intents/<nom>.py` : un `dataclass` de choix, `plan_<nom>`
   (pur : commande + dossier) et `run_<nom>` (crée le dossier, délègue au runner).
3. **Explications** dans `ui/explain.py` : ajoute une entrée par option pour le mode
   « voir la commande ».
4. **Écran** dans `ui/questionary_ui.py` : un `_flow_<nom>` qui pose les questions et
   appelle `_confirm_and_run`, puis une entrée dans le menu.
5. **Valide en réel** avec un vrai lien avant d'ouvrir la PR.

## Style

- Code et commentaires en français, cohérents avec l'existant.
- Fonctions pures et testables autant que possible ; aucune logique métier dans `ui/`.
- Messages de commit clairs : « quoi + pourquoi ».
