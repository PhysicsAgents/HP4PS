"""Your solution. The evaluator imports this package and calls the functions below;
their docstrings give the contract. See README.md."""


def choose_n(env):
    """choose_n(env) -> int: number of repetitive QND readouts n (1..2000) per sample.
    
    The evaluator records N-sample traces with env.run({'n': n}, shots=N) and scores the spectral SNR: power in the signal bin over the standard deviation of the noise floor."""
    raise NotImplementedError
