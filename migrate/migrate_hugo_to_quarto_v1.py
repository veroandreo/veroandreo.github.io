#!/usr/bin/env python3
"""
migrate_hugo_to_quarto.py  —  zero dependencies (stdlib only)
─────────────────────────────────────────────────────────────
Migrates Hugo Academic / Wowchemy content to Quarto listing format.

Usage:
    python3 migrate_hugo_to_quarto.py \
        --hugo  /path/to/hugo-site/content \
        --quarto /path/to/quarto-site

Sections converted:
    content/publication/<slug>/index.md  →  publications/<slug>/index.qmd
    content/post/<slug>/index.md         →  posts/<slug>/index.qmd
    content/talk/<slug>/index.md         →  talks/<slug>/index.qmd
    content/event/<slug>/index.md        →  talks/<slug>/index.qmd

No external packages needed — requires Python 3.8+ only.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path


# ── Minimal YAML helpers (handles Hugo Academic front matter) ─────────────────

def _unquote(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or \
       (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def parse_yaml_fm(text: str) -> dict:
    """
    Parse the subset of YAML used in Hugo Academic front matter.
    Handles: scalars, quoted strings, lists (block and flow), nested dicts (image:).
    Not a full YAML parser — good enough for Hugo Academic files.
    """
    result = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip blank / comment lines
        if not line.strip() or line.strip().startswith('#'):
            i += 1
            continue

        # Top-level key: value
        m = re.match(r'^(\w[\w\-]*)\s*:\s*(.*)', line)
        if not m:
            i += 1
            continue

        key, rest = m.group(1), m.group(2).strip()

        # Nested dict (e.g. image:)
        if rest == '' and i + 1 < len(lines) and re.match(r'^  \w', lines[i+1]):
            nested = {}
            i += 1
            while i < len(lines) and re.match(r'^  (\w[\w\-]*)\s*:\s*(.*)', lines[i]):
                nm = re.match(r'^  (\w[\w\-]*)\s*:\s*(.*)', lines[i])
                nested[nm.group(1)] = _unquote(nm.group(2))
                i += 1
            result[key] = nested
            continue

        # Flow list:  key: [a, b, c]
        if rest.startswith('['):
            inner = rest.strip('[]')
            items = [_unquote(x) for x in inner.split(',') if x.strip()]
            result[key] = items
            i += 1
            continue

        # Block list (next lines start with '  - ')
        if rest == '':
            block_items = []
            i += 1
            while i < len(lines) and re.match(r'^[ \t]+-', lines[i]):
                item_line = lines[i]
                # Simple scalar item
                item_m = re.match(r'^[ \t]+-\s*(.*)', item_line)
                if item_m:
                    item_val = item_m.group(1).strip()
                    # Sub-dict item (e.g. links: - name: ... url: ...)
                    if re.match(r'\w+\s*:', item_val):
                        sub = {}
                        sub_m = re.match(r'(\w[\w\-]*)\s*:\s*(.*)', item_val)
                        if sub_m:
                            sub[sub_m.group(1)] = _unquote(sub_m.group(2))
                        i += 1
                        while i < len(lines) and re.match(r'^    \w', lines[i]):
                            sub_line = re.match(r'^    (\w[\w\-]*)\s*:\s*(.*)', lines[i])
                            if sub_line:
                                sub[sub_line.group(1)] = _unquote(sub_line.group(2))
                            i += 1
                        block_items.append(sub)
                    else:
                        block_items.append(_unquote(item_val))
                        i += 1
                else:
                    i += 1
            result[key] = block_items
            continue

        # Multi-line string (|  or >)
        if rest in ('|', '>', '|-', '>-'):
            ml_lines = []
            i += 1
            while i < len(lines) and (lines[i].startswith('  ') or lines[i].strip() == ''):
                ml_lines.append(lines[i][2:] if lines[i].startswith('  ') else '')
                i += 1
            result[key] = '\n'.join(ml_lines).strip()
            continue

        # Scalar
        result[key] = _unquote(rest)
        i += 1

    return result


def read_hugo_md(path: Path):
    """Return (front_matter_dict, body_str)."""
    text = path.read_text(encoding='utf-8')

    # YAML front matter
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)', text, re.DOTALL)
    if m:
        return parse_yaml_fm(m.group(1)), m.group(2).strip()

    # TOML front matter
    m = re.match(r'^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n?(.*)', text, re.DOTALL)
    if m:
        print(f"  ⚠  TOML front matter in {path.name} — basic parsing only")
        # Very basic TOML: just grab key = "value" lines
        fm = {}
        for line in m.group(1).splitlines():
            tm = re.match(r'^(\w[\w\-]*)\s*=\s*"([^"]*)"', line)
            if tm:
                fm[tm.group(1)] = tm.group(2)
        return fm, m.group(2).strip()

    return {}, text.strip()


# ── YAML writer (stdlib-only, clean output) ───────────────────────────────────

def _yaml_scalar(v) -> str:
    if isinstance(v, bool):
        return 'true' if v else 'false'
    s = str(v)
    # Quote if contains special chars
    if any(c in s for c in ':#{}[]|>&*!,?@`"\'') or s in ('true','false','null','~','') \
       or re.match(r'^[\d\-]', s):
        s = s.replace('"', '\\"')
        return f'"{s}"'
    return s


def _yaml_dump(obj, indent=0) -> str:
    pad = '  ' * indent
    if isinstance(obj, dict):
        lines = []
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append(f'{pad}{k}:')
                lines.append(_yaml_dump(v, indent + 1))
            else:
                lines.append(f'{pad}{k}: {_yaml_scalar(v)}')
        return '\n'.join(lines)
    elif isinstance(obj, list):
        lines = []
        for item in obj:
            if isinstance(item, dict):
                first = True
                for k, v in item.items():
                    prefix = f'{pad}- ' if first else f'{pad}  '
                    first = False
                    if isinstance(v, (dict, list)):
                        lines.append(f'{prefix}{k}:')
                        lines.append(_yaml_dump(v, indent + 1))
                    else:
                        lines.append(f'{prefix}{k}: {_yaml_scalar(v)}')
            else:
                lines.append(f'{pad}- {_yaml_scalar(item)}')
        return '\n'.join(lines)
    else:
        return f'{pad}{_yaml_scalar(obj)}'


def write_qmd(fm: dict, body: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    yaml_str = _yaml_dump(fm)
    content = f'---\n{yaml_str}\n---\n\n{body}\n' if body else f'---\n{yaml_str}\n---\n'
    dest.write_text(content, encoding='utf-8')


# ── Shared utilities ──────────────────────────────────────────────────────────

PUB_TYPE_MAP = {
    '0': 'Uncategorized', '1': 'Conference paper', '2': 'Journal article',
    '3': 'Preprint', '4': 'Report', '5': 'Book', '6': 'Book section',
    '7': 'Thesis', '8': 'Patent', '9': 'Software', '10': 'Poster',
}


def first_nonempty(*vals):
    for v in vals:
        if v:
            return v
    return None


def convert_authors(raw):
    if not raw:
        return None
    if isinstance(raw, str):
        raw = [raw]
    return [{'name': a} if isinstance(a, str) else a for a in raw]


def find_featured_image(src_dir: Path):
    for ext in ('jpg', 'jpeg', 'png', 'webp', 'gif'):
        for stem in ('featured', 'thumbnail', 'preview'):
            if (src_dir / f'{stem}.{ext}').exists():
                return f'{stem}.{ext}'
    return None


def build_links(fm: dict):
    links = []
    for lnk in (fm.get('links') or []):
        if isinstance(lnk, dict):
            name = lnk.get('name') or lnk.get('text') or 'Link'
            url  = lnk.get('url')  or lnk.get('href')
            if url:
                links.append({'text': name, 'href': url})
    for key, label in [('url_pdf','PDF'),('url_code','Code'),('url_dataset','Dataset'),
                        ('url_slides','Slides'),('url_video','Video'),('url_poster','Poster')]:
        if fm.get(key):
            links.append({'text': label, 'href': fm[key]})
    doi = fm.get('doi')
    if doi and not any('doi.org' in l['href'] for l in links):
        links.append({'text': 'DOI', 'href': f'https://doi.org/{doi}'})
    return links or None


def copy_assets(src_dir: Path, dest_dir: Path):
    for f in src_dir.iterdir():
        if f.is_file() and f.suffix.lower() not in ('.md', '.markdown'):
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest_dir / f.name)


# ── Converters ────────────────────────────────────────────────────────────────

def convert_publication(fm, body, src_dir, dest_dir):
    out = {'title': fm.get('title', 'Untitled')}
    if fm.get('date'):     out['date'] = fm['date']
    authors = convert_authors(fm.get('authors') or fm.get('author'))
    if authors:            out['author'] = authors
    desc = first_nonempty(fm.get('abstract'), fm.get('summary'))
    if desc:               out['description'] = desc
    if fm.get('publication'):       out['publication'] = fm['publication']
    if fm.get('publication_short'): out['publication_short'] = fm['publication_short']
    pt = fm.get('publication_types')
    if pt:
        pt = pt[0] if isinstance(pt, list) else pt
        out['pub_type'] = PUB_TYPE_MAP.get(str(pt), str(pt))
    if fm.get('doi'):      out['doi'] = fm['doi']
    cats = fm.get('tags') or fm.get('keywords') or []
    if cats:               out['categories'] = list(cats)
    img = find_featured_image(src_dir)
    if img:                out['image'] = img
    links = build_links(fm)
    if links:              out['links'] = links
    if fm.get('draft'):    out['draft'] = True
    write_qmd(out, body, dest_dir)
    copy_assets(src_dir, dest_dir.parent)


def convert_post(fm, body, src_dir, dest_dir):
    out = {'title': fm.get('title', 'Untitled')}
    if fm.get('date'):     out['date'] = fm['date']
    lm = fm.get('lastmod') or fm.get('date_modified')
    if lm and lm != fm.get('date'): out['date-modified'] = lm
    authors = convert_authors(fm.get('authors') or fm.get('author'))
    if authors:            out['author'] = authors
    desc = first_nonempty(fm.get('summary'), fm.get('abstract'), fm.get('description'))
    if desc:               out['description'] = desc
    cats = fm.get('tags') or fm.get('categories') or []
    if cats:               out['categories'] = list(cats)
    img = find_featured_image(src_dir)
    if img:                out['image'] = img
    if fm.get('draft'):    out['draft'] = True
    write_qmd(out, body, dest_dir)
    copy_assets(src_dir, dest_dir.parent)


def convert_talk(fm, body, src_dir, dest_dir):
    out = {'title': fm.get('title', 'Untitled')}
    if fm.get('date') or fm.get('start_date'):
        out['date'] = fm.get('date') or fm.get('start_date')
    if fm.get('date_end'):  out['date-end'] = fm['date_end']
    authors = convert_authors(fm.get('authors') or fm.get('author'))
    if authors:             out['author'] = authors
    desc = first_nonempty(fm.get('abstract'), fm.get('summary'))
    if desc:                out['description'] = desc
    for f in ('event', 'event_url', 'location'):
        if fm.get(f):       out[f] = fm[f]
    cats = fm.get('tags') or []
    if cats:                out['categories'] = list(cats)
    img = find_featured_image(src_dir)
    if img:                 out['image'] = img
    links = build_links(fm)
    if links:               out['links'] = links
    if fm.get('draft'):     out['draft'] = True
    write_qmd(out, body, dest_dir)
    copy_assets(src_dir, dest_dir.parent)


# ── Section walker ────────────────────────────────────────────────────────────

def migrate_section(hugo_section: Path, quarto_section: Path, converter, label: str):
    if not hugo_section.exists():
        print(f'  ⏭  {label}: not found, skipping.')
        return 0
    count = 0
    for entry in sorted(hugo_section.iterdir()):
        if entry.is_dir():
            src_md = entry / 'index.md'
            if not src_md.exists():
                src_md = entry / '_index.md'
            if not src_md.exists():
                mds = list(entry.glob('*.md'))
                src_md = mds[0] if mds else None
            if not src_md:
                continue
            slug, src_dir = entry.name, entry
        elif entry.suffix.lower() in ('.md', '.markdown') and entry.stem != '_index':
            src_md, slug, src_dir = entry, entry.stem, entry.parent
        else:
            continue
        print(f'  ✓  {label}/{slug}')
        fm, body = read_hugo_md(src_md)
        converter(fm, body, src_dir, quarto_section / slug / 'index.qmd')
        count += 1
    return count


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description='Migrate Hugo Academic → Quarto (no dependencies)')
    p.add_argument('--hugo',   required=True, help='Hugo content/ directory')
    p.add_argument('--quarto', required=True, help='Quarto site root')
    p.add_argument('--sections',
        default='publication:publications,post:posts,talk:talks,event:talks')
    args = p.parse_args()

    hugo_content = Path(args.hugo).expanduser().resolve()
    quarto_root  = Path(args.quarto).expanduser().resolve()

    if not hugo_content.exists():
        sys.exit(f'Hugo content dir not found: {hugo_content}')

    type_converters = {
        'publications': convert_publication,
        'posts':        convert_post,
        'talks':        convert_talk,
    }

    print(f'\n🔄  Hugo → Quarto migration')
    print(f'    Hugo:   {hugo_content}')
    print(f'    Quarto: {quarto_root}\n')

    total = 0
    for pair in args.sections.split(','):
        if ':' not in pair: continue
        h, q = pair.strip().split(':', 1)
        total += migrate_section(hugo_content / h, quarto_root / q,
                                  type_converters.get(q, convert_post), h)

    # Author bio
    bio_md = hugo_content / 'authors' / 'admin' / '_index.md'
    if bio_md.exists():
        print(f'\n  ✓  authors/admin/_index.md → about/bio_migrated.qmd')
        fm, body = read_hugo_md(bio_md)
        dest = quarto_root / 'about' / 'bio_migrated.qmd'
        out = {'title': fm.get('name', 'About'), 'role': fm.get('role', ''),
               'bio': fm.get('bio', '')}
        write_qmd(out, body, dest)
        admin_dir = bio_md.parent
        for ext in ('jpg', 'png', 'webp'):
            av = admin_dir / f'avatar.{ext}'
            if av.exists():
                shutil.copy2(av, quarto_root / 'about' / av.name)
        total += 1

    print(f'\n✅  Done — {total} items migrated to {quarto_root}')
    print('\n⚠️  Check manually:')
    print('   • Local URLs like /files/paper.pdf → update to full path')
    print('   • Hugo shortcodes {{< ... >}} → convert to Quarto equivalents')
    print('   • Run `quarto preview` to catch rendering errors')

if __name__ == '__main__':
    main()
