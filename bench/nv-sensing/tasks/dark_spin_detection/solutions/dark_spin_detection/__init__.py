"""Your solution. The evaluator imports this package and calls the functions below;
their docstrings give the contract. See README.md."""


def best_t_DEER(env, sensor, target, rng=None):
    """best_t_DEER(env, sensor, target) -> float
    
    DEER sensing time t_DEER (s) that gives the best sensitivity of `sensor` ('NV1' or 'psi2') for
    `target` ('DS1' or 'DS2+'), within the allowed range (0, 20 us]."""
    raise NotImplementedError


def choose_sensor(env, target, rng=None):
    """choose_sensor(env, target) -> str
    
    The sensor ('NV1' or 'psi2') with the better optimal sensitivity for `target`."""
    raise NotImplementedError
