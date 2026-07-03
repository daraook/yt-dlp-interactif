#!/usr/bin/env python3
"""Parse la sortie `yt-dlp --help` en JSON structure (groupes -> options).

Source de verite : docs/reference/yt-dlp-help-<version>.txt
Sortie          : docs/reference/yt-dlp-options.json

But : cartographier fidelement l'outil (zero invention) et produire une base
reutilisable par l'interface interactive pour construire les menus.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# En-tete de groupe : 2 espaces d'indentation, texte, deux-points final.
GROUP_RE = re.compile(r"^  (?P<name>[A-Z][A-Za-z0-9 ,/()&+-]+):$")
# Ligne d'option : 4 espaces d'indentation, commence par un tiret.
OPTION_RE = re.compile(r"^    (?P<sig>-\S.*?)(?:  +(?P<desc>\S.*))?$")


def split_signature(sig: str) -> dict:
    """Separe une signature type '-x, --extract-audio' + metavar eventuel."""
    flags: list[str] = []
    metavar = None
    # Chaque forme est separee par ', ' ; le metavar suit le dernier flag.
    for part in sig.split(", "):
        part = part.strip()
        m = re.match(r"^(--?[A-Za-z0-9][\w-]*)(?:[ =](.+))?$", part)
        if not m:
            flags.append(part)
            continue
        flags.append(m.group(1))
        if m.group(2):
            metavar = m.group(2).strip()
    short = next((f for f in flags if re.fullmatch(r"-[A-Za-z]", f)), None)
    long = next((f for f in flags if f.startswith("--")), None)
    return {"flags": flags, "short": short, "long": long, "metavar": metavar}


def parse(text: str) -> list[dict]:
    groups: list[dict] = []
    current: dict | None = None
    last_opt: dict | None = None

    for raw in text.splitlines():
        gm = GROUP_RE.match(raw)
        if gm:
            current = {"group": gm.group("name").strip(), "options": []}
            groups.append(current)
            last_opt = None
            continue
        if current is None:
            continue
        om = OPTION_RE.match(raw)
        if om:
            info = split_signature(om.group("sig").strip())
            last_opt = {
                **info,
                "description": (om.group("desc") or "").strip(),
            }
            current["options"].append(last_opt)
            continue
        # Ligne de continuation de description (fortement indentee, pas un flag).
        if last_opt is not None and raw.strip() and raw.startswith("      "):
            sep = " " if last_opt["description"] else ""
            last_opt["description"] += sep + raw.strip()

    return groups


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    src = next((root / "docs" / "reference").glob("yt-dlp-help-*.txt"), None)
    if src is None:
        print("Fichier --help introuvable dans docs/reference/", file=sys.stderr)
        return 1

    groups = parse(src.read_text(encoding="utf-8"))
    total = sum(len(g["options"]) for g in groups)
    out = {
        "source": src.name,
        "groups_count": len(groups),
        "options_count": total,
        "groups": groups,
    }
    dst = root / "docs" / "reference" / "yt-dlp-options.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK -> {dst.relative_to(root)}")
    print(f"groupes : {len(groups)} | options : {total}")
    for g in groups:
        print(f"  {len(g['options']):>3}  {g['group']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
