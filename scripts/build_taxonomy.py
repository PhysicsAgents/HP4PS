"""Build homepage/data/taxonomy.json from the source tables in references/taxonomy/.

Levels 1-3 are PACS 2010 (domain, subfield, branch). Each node carries its PACS code
and the GB/T 13745-2009 codes mapped onto it by gb_to_pacs.tsv. The build fails if a
PACS node lacks a Chinese name, a mapping points at an unknown PACS code, or any
GB/T 13745 physics (140) code is left unmapped.
"""

import csv
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'references' / 'taxonomy'
OUT = ROOT / 'homepage' / 'data' / 'taxonomy.json'


def rows(name):
    with open(SRC / name, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def node_id(code):
    # '40.' -> '40', '47.' -> '47', '47.27.-i' -> '47.27'
    return code.rstrip('.') if code.count('.') == 1 else code[:5]


def english(name, level):
    name = html.unescape(name)
    return name.capitalize() if level == 1 else name


def build():
    errors = []
    pacs = rows('pacs2010_levels1-3.tsv')
    zh = {r['code']: r['zh'] for r in rows('pacs2010_zh.tsv')}
    known = {r['code'] for r in pacs}
    gb_physics = {r['code']: r['name'] for r in rows('gb13745_2009_physics.tsv')}

    gb_on = {}
    mapped = set()
    for r in rows('gb_to_pacs.tsv'):
        mapped.add(r['gb'])
        for code in r['pacs'].split(','):
            if code not in known:
                errors.append(f'gb_to_pacs: {r["gb"]} -> unknown PACS code {code}')
            gb_on.setdefault(code, []).append(r['gb'])
        if r['gb'] in gb_physics and gb_physics[r['gb']] != r['name']:
            errors.append(f'gb_to_pacs: {r["gb"]} name "{r["name"]}" differs from standard "{gb_physics[r["gb"]]}"')
    errors += [f'GB/T 13745 physics code {code} {name} is not mapped' for code, name in gb_physics.items() if code not in mapped]

    nodes, by_code = [], {}
    for r in pacs:
        level, code = int(r['level']), r['code']
        if code not in zh:
            errors.append(f'pacs2010_zh: no Chinese name for {code}')
        source = {'PACS': code}
        if code in gb_on:
            source['GB'] = sorted(set(gb_on[code]), key=lambda c: (len(c), c))
        node = {'id': node_id(code), 'name': {'en': english(r['name'], level), 'zh': zh.get(code, '')}, 'source': source}
        by_code[code] = node
        if level == 1:
            nodes.append(node)
        else:
            parent = by_code.get(r['parent'])
            if parent is None:
                errors.append(f'pacs2010: parent {r["parent"]} of {code} not found')
                continue
            parent.setdefault('children', []).append(node)

    ids = [n['id'] for n in by_code.values()]
    errors += [f'duplicate node id {i}' for i in sorted({i for i in ids if ids.count(i) > 1})]
    return nodes, by_code, errors


if __name__ == '__main__':
    nodes, by_code, errors = build()
    for error in errors:
        print(error)
    if errors:
        sys.exit(1)
    taxonomy = {
        'standards': {'PACS': 'PACS 2010', 'GB': 'GB/T 13745-2009'},
        'nodes': nodes,
    }
    OUT.write_text(json.dumps(taxonomy, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    subfields = sum(len(n.get('children', [])) for n in nodes)
    print(f'taxonomy: {len(nodes)} domains, {subfields} subfields, {len(by_code) - len(nodes) - subfields} branches')
