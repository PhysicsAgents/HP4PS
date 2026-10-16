# ac_field_echo: Measuring an AC magnetic field with a single NV

English | [中文](README.zh.md)

## System

A single NV electron spin in bulk diamond uses spin echo to measure an AC magnetic field B_AC·cos(2πνt + φ_AC) of frequency ν (1–10 kHz).

Procedure for each shot:
1. polarization;
2. π/2 – τ/2 – π – τ/2 – π/2;
3. readout.

The echo envelope is affected by the ¹³C nuclear spin bath. Readout photon counts are very low, and single-shot noise is large. Polarization and readout durations, echo envelope, photon counts and other parameters are given in the configuration.

## Quantity to measure

The AC magnetic field amplitude B_AC.

## Performance metric

The minimum detectable field after averaging for T seconds, δB_min = σ(S̄)/|dS̄/dB_AC|, in T. Another metric is its scaling with averaging time.

## Interface

- Environment: `env = nvlab.env.load('ac_field_echo')`
- Measurement: `env.run(d, T_s=T, repeats=..., rng=...)` returns the signal after averaging for T seconds. d is the dict returned by `design` below.
- ν and B_AC are set by the evaluator.
- Constraints:
  - 0 < τ ≤ 1 ms;
  - period per shot ≥ polarization + τ + readout;
  - number of shots N = floor(T / period).

Implement `design(env, nu_Hz, T_s) -> dict(tau_s, period_s, phi_ac, theta)` in `solutions/ac_field_echo/__init__.py`.

## Scoring

The evaluator measures δB_min at several frequencies in 1.4–7.4 kHz with T = 1 s, and measures the averaging-time scaling over the range 0.3–155 s, and compares with the reference level. It then runs again on hidden samples with different sample parameters and frequencies.

## Runtime environment

- Python 3.12; dependencies are listed in `requirements.txt`.
- Run from the repository root with `PYTHONPATH=.`; load the environment with `nvlab.env.load('ac_field_echo')`.
- Write your code in `solutions/ac_field_echo/__init__.py`. Evaluation uses the original `nvlab/` and the evaluator's own samples; your modifications to `nvlab/` and `configs/` do not count toward scoring; the evaluator also runs your solution on hidden samples with different parameters.
