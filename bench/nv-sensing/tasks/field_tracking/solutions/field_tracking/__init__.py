"""Your solution. The evaluator imports this package and calls the functions below;
their docstrings give the contract. See README.md."""


def track(env):
    """track(env) -> numpy array with one estimate per epoch (env.slot('statistics').p['max_epochs'] epochs).
    
    One tracking run: for each epoch choose a Ramsey time tau (us), call env.run({'tau_us': tau}) exactly once
    (it returns the reported outcome 0 or 1), and record the estimate of the current angular frequency w (rad/us)
    after the update. Public prior knowledge: the signal's w_amp and nu
    (env.slot('signal').p) and the readout fids (env.slot('readout').p['fids']); w0 and the phase are unknown."""
    raise NotImplementedError
