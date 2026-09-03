#!/usr/bin/env python3
"""Aplica el mapa de armonización de categorías sobre los .qmd del sitio.

Lee los archivos como están en el momento de correr, así que no se desincroniza
si se editaron categorías a mano. Con --dry-run solo informa.

    python3 migrate/aplicar_categorias.py --dry-run
    python3 migrate/aplicar_categorias.py
"""
import argparse, collections, pathlib, re, sys
import yaml

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from mapa_categorias import MAPA, BORRAR

SECCIONES = ("publications", "posts", "talks")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = pathlib.Path(args.root)

    antes, despues = collections.Counter(), collections.Counter()
    sin_categorias, tocados = [], 0

    for sec in SECCIONES:
        for p in sorted((root / sec).glob("*/index.qmd")):
            txt = p.read_text(encoding="utf-8")
            m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.DOTALL)
            if not m:
                continue
            fm = yaml.safe_load(m.group(1)) or {}
            cats = [str(c) for c in (fm.get("categories") or [])]
            if not cats:
                continue
            antes.update(cats)

            nuevas, vistas = [], set()
            for c in cats:
                d = MAPA.get(c, c)
                if d in BORRAR or d in vistas:
                    continue
                vistas.add(d)
                nuevas.append(d)
            despues.update(nuevas)

            if nuevas == cats:
                continue
            tocados += 1
            if not nuevas:
                sin_categorias.append(str(p))
                fm.pop("categories", None)
            else:
                fm["categories"] = nuevas
            print(f"  {p.parent.name}\n      {cats}\n   →  {nuevas or '(sin categorías)'}")
            if not args.dry_run:
                out = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False,
                                     default_flow_style=False, width=100).rstrip()
                p.write_text(f"---\n{out}\n---\n{m.group(2)}", encoding="utf-8")

    print(f"\n{'(simulacro) ' if args.dry_run else ''}{tocados} archivos cambiados")
    print(f"etiquetas: {len(antes)} → {len(despues)}   ·   usos: {sum(antes.values())} → {sum(despues.values())}")
    if sin_categorias:
        print(f"\n⚠  {len(sin_categorias)} quedaron sin ninguna categoría:")
        for s in sin_categorias:
            print(f"   · {s}")
    print("\nVocabulario final:")
    for c, n in sorted(despues.items(), key=lambda x: (-x[1], x[0].lower())):
        print(f"  {n:>2}  {c}")


if __name__ == "__main__":
    main()
