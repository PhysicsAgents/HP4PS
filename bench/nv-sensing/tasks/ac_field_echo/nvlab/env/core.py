"""One environment for every paper sample: fixed slots, implementations chosen by configuration.

A paper's configuration (configs/papers/<paper>.yaml) has an `env` block with one entry per slot:

    env:
      signal:   {impl: random_phase_ac, f0_Hz: ..., ...}          # one implementation and its parameters
      readout:  {select_by: readout, options: {conventional: {impl: sigma_R, ...}, scc: {...}}}
      decoherence: {select_by: [sensor, target], options: {NV1-DS1: {impl: stretched_exp, ...}, ...}}

A slot that is absent is disabled. `export: {key: value}` in a slot gives the value an exported (agent-side)
copy uses instead, for quantities the evaluator keeps (e.g. the sensed signal). `select_by` names the protocol key(s) whose value picks one of the
`options` (several keys are joined with '-'). The level of detail of a paper is set the same way: the
`statistics` slot picks how a measurement is executed (exact probability, shot by shot, or the large-N
Gaussian limit) and the other slots provide the physics at the level the paper gives it.

Implementations live in nvlab/env/slots/*.py and register themselves with @implementation(slot, name).
"""

from __future__ import annotations

import copy

SLOTS = ('system', 'init', 'signal', 'accumulation', 'decoherence', 'readout', 'timing', 'limits', 'statistics', 'analytic')
_REGISTRY: dict[tuple[str, str], type] = {}


def implementation(slot, name):
    if slot not in SLOTS:
        raise ValueError(f'unknown slot {slot}')

    def deco(cls):
        _REGISTRY[(slot, name)] = cls
        cls.slot, cls.name = slot, name
        return cls
    return deco


class Impl:
    """Base of slot implementations: `self.p` holds the configured parameters, `self.env` the environment."""

    def __init__(self, params, env):
        self.p = params
        self.env = env


def _build(slot, node, env):
    node = dict(node)
    node.pop('export', None)                 # values that replace the sample's in the agent's copy (scripts/export_paper.py)
    name = node.pop('impl')
    try:
        cls = _REGISTRY[(slot, name)]
    except KeyError:
        raise ValueError(f'no implementation {name!r} for slot {slot!r}') from None
    return cls(node, env)


class _Options:
    def __init__(self, slot, node, env):
        keys = node['select_by']
        self.keys = [keys] if isinstance(keys, str) else list(keys)
        self.options = {k: _build(slot, v, env) for k, v in node['options'].items()}

    def pick(self, protocol):
        missing = [k for k in self.keys if k not in protocol]
        if missing:
            raise ValueError(f'protocol must give {missing} (one of {sorted(self.options)})')
        key = '-'.join(str(protocol[k]) for k in self.keys)
        if key not in self.options:
            raise ValueError(f'{"-".join(self.keys)} = {key!r} is not one of {sorted(self.options)}')
        return self.options[key]


class Env:
    def __init__(self, params, paper=''):
        self.paper = paper
        self.params = params
        self._slots = {}
        for slot in SLOTS:
            node = params.get('env', {}).get(slot)
            if node is None:
                continue
            self._slots[slot] = _Options(slot, node, self) if 'options' in node else _build(slot, node, self)

    def has(self, slot):
        return slot in self._slots

    def slot(self, slot, protocol=None):
        """The implementation used in `slot` for this protocol (None if the slot is disabled)."""
        s = self._slots.get(slot)
        if isinstance(s, _Options):
            return s.pick(protocol or {})
        return s

    def options(self, slot):
        s = self._slots.get(slot)
        return sorted(s.options) if isinstance(s, _Options) else []

    # -- the interface used by solutions and evaluators ------------------------------------------
    def check(self, protocol):
        if self.has('limits'):
            self.slot('limits', protocol).check(protocol)

    def shot_time(self, protocol):
        """Duration of one repetition of the protocol (s), from the timing slot."""
        return self.slot('timing', protocol).shot_time(protocol)

    def run(self, protocol=None, **kw):
        """Execute a measurement with the statistics slot; see the implementation for the result."""
        protocol = dict(protocol or {})
        self.check(protocol)
        return self.slot('statistics', protocol).run(protocol, **kw)

    def predict(self, name, *args, **kw):
        """A closed-form result of the paper enabled in the analytic slot (e.g. a sensitivity formula)."""
        return self.slot('analytic').call(name, *args, **kw)

    def set_signal(self, **values):
        """Evaluator: set the sensed signal (amplitude, frequency, ...). Not part of a solution."""
        sig = self._slots['signal']
        for s in (sig.options.values() if isinstance(sig, _Options) else [sig]):
            s.set(**values)

    def copy(self):
        return copy.deepcopy(self)
