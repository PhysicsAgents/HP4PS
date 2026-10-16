# dark_spin_detection: Detecting a single dark spin

English | [中文](README.zh.md)

## System

A pair of mutually coupled NV centers has dark spins nearby (targets `DS1`, `DS2+`), which are detected with the DEER slope method: within DEER time t_DEER, the position of the target-spin π pulse is shifted by δt_p, and the signal changes linearly with it.

There are two available sensors:
- **`NV1`:** a single NV;
- **`psi2`:** an entangled state of two NVs.

Each "sensor–target" combination has its own effective coupling, coherence decay, readout contrast, photon count and extra overhead per repetition; details are given in the configuration.

## Quantity to measure

The π-pulse shift δt_p.

## Performance metric

Sensitivity: the minimum δt_p giving SNR = 1 within a total time of 1 s; smaller is better. Another metric is sensor choice: for each target, choose the sensor with the better sensitivity.

## Interface

- Environment: `env = nvlab.env.load('dark_spin_detection')`
- Measurement: `env.run({'sensor': ..., 'target': ..., 't_s': t_DEER, 'delta_tp_s': the shift you apply}, T_s=1.0, repeats=..., rng=...)`, returns the averaged slope signal, in units of single-shot readout noise.
- Constraint: t_DEER is within (0, 20 µs].

Implement two functions in `solutions/dark_spin_detection/__init__.py`:
- `best_t_DEER(env, sensor, target) -> float`
- `choose_sensor(env, target) -> str`

## Scoring

The evaluator measures the sensitivity of both sensors at the t_DEER you give, and checks two items:
1. whether the ratio of the two and the sensor choice reach the reference level;
2. on hidden samples with different parameters, whether the t_DEER and sensor you choose are still optimal.

## Runtime environment

- Python 3.12; dependencies are listed in `requirements.txt`.
- Run from the repository root with `PYTHONPATH=.`; load the environment with `nvlab.env.load('dark_spin_detection')`.
- Write your code in `solutions/dark_spin_detection/__init__.py`. Evaluation uses the original `nvlab/` and the evaluator's own samples; your modifications to `nvlab/` and `configs/` do not count toward scoring; the evaluator also runs your solution on hidden samples with different parameters.
