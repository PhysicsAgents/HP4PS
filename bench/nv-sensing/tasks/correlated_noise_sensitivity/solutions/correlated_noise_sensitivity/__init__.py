"""Your solution. The evaluator imports this package and calls the functions below;
their docstrings give the contract. See README.md."""


def design(env, T_s):
    """design(env, T_s) -> dict(protocol, readout, t_s, shots): the measurement to run within the total
    experiment time T_s (s) so that the weakest correlated field is detected (SNR = mean / std of the
    estimate returned by env.run(design, shots=...)). shots * env.shot_time(design) must not exceed T_s."""
    raise NotImplementedError
