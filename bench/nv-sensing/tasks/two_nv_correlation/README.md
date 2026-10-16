# two_nv_correlation: Shot-by-shot correlation of two NVs

English | [中文](README.zh.md)

## System

Two shallow NV centers that can be read out separately.

- They jointly sense an applied AC magnetic field with random phase.
- Both sense with the XY8 dynamical decoupling sequence; the sequence can use parallel or antiparallel initialization.
- Readout is by spin-to-charge conversion (SCC), recording the photon count of each shot.

Current operating point:
- XY8-4, 32 pulses in total;
- ionization time 200 ns;
- pulse spacing τ between 200–300 ns.

## Quantity to measure

The Pearson correlation coefficient r between the shot-by-shot readings of the two NVs, and the pulse spacing that makes the correlation strongest.

## Performance metric

The magnitude and sign of the correlation coefficient r. With parallel initialization r is positive; with antiparallel it is negative.

## Interface

- Environment: `env = nvlab.env.load('two_nv_correlation')`
- Measurement: `env.run({'tau_s': tau, 'init': 'parallel' or 'antiparallel'}, shots=..., rng=...)`, returns the shot-by-shot photon counts of each of the two NVs.

Implement two functions in `solutions/two_nv_correlation/__init__.py`:
- `resonant_tau(env, rng=None) -> float`
- `pearson(c1, c2) -> float`

## Scoring

At the τ you give, the evaluator measures 20 million shots each for parallel and antiparallel, computes the correlation with your `pearson`, and compares with the reference level. It then runs again on hidden samples with a different signal frequency.

## Runtime environment

- Python 3.12; dependencies are listed in `requirements.txt`.
- Run from the repository root with `PYTHONPATH=.`; load the environment with `nvlab.env.load('two_nv_correlation')`.
- Write your code in `solutions/two_nv_correlation/__init__.py`. Evaluation uses the original `nvlab/` and the evaluator's own samples; your modifications to `nvlab/` and `configs/` do not count toward scoring; the evaluator also runs your solution on hidden samples with different parameters.
