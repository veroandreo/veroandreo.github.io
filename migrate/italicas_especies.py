#!/usr/bin/env python3
"""Pone en itálica los nombres científicos en títulos y cuerpos de los .qmd.

  python3 migrate/italicas_especies.py --dry-run
  python3 migrate/italicas_especies.py

No toca: bloques de código, código en línea, URLs, ni los campos de autores
o categorías del front matter (Quarto no interpreta markdown ahí).
"""
import argparse, pathlib, re, sys

BINOMIALES = [
    "Aedes aegypti", "Aedes albopictus", "Aedes japonicus", "Aedes koreicus",
    "Akodon azarae", "Calomys venustus", "Calomys fecundus", "Calomys musculinus",
    "Oligoryzomys longicaudatus", "Oligoryzomys flavescens",
    "Lutzomyia longipalpis", "Evandromyia correalimai",
    "Plasmodium falciparum", "Trypanosoma cruzi", "Leishmania infantum",
    "Triatoma infestans", "Ixodes ricinus", "Rhipicephalus microplus",
    "Rosa rubiginosa", "Plantago lanceolata", "Rumex acetosella",
    "Holcus lanatus", "Mulinum spinosum", "Ochetophila trinervis",
    "Tamarix ramosissima",
]
# Géneros que también van en itálica cuando aparecen solos.
# "Rosa" queda afuera a propósito: colisiona con el apellido de una coautora.
GENEROS = [
    "Aedes", "Anopheles", "Culex", "Lutzomyia", "Evandromyia",
    "Akodon", "Calomys", "Oligoryzomys", "Nothofagus", "Austrocedrus",
    "Tamarix", "Leishmania", "Plasmodium", "Trypanosoma", "Triatoma",
    "Rickettsia",
]

TERMINOS = sorted(BINOMIALES, key=len, reverse=True) + sorted(GENEROS, key=len, reverse=True)
RE_TERMINOS = re.compile(r"(?<![*_\w])(" + "|".join(re.escape(t) for t in TERMINOS) + r")(?![*_\w])")


def italizar(texto: str) -> tuple[str, int]:
    """Envuelve los términos en *...* fuera de código y de itálicas existentes."""
    piezas = re.split(r"(```.*?```|`[^`\n]+`|\]\([^)]*\)|https?://\S+|\*[^*\n]+\*|_[^_\n]+_)",
                      texto, flags=re.S)
    n = 0
    for i, pieza in enumerate(piezas):
        if i % 2:                      # separadores: no se tocan
            continue
        piezas[i], k = RE_TERMINOS.subn(lambda m: f"*{m.group(1)}*", pieza)
        n += k
    return "".join(piezas), n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    total = archivos = 0
    for p in sorted(pathlib.Path(".").glob("*/*/index.qmd")):
        txt = p.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.DOTALL)
        if not m:
            continue
        fm, cuerpo = m.group(1), m.group(2)

        # front matter: solo el título (puede ocupar varias líneas)
        def fix_titulo(mt):
            nuevo, k = italizar(mt.group(2))
            fix_titulo.n += k
            return mt.group(1) + nuevo
        fix_titulo.n = 0
        fm2 = re.sub(r"(?m)^(title:\s*)(.*(?:\n  .*)*)$", fix_titulo, fm)

        cuerpo2, kc = italizar(cuerpo)
        k = fix_titulo.n + kc
        if not k:
            continue
        total += k
        archivos += 1
        print(f"  {p.parent.name}: {k}")
        if not args.dry_run:
            p.write_text(f"---\n{fm2}\n---\n{cuerpo2}", encoding="utf-8")

    print(f"\n{'(simulacro) ' if args.dry_run else ''}{total} nombres en {archivos} archivos")


if __name__ == "__main__":
    main()
