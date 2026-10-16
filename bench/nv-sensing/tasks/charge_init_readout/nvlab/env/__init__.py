"""The NV sensing environment: one set of slots, each paper selected by its configuration.

    from nvlab import env
    e = env.load('rovny2022')               # configs/papers/rovny2022.yaml
    e.run({'tau_s': 250e-9, 'init': 'parallel'}, shots=10**6)
"""

from nvlab import config
from nvlab.env.core import SLOTS, Env, Impl, implementation  # noqa: F401
from nvlab.env.slots import (accumulation, analytic, decoherence, init, limits, readout, signal,  # noqa: F401
                             statistics, system, timing)
from nvlab.env.slots.system import Pulse, Uz, Wait  # noqa: F401  (program operations of register_e_N_C)


def load(paper, overlay=None):
    """Environment of a paper sample; `overlay` (dict) changes configuration values (hidden samples)."""
    return Env(config.load(f'papers/{paper}', overlay=overlay), paper)
