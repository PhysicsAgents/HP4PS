"""Layered YAML configuration with per-value provenance.

A value may be written plainly (`D_Hz: 2.87e9`) or with its source
(`D_Hz: {value: 2.87e9, src: "Barry2020 Table 16"}`). `load` returns the plain
tree; `provenance` returns the source of every value that declared one.

A file may list `extends: [other.yaml, ...]`; those are merged first, then the
file itself on top. Paths in `extends` and in keys ending with `_file` are
resolved relative to the repository's `configs/` directory.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIGS = ROOT / 'configs'


def _is_sourced(node):
    return isinstance(node, dict) and 'value' in node and set(node) <= {'value', 'src', 'err', 'note'}


_FLOAT = re.compile(r'^[-+]?(\d+\.?\d*|\.\d+)[eE][-+]?\d+$')


def _num(v):
    """PyYAML reads 2.87e9 (no dot or sign in the exponent) as a string; fix that."""
    return float(v) if isinstance(v, str) and _FLOAT.match(v) else v


def _split(node, path, prov):
    if _is_sourced(node):
        if 'src' in node:
            prov[path] = node['src']
        return _split(node['value'], path, {})
    if isinstance(node, dict):
        return {k: _split(v, f'{path}.{k}' if path else k, prov) for k, v in node.items()}
    if isinstance(node, list):
        return [_split(v, f'{path}[{i}]', prov) for i, v in enumerate(node)]
    return _num(node)


def _merge(base, top):
    out = copy.deepcopy(base)
    for k, v in top.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict) and not _is_sourced(v):
            out[k] = _merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def resolve(name, root=CONFIGS):
    p = Path(name)
    if not p.suffix:
        p = p.with_suffix('.yaml')
    return p if p.is_absolute() else root / p


def _raw(path, root, seen):
    path = resolve(path, root)
    if path in seen:
        raise ValueError(f'circular extends: {path}')
    node = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    merged = {}
    for parent in node.pop('extends', []) or []:
        merged = _merge(merged, _raw(parent, root, seen | {path}))
    return _merge(merged, node)


def load_raw(path, root=CONFIGS):
    """Merged tree, sources still attached."""
    return _raw(path, root, frozenset())


def load(path, root=CONFIGS, overlay=None):
    """Plain merged tree. `overlay` (a dict or another file) is merged last."""
    raw = load_raw(path, root)
    if overlay is not None:
        raw = _merge(raw, overlay if isinstance(overlay, dict) else load_raw(overlay, root))
    return _split(raw, '', {})


def provenance(path, root=CONFIGS):
    prov = {}
    _split(load_raw(path, root), '', prov)
    return prov


def get(tree, dotted, default=...):
    node = tree
    for key in dotted.split('.'):
        if not isinstance(node, dict) or key not in node:
            if default is ...:
                raise KeyError(dotted)
            return default
        node = node[key]
    return node
