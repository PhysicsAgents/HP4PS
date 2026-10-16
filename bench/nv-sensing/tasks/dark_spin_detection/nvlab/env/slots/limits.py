"""Limits slot: the settings a paper characterises. Outside them the environment raises instead of extrapolating."""

from __future__ import annotations

import numbers

from nvlab.env.core import Impl, implementation


@implementation('limits', 'ranges')
class Ranges(Impl):
    """defaults: filled in when the protocol omits a key; allowed: key -> list of values; ranges: key -> [lo, hi]
    (inclusive; lo_open: keys whose lower bound is exclusive); integers: keys that must be integers; reason: key -> why (cited in the error)."""

    def check(self, protocol):
        for k, v in (self.p.get('defaults') or {}).items():
            protocol.setdefault(k, v)
        why = self.p.get('reason') or {}
        for k in self.p.get('integers') or []:
            if k in protocol and not isinstance(protocol[k], numbers.Integral):
                raise ValueError(f'{k} = {protocol[k]!r} must be an integer: {why.get(k, "")}')
        for k, vals in (self.p.get('allowed') or {}).items():
            if k in protocol and not any(_eq(protocol[k], v) for v in vals):
                raise ValueError(f'{k} = {protocol[k]!r} not allowed ({vals}): {why.get(k, "")}')
        for k, (lo, hi) in (self.p.get('ranges') or {}).items():
            if k not in protocol:
                continue
            v = protocol[k]
            low_ok = v > lo if k in (self.p.get('lo_open') or []) else v >= lo - abs(lo) * 1e-9 - 1e-15
            if not (low_ok and v <= hi + abs(hi) * 1e-9 + 1e-15):
                raise ValueError(f'{k} = {v!r} outside [{lo}, {hi}]: {why.get(k, "")}')


def _eq(a, b):
    try:
        return abs(float(a) - float(b)) <= 1e-12 * max(1.0, abs(float(b)))
    except (TypeError, ValueError):
        return a == b
