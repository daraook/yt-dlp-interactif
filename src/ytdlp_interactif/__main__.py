"""Point d'entrée : `python -m ytdlp_interactif`.

Lance l'interface questionary (piste B) par défaut. `--ui textual` viendra ensuite.
"""
from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="ytdlp_interactif")
    parser.add_argument(
        "--ui",
        choices=["questionary", "textual"],
        default="questionary",
        help="Interface à utiliser (défaut : questionary).",
    )
    args = parser.parse_args()

    if args.ui == "questionary":
        from .ui.questionary_ui import run_app
        run_app()
    else:
        print("L'interface Textual arrive bientôt.")


if __name__ == "__main__":
    main()
