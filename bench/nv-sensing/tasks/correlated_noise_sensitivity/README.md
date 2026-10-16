# correlated_noise_sensitivity: Detecting spatially correlated magnetic noise

English | [中文](README.zh.md)

## System

Two NV centers sit in the same spatially correlated magnetic noise field. The spectral density of the noise field is flat near the detection frequency, with root-mean-square amplitude σB.

There are two available measurement protocols:
- **`entangled`:** prepare the two NVs in the Bell states |Φ⟩ and |Ψ⟩ (half of the shots each), and compare the difference signal of the two.
- **`non-interacting`:** the two NVs are not entangled; directly compute the correlation between their readings.

There are two available readout methods:
- **`conventional`:** fast readout, but large readout noise;
- **`scc`:** small readout noise, but each readout takes a long time.

Coherence time, entangling gate duration and readout parameters are given in the configuration.

## Quantity to measure

The weakest correlated field σB that can be detected within total experiment time T. The criterion is SNR = 1.

## Performance metric

The minimum detectable σB at the given T. Equivalently: with σB fixed, the higher the SNR the better.

## Interface

- Environment: `env = nvlab.env.load('correlated_noise_sensitivity')`
- Measurement: `env.run({'protocol': ..., 'readout': ..., 't_s': ...}, shots=..., repeats=..., rng=...)` returns the estimator. Its SNR is the mean over repeats divided by the standard deviation.
- Time per shot: `env.shot_time({...})`
- Requirement: shots × time per shot ≤ T.

Implement `design(env, T_s) -> dict(protocol, readout, t_s, shots)` in `solutions/correlated_noise_sensitivity/__init__.py`.

## Scoring

T takes 10³, 10⁴, 10⁶ s. The evaluator sets σB to the reference level and checks two items:
1. whether the SNR of your protocol reaches 1;
2. the SNR gain relative to "non-entangled + conventional readout".

It then runs again on hidden samples with different coherence time and gate duration.

## Runtime environment

- Python 3.12; dependencies are listed in `requirements.txt`.
- Run from the repository root with `PYTHONPATH=.`; load the environment with `nvlab.env.load('correlated_noise_sensitivity')`.
- Write your code in `solutions/correlated_noise_sensitivity/__init__.py`. Evaluation uses the original `nvlab/` and the evaluator's own samples; your modifications to `nvlab/` and `configs/` do not count toward scoring; the evaluator also runs your solution on hidden samples with different parameters.
