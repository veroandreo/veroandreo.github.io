#!/usr/bin/env python3
"""
migrate_v2.py — Hugo/Wowchemy → Quarto, para el sitio de Verónica Andreo
────────────────────────────────────────────────────────────────────────
Reescritura de migrate_hugo_to_quarto_v1.py. Diferencias principales, todas
motivadas por lo que hay realmente en content/ de este repo:

  · Front matter TOML con tomllib (stdlib 3.11+) en vez de un regex que solo
    leía `key = "value"`. Las 51 publicaciones usan TOML y sus campos
    authors / tags / publication_types son arrays: la v1 los perdía todos.
  · Front matter YAML con PyYAML. La v1 truncaba los valores multilínea
    (los abstract de content/event/) a su primera línea.
  · Fechas RFC 1123 de los posts ("Wed, 30 Dec 2020 00:00:00 +0000")
    normalizadas a ISO; Quarto no las ordena de otro modo.
  · Shortcodes {{% callout %}} → ::: {.callout-note}, y aviso para los
    {{< ref >}} y {{< gallery >}} que quedan.
  · Los archivos sueltos (publicaciones) ya no toman como "carpeta del
    bundle" a content/publication/ entera.
  · Migra además lo que la v1 ignoraba: courses/_index.md, la bio completa
    del autor (educación, intereses, organizaciones, redes), el widget
    de experiencia (TOML [[experience]]) y los archivos de static/.

Uso:
    python3 migrate_v2.py --hugo ../../content --quarto .. --static ../../static

Sin dependencias externas salvo PyYAML.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tomllib
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Falta PyYAML. Instalalo con:  python3 -m pip install --user pyyaml")


WARNINGS: list[str] = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)
    print(f"  ⚠  {msg}")


# ── Lectura de front matter ───────────────────────────────────────────────────

def read_front_matter(path: Path) -> tuple[dict, str]:
    """Devuelve (front matter, cuerpo). Soporta TOML (+++) y YAML (---)."""
    text = path.read_text(encoding="utf-8")

    m = re.match(r"^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n?(.*)", text, re.DOTALL)
    if m:
        try:
            return tomllib.loads(m.group(1)), m.group(2).strip()
        except tomllib.TOMLDecodeError as e:
            warn(f"TOML inválido en {path}: {e}")
            return {}, m.group(2).strip()

    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)", text, re.DOTALL)
    if m:
        try:
            return (yaml.safe_load(m.group(1)) or {}), m.group(2).strip()
        except yaml.YAMLError as e:
            warn(f"YAML inválido en {path}: {e}")
            return {}, m.group(2).strip()

    return {}, text.strip()


# ── Escritura de qmd ──────────────────────────────────────────────────────────

def write_qmd(fm: dict, body: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fm_yaml = yaml.safe_dump(
        fm, allow_unicode=True, sort_keys=False, default_flow_style=False, width=100
    ).rstrip()
    content = f"---\n{fm_yaml}\n---\n"
    if body:
        content += f"\n{body}\n"
    dest.write_text(content, encoding="utf-8")


# ── Fechas ────────────────────────────────────────────────────────────────────

def normalize_date(value) -> str | None:
    """Cualquier fecha de Hugo → 'YYYY-MM-DD'."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if hasattr(value, "isoformat") and not isinstance(value, str):
        return value.isoformat()

    s = str(value).strip().strip('"')
    # 2019-09-03T11:00:00Z  /  2009-01-01
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", s)
    if m:
        return m.group(1)
    # Wed, 30 Dec 2020 00:00:00 +0000
    try:
        return parsedate_to_datetime(s).date().isoformat()
    except (TypeError, ValueError):
        warn(f"fecha no reconocida: {value!r}")
        return None


def time_of(value) -> str | None:
    """Hora de un date_end tipo 2019-09-03T13:00:00Z, para las charlas."""
    m = re.match(r"^\d{4}-\d{2}-\d{2}T(\d{2}:\d{2})", str(value))
    return m.group(1) if m else None


# ── Cuerpo: shortcodes de Hugo → sintaxis Quarto ──────────────────────────────

CALLOUT_RE = re.compile(
    r"\{\{%\s*callout\s+(\w+)\s*%\}\}\s*\n(.*?)\n\s*\{\{%\s*/\s*callout\s*%\}\}",
    re.DOTALL,
)


FENCE_LANG = {
    "shell script": "bash",
    "shell": "bash",
    "console": "bash",
}


def convert_body(body: str, ctx: str) -> str:
    if not body:
        return ""

    # ```shell script``` rompe el parseo de Pandoc: el bloque no abre como código
    # y los comentarios `#` de adentro terminan como títulos de sección.
    def fence(m: re.Match) -> str:
        return "```" + FENCE_LANG[m.group(1).strip().lower()]

    body, n = re.subn(r"^```[ \t]*(" + "|".join(FENCE_LANG) + r")[ \t]*$",
                      fence, body, flags=re.M | re.I)
    if n:
        print(f"     · {n} bloque(s) de código con lenguaje normalizado")

    def callout(m: re.Match) -> str:
        kind = m.group(1).lower()
        kind = {"note": "note", "tip": "tip", "warning": "warning",
                "important": "important", "danger": "important"}.get(kind, "note")
        inner = m.group(2).strip()
        return f"::: {{.callout-{kind}}}\n{inner}\n:::"

    body, n = CALLOUT_RE.subn(callout, body)
    if n:
        print(f"     · {n} callout(s) convertido(s)")

    for sc in re.findall(r"\{\{<\s*(\w+)[^>]*>\}\}", body):
        warn(f"{ctx}: shortcode {{{{< {sc} >}}}} sin convertir, revisar a mano")

    return body


def strip_md(s: str) -> str:
    """Quita énfasis markdown de un campo que va al front matter."""
    return re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", str(s)).strip()


# ── Utilidades ────────────────────────────────────────────────────────────────

PUB_TYPE = {
    "0": "Uncategorized", "1": "Conference paper", "2": "Journal article",
    "3": "Preprint", "4": "Report", "5": "Book", "6": "Book section",
    "7": "Thesis", "8": "Patent", "9": "Software", "10": "Poster",
}

LINK_FIELDS = [
    ("url_pdf", "PDF"), ("url_preprint", "Preprint"), ("url_code", "Code"),
    ("url_dataset", "Dataset"), ("url_slides", "Slides"), ("url_video", "Video"),
    ("url_poster", "Poster"), ("url_project", "Project"), ("url_source", "Source"),
]


def as_list(v) -> list:
    if v is None or v == "":
        return []
    return v if isinstance(v, list) else [v]


def collect_links(fm: dict) -> list[tuple[str, str]]:
    out = []
    for key, label in LINK_FIELDS:
        url = str(fm.get(key) or "").strip()
        if url:
            out.append((label, url))
    for lnk in as_list(fm.get("links")):
        if isinstance(lnk, dict) and lnk.get("url"):
            out.append((lnk.get("name") or lnk.get("text") or "Link", lnk["url"]))
    # Los "Follow" a Twitter del Hugo no van más.
    return [(label, url) for label, url in out
            if label.strip().lower() != "follow" and "twitter.com" not in url]


def links_block(links: list[tuple[str, str]]) -> str:
    if not links:
        return ""
    return " · ".join(f"[{label}]({url})" for label, url in links)


def doi_from(fm: dict) -> str | None:
    if fm.get("doi"):
        return str(fm["doi"]).replace("https://doi.org/", "")
    for _, url in collect_links(fm):
        m = re.search(r"doi\.org/(10\.\S+)", url)
        if m:
            return m.group(1)
    return None


def find_featured(src_dir: Path) -> str | None:
    for stem in ("featured", "thumbnail", "preview"):
        for ext in ("png", "jpg", "jpeg", "webp", "gif"):
            if (src_dir / f"{stem}.{ext}").exists():
                return f"{stem}.{ext}"
    return None


def header_image(fm: dict) -> tuple[str | None, str | None]:
    """Imagen declarada en el front matter de Hugo.

    Wowchemy v5 no renderizaba `[header] image`, así que estas URLs estaban
    cargadas pero no se veían en el sitio viejo. En Quarto sí sirven: son la
    figura de cada paper. Las remotas conviene bajarlas (ver descargar_imagenes
    en MIGRACION.md); las que empiezan con `/` apuntan a static/.
    """
    h = fm.get("header") or {}
    img = h.get("image") or fm.get("image") or ""
    cap = h.get("caption") or ""
    if not img:
        return None, None
    if img.startswith("/"):
        img = "../.." + img.replace("/img/", "/assets/img/")
    return img, (cap or None)


def copy_bundle_assets(src_dir: Path, dest_dir: Path) -> int:
    n = 0
    for f in sorted(src_dir.iterdir()):
        if f.is_file() and f.suffix.lower() not in (".md", ".markdown"):
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest_dir / f.name)
            n += 1
    return n


def first_paragraph(body: str, limit: int = 220) -> str | None:
    """Descripción automática para los posts, que no traen summary."""
    for block in body.split("\n\n"):
        b = block.strip()
        if not b or b.startswith(("#", "```", ":::", "!", "<", "|")):
            continue
        b = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", b)      # links → texto
        b = re.sub(r"[*_`]", "", b).replace("\n", " ")
        b = re.sub(r"\s+", " ", b).strip()
        if len(b) < 40:
            continue
        if len(b) > limit:
            cut = b[:limit].rsplit(" ", 1)[0]
            b = cut + "…"
        return b
    return None


# ── Conversores por sección ───────────────────────────────────────────────────

def convert_publication(fm: dict, body: str, src_dir: Path, dest: Path, is_bundle: bool):
    out: dict = {"title": strip_md(fm.get("title", "Untitled"))}

    date = normalize_date(fm.get("date"))
    if date:
        out["date"] = date

    authors = [a for a in as_list(fm.get("authors")) if a]
    if authors:
        out["author"] = [{"name": a} for a in authors]
    else:
        warn(f"{dest.parent.name}: sin autores")

    journal = strip_md(fm.get("publication") or fm.get("publication_short") or "")
    # El journal no va como `description`: en la tarjeta competía con el título.
    # Queda en el cuerpo, en la sección Citation.

    pt = as_list(fm.get("publication_types"))
    if pt:
        out["pub-type"] = PUB_TYPE.get(str(pt[0]), str(pt[0]))

    doi = doi_from(fm)
    if doi:
        out["doi"] = doi

    cats = [str(t) for t in as_list(fm.get("tags")) if t]
    if cats:
        out["categories"] = cats

    # Imagen: primero un featured.* junto al qmd, si no la declarada en Hugo.
    img = find_featured(src_dir) if is_bundle else None
    if img:
        out["image"] = img
    else:
        img, cap = header_image(fm)
        if img:
            out["image"] = img
            if cap:
                out["image-alt"] = cap
            if img.startswith("http"):
                warn(f"{dest.parent.name}: imagen remota ({img[:48]}…), conviene bajarla")

    if fm.get("draft"):
        out["draft"] = True

    # Cuerpo: figura, links, abstract y cita. Las de Hugo vienen vacías.
    parts = []
    if out.get("image"):
        alt = (out.get("image-alt") or out["title"]).replace('"', "'")[:180]
        parts.append(f'![]({out["image"]}){{fig-alt="{alt}" .featured-figure}}')
    lb = links_block(collect_links(fm))
    if lb:
        parts.append(lb)
    abstract = str(fm.get("abstract") or "").strip()
    if abstract:
        parts.append("## Abstract\n\n" + abstract)
    if journal:
        cite = ", ".join(authors[:6]) + (", et al." if len(authors) > 6 else "")
        year = date[:4] if date else ""
        parts.append(f"## Citation\n\n{cite} ({year}). {out['title']}. *{journal}*."
                     + (f" <https://doi.org/{doi}>" if doi else ""))
    if body:
        parts.append(convert_body(body, dest.parent.name))

    write_qmd(out, "\n\n".join(parts), dest)
    if is_bundle:
        copy_bundle_assets(src_dir, dest.parent)


def convert_post(fm: dict, body: str, src_dir: Path, dest: Path, is_bundle: bool):
    out: dict = {"title": strip_md(fm.get("title", "Untitled"))}

    date = normalize_date(fm.get("date"))
    if date:
        out["date"] = date
    lm = normalize_date(fm.get("lastmod") or fm.get("date_modified"))
    if lm and lm != date:
        out["date-modified"] = lm

    body = convert_body(body, dest.parent.name)

    # Sin description: en las tarjetas repetía el primer párrafo del propio post.
    # Si algún día querés una, ponela a mano en el front matter.

    cats = [str(t) for t in as_list(fm.get("tags") or fm.get("categories")) if t]
    if cats:
        out["categories"] = cats

    if is_bundle:
        img = find_featured(src_dir)
        if img:
            out["image"] = img
    if fm.get("draft"):
        out["draft"] = True

    write_qmd(out, body, dest)
    if is_bundle:
        copy_bundle_assets(src_dir, dest.parent)


def convert_talk(fm: dict, body: str, src_dir: Path, dest: Path, is_bundle: bool):
    out: dict = {"title": strip_md(fm.get("title", "Untitled"))}

    date = normalize_date(fm.get("date") or fm.get("start_date"))
    if date:
        out["date"] = date

    authors = [a for a in as_list(fm.get("authors")) if a]
    if authors:
        out["author"] = [{"name": a} for a in authors]

    for key in ("event", "event_url", "location"):
        if fm.get(key):
            out[key] = fm[key]

    end = normalize_date(fm.get("date_end"))
    if end:
        t0, t1 = time_of(fm.get("date")), time_of(fm.get("date_end"))
        out["when"] = f"{date} {t0}–{t1}" if (t0 and t1 and end == date) else f"{date} – {end}"

    cats = [str(t) for t in as_list(fm.get("tags")) if t]
    if cats:
        out["categories"] = cats
    if is_bundle:
        img = find_featured(src_dir)
        if img:
            out["image"] = img
    if fm.get("draft"):
        out["draft"] = True

    parts = []
    lb = links_block(collect_links(fm))
    if lb:
        parts.append(lb)
    abstract = str(fm.get("abstract") or "").strip()
    if abstract:
        parts.append("## Abstract\n\n" + abstract)
    if body:
        parts.append(convert_body(body, dest.parent.name))

    write_qmd(out, "\n\n".join(parts), dest)
    if is_bundle:
        copy_bundle_assets(src_dir, dest.parent)


# ── Recorrido de secciones ────────────────────────────────────────────────────

def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)


def migrate_section(hugo_dir: Path, quarto_dir: Path, convert, label: str) -> int:
    if not hugo_dir.exists():
        print(f"  ⏭  {label}: no existe, se omite")
        return 0

    count = 0
    for entry in sorted(hugo_dir.iterdir()):
        if entry.is_dir():
            src = entry / "index.md"
            if not src.exists():
                mds = sorted(entry.glob("*.md"))
                src = mds[0] if mds else None
            if src is None:
                continue
            slug, src_dir, is_bundle = slugify(entry.name), entry, True
        elif entry.suffix.lower() in (".md", ".markdown") and entry.stem != "_index":
            src, slug, src_dir, is_bundle = entry, slugify(entry.stem), entry.parent, False
        else:
            continue

        fm, body = read_front_matter(src)
        convert(fm, body, src_dir, quarto_dir / slug / "index.qmd", is_bundle)
        print(f"  ✓  {label}/{slug}")
        count += 1
    return count


# ── Páginas que la v1 no tocaba ───────────────────────────────────────────────

def migrate_courses(hugo: Path, quarto: Path) -> int:
    src = hugo / "courses" / "_index.md"
    if not src.exists():
        return 0
    fm, body = read_front_matter(src)
    out = {
        "title": fm.get("title", "Courses"),
        "description": "Cursos y talleres dictados.",
    }
    write_qmd(out, convert_body(body, "courses"), quarto / "courses" / "index.qmd")
    print("  ✓  courses/index.qmd")
    return 1


def read_experience(hugo: Path) -> list[dict]:
    src = hugo / "home" / "experience.md"
    if not src.exists():
        return []
    fm, _ = read_front_matter(src)
    return fm.get("experience", []) or []


def read_contact(hugo: Path) -> dict:
    src = hugo / "home" / "contact.md"
    if not src.exists():
        return {}
    fm, _ = read_front_matter(src)
    return (fm.get("content") or {})


def migrate_about(hugo: Path, quarto: Path) -> int:
    src = hugo / "authors" / "admin" / "_index.md"
    if not src.exists():
        warn("no encontré authors/admin/_index.md")
        return 0

    fm, bio_body = read_front_matter(src)
    parts = [convert_body(bio_body, "about")]

    interests = as_list(fm.get("interests"))
    if interests:
        parts.append("## Interests\n\n" + "\n".join(f"- {i}" for i in interests))

    edu = ((fm.get("education") or {}).get("courses")) or []
    if edu:
        rows = ["| | |", "|---|---|"]
        for c in edu:
            inst = c.get("institution", "")
            year = c.get("year", "")
            rows.append(f"| **{c.get('course','')}** | {inst}, {year} |")
        parts.append("## Education\n\n" + "\n".join(rows))

    exp = read_experience(hugo)
    if exp:
        rows = ["| | |", "|---|---|"]
        for e in exp:
            start = normalize_date(e.get("date_start")) or ""
            end = normalize_date(e.get("date_end")) or "presente"
            company = e.get("company", "")
            if e.get("company_url"):
                company = f"[{company}]({e['company_url']})"
            when = f"{start[:7]} – {end[:7] if end != 'presente' else end}"
            rows.append(f"| **{e.get('title','')}** · {company} | {when}, {e.get('location','')} |")
        parts.append("## Experience\n\n" + "\n".join(rows))
    else:
        warn("no pude leer el widget de experiencia (home/experience.md)")

    contact = read_contact(hugo)
    if contact:
        addr = contact.get("address") or {}
        line = ", ".join(str(addr.get(k)) for k in
                         ("street", "city", "region", "country") if addr.get(k))
        bits = []
        if contact.get("email"):
            bits.append(f"<{contact['email']}>")
        if line:
            bits.append(line)
        for oh in as_list(contact.get("office_hours")):
            bits.append(str(oh))
        parts.append("## Contact\n\n" + "\n".join(f"- {b}" for b in bits))

    out = {
        "title": fm.get("title", "About"),
        "subtitle": fm.get("role", ""),
        "about": {
            "template": "trestles",
            "image": "../assets/img/avatar.jpg",
            "image-width": "15em",
        },
    }
    write_qmd(out, "\n\n".join(p for p in parts if p), quarto / "about" / "index.qmd")
    print("  ✓  about/index.qmd")

    avatar = src.parent / "avatar.jpg"
    if avatar.exists():
        dest = quarto / "assets" / "img" / "avatar.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(avatar, dest)
        print("  ✓  assets/img/avatar.jpg")
    return 1


def migrate_static(static: Path, quarto: Path) -> int:
    if not static or not static.exists():
        return 0
    n = 0
    for rel, dest in [("files/cv.pdf", "assets/cv.pdf"),
                      ("files/cv.html", "assets/cv.html")]:
        f = static / rel
        if f.exists():
            d = quarto / dest
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, d)
            print(f"  ✓  {dest}")
            n += 1
    img_src = static / "img"
    if img_src.exists():
        for f in img_src.rglob("*"):
            if f.is_file():
                d = quarto / "assets" / "img" / f.relative_to(img_src)
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, d)
                n += 1
        print(f"  ✓  assets/img/ ({n - 2} imágenes de static/img)")
    return n


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Hugo/Wowchemy → Quarto (v2)")
    ap.add_argument("--hugo", required=True, help="carpeta content/ de Hugo")
    ap.add_argument("--quarto", required=True, help="raíz del sitio Quarto")
    ap.add_argument("--static", default=None, help="carpeta static/ de Hugo")
    args = ap.parse_args()

    hugo = Path(args.hugo).expanduser().resolve()
    quarto = Path(args.quarto).expanduser().resolve()
    static = Path(args.static).expanduser().resolve() if args.static else None

    if not hugo.exists():
        sys.exit(f"No existe {hugo}")

    print(f"\n🔄  Hugo → Quarto\n    origen:  {hugo}\n    destino: {quarto}\n")

    total = 0
    print("Publicaciones")
    total += migrate_section(hugo / "publication", quarto / "publications",
                             convert_publication, "publications")
    print("\nPosts")
    total += migrate_section(hugo / "post", quarto / "posts", convert_post, "posts")
    print("\nCharlas y talleres")
    total += migrate_section(hugo / "event", quarto / "talks", convert_talk, "talks")
    print("\nPáginas")
    total += migrate_courses(hugo, quarto)
    total += migrate_about(hugo, quarto)
    if static:
        print("\nEstáticos")
        migrate_static(static, quarto)

    print(f"\n✅  {total} elementos migrados")
    if WARNINGS:
        print(f"\n⚠️   {len(WARNINGS)} avisos:")
        for w in WARNINGS:
            print(f"   · {w}")
    print("\nSiguiente paso:  quarto render")


if __name__ == "__main__":
    main()
