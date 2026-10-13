"""Check the bilingual contract: homepage locale key parity and Markdown pairs.

Every `foo.md` in scope needs a sibling `foo.zh.md`. The English file carries
`English | [中文](foo.zh.md)` and the Chinese file `[English](foo.md) | 中文`
on the first line after the H1. Both locale dictionaries must have the same keys.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ROOT / 'homepage' / 'locales'
SKIP_DIRS = {'.git', '.github', 'node_modules', '.venv'}
EXCLUDED = {'AGENTS.md', 'CLAUDE.md'}


def keys(node, prefix=''):
    if not isinstance(node, dict):
        return {prefix}
    return set().union(*(keys(value, f'{prefix}.{key}' if prefix else key) for key, value in node.items()))


def switcher(path):
    lines = [line.strip() for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    return lines[1] if len(lines) > 1 and lines[0].startswith('# ') else None


def check_locales():
    en = keys(json.loads((LOCALES / 'en_US.json').read_text(encoding='utf-8')))
    zh = keys(json.loads((LOCALES / 'zh_CN.json').read_text(encoding='utf-8')))
    return [f'zh_CN.json missing key: {k}' for k in sorted(en - zh)] + \
           [f'zh_CN.json extra key: {k}' for k in sorted(zh - en)]


def check_pairs():
    errors = []
    for en in sorted(ROOT.rglob('*.md')):
        rel = en.relative_to(ROOT)
        if SKIP_DIRS & set(rel.parts) or en.name.endswith('.zh.md') or en.name in EXCLUDED:
            continue
        zh = en.with_name(en.stem + '.zh.md')
        if not zh.exists():
            errors.append(f'{rel}: missing {zh.name}')
            continue
        if switcher(en) != f'English | [中文]({zh.name})':
            errors.append(f'{rel}: line after H1 must be "English | [中文]({zh.name})"')
        if switcher(zh) != f'[English]({en.name}) | 中文':
            errors.append(f'{zh.relative_to(ROOT)}: line after H1 must be "[English]({en.name}) | 中文"')
    for zh in sorted(ROOT.rglob('*.zh.md')):
        rel = zh.relative_to(ROOT)
        if not SKIP_DIRS & set(rel.parts) and not zh.with_name(zh.name[:-6] + '.md').exists():
            errors.append(f'{rel}: no English counterpart')
    return errors


if __name__ == '__main__':
    errors = check_locales() + check_pairs()
    for error in errors:
        print(error)
    print('i18n: ok' if not errors else f'i18n: {len(errors)} problem(s)')
    sys.exit(1 if errors else 0)
