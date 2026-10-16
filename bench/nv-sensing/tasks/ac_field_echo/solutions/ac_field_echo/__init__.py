"""Your solution. The evaluator imports this package and calls the functions below;
their docstrings give the contract. See README.md."""


def design(env, nu_Hz, T_s):
    """design(env, nu_Hz, T_s) -> dict(tau_s, period_s, phi_ac, theta)
    
    Measurement design for sensing an AC field of frequency nu_Hz with total averaging time T_s:
    echo time tau_s, repetition period period_s (>= 1 us + tau_s + 3 us), AC phase phi_ac at the
    start of the first shot (radians), and phase theta of the last pi/2 pulse (radians)."""
    raise NotImplementedError
