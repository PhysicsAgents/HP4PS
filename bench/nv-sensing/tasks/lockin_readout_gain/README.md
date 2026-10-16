# lockin_readout_gain: Readout gain in continuous-sampling measurement

English | [中文](README.zh.md)

## System

One NV center samples an AC signal synchronously (lock-in), and each sample point outputs one photon count.

Within each sample point:
1. the spin accumulates phase;
2. the phase is stored in a nuclear-spin memory;
3. this memory is read out non-destructively n times in repetition.

The more readouts n, the more photons are collected, but each readout has some probability of depolarizing the memory, and the information is lost with it. One record has N sample points. Optical contrast, photons per readout and depolarization rate are given in the configuration.

## Quantity to measure

The signal peak in the spectrum of the record.

## Performance metric

Spectral SNR: the power of the frequency component at the signal frequency, |Σ y_k e^{−2πikj/N}|², divided by the standard deviation of the noise floor.

## Interface

- Environment: `env = nvlab.env.load('lockin_readout_gain')`
- Measurement: `env.run({'n': n}, shots=N, rng=...)` returns the photon counts of one N-point record.
- n is an integer in the range 1–2000.

Implement `choose_n(env) -> int` in `solutions/lockin_readout_gain/__init__.py`.

## Scoring

The evaluator takes several recordings at the n you give, computes the average spectral SNR, and compares it with the reference level. It then runs again on hidden samples with different contrast, depolarization rate and signal amplitude.

## Runtime environment

- Python 3.12; dependencies are listed in `requirements.txt`.
- Run from the repository root with `PYTHONPATH=.`; load the environment with `nvlab.env.load('lockin_readout_gain')`.
- Write your code in `solutions/lockin_readout_gain/__init__.py`. Evaluation uses the original `nvlab/` and the evaluator's own samples; your modifications to `nvlab/` and `configs/` do not count toward scoring; the evaluator also runs your solution on hidden samples with different parameters.
