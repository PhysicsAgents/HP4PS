"""Your solution. The evaluator imports this package and calls the functions below;
their docstrings give the contract. See README.md."""


def pearson(c1, c2, block=None):
    """pearson(c1, c2) -> float: the correlation estimate between the photon-count arrays of NV1 and NV2
    (one entry per shot, as returned by env.run({'tau_s': ..., 'init': ...}, shots, rng))."""
    raise NotImplementedError


def resonant_tau(env, rng=None):
    """resonant_tau(env, rng=None) -> float: the XY8 pulse spacing tau (s) at which the two NVs are most
    strongly correlated by the applied signal. Measure only through env.run, drawing randomness from rng."""
    raise NotImplementedError
