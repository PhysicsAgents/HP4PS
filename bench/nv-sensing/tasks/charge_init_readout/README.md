# charge_init_readout: Charge initialization and spin readout

English | [中文](README.zh.md)

## System

A single NV center; each measurement consists of three steps.

1. **Charge initialization, one of two:**
   - **Real-time initialization (`rti`):** repeat "green pump + red probe" until the detected photon count reaches the threshold ν;
   - **Steady-state initialization (`ssi`):** a fixed period of green light.
2. **Spin operation:** duration τO.
3. **SCC readout:** first perform spin-to-charge conversion, then probe the charge state with red light and classify by a photon-count threshold.

Charge dynamics under red light, conversion efficiency and other parameters are given in the configuration. The red-light power limit is 200 µW.

## Quantity to measure

The spin state.

## Performance metric

Readout efficiency ξ = SNR/√(τI + τO + τR), and the AC magnetic field sensitivity determined by it, in T/√Hz.

## What you control

| Key | Meaning |
|---|---|
| `init` | `'rti'` or `'ssi'` |
| `P_probe_uW`, `tau_probe_s`, `nu` | Probe power, duration and threshold for real-time initialization |
| `P_read_uW`, `tau_read_s`, `threshold` | Power, duration and threshold for charge readout |

## Interface

- Environment: `env = nvlab.env.load('charge_init_readout')`
- Shot-by-shot measurement: `env.run(dict(d, spin=0 or 1), shots=..., rng=...)`, returns the classification result of each shot and the total time.
- Model: `env.slot('init', d).initialization(d)`, `env.slot('readout', d).probabilities(F, d)`, `env.shot_time(dict(d, tau_O_s=...))`.

Implement `protocol(env, tau_O_s) -> dict` in `solutions/charge_init_readout/__init__.py`.

## Scoring

The evaluator sets τO equal to the coherence time, computes the sensitivity of your protocol, executes it shot by shot to check the SNR, and compares with the reference level. It then runs again on hidden samples with different coherence time, brightness and background.

## Runtime environment

- Python 3.12; dependencies are listed in `requirements.txt`.
- Run from the repository root with `PYTHONPATH=.`; load the environment with `nvlab.env.load('charge_init_readout')`.
- Write your code in `solutions/charge_init_readout/__init__.py`. Evaluation uses the original `nvlab/` and the evaluator's own samples; your modifications to `nvlab/` and `configs/` do not count toward scoring; the evaluator also runs your solution on hidden samples with different parameters.
