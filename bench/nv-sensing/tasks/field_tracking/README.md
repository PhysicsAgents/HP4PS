# field_tracking: Tracking a time-varying magnetic field

English | [中文](README.zh.md)

## System

A single NV performs Ramsey measurements under ideal conditions:
- decoherence is not included;
- experimental overhead is not included.

Each epoch performs one single-shot Ramsey measurement: you give the phase accumulation time τ (µs) and get outcome 0 or 1.

The angular frequency corresponding to the magnetic field varies with epoch index k: ω(k) = ω0 + w·cos(νk + φ).
- **Known:** w and ν, readable from `env.slot('signal').p`; they are a public prior.
- **Unknown:** ω0 and φ, different in every run, and can only be inferred from the measurement outcomes.

The parameters of the readout model are in `env.slot('readout').p`. Each run has a fixed number of epochs.

## Quantity to measure

ω at each epoch.

## Performance metric

Relative tracking error. First, for each epoch take the median over runs of "(estimate − true value)² / ω0²", then take the median over the later epochs, and finally take the square root.

## Interface

- Environment: `env = nvlab.env.load('field_tracking')`
- One measurement: `env.run({'tau_us': tau})`

Implement `track(env)` in `solutions/field_tracking/__init__.py`:
- call `env.run` exactly once per epoch;
- record the estimate of ω after this epoch's update;
- return one estimate per epoch.

You may use any algorithm and library, but all code and dependencies must be placed inside the `solutions/field_tracking/` directory.

## Scoring

The evaluator runs 100 times for each of several cases with ν from slow to fast, and compares with the reference level. During evaluation the magnetic field is held in a separate process; a trajectory written without making measurements will fail. It then runs again on hidden samples with a different ω0 range and readout model.

## Runtime environment

- Python 3.12; dependencies are listed in `requirements.txt`.
- Run from the repository root with `PYTHONPATH=.`; load the environment with `nvlab.env.load('field_tracking')`.
- Write your code in `solutions/field_tracking/__init__.py`. Evaluation uses the original `nvlab/` and the evaluator's own samples; your modifications to `nvlab/` and `configs/` do not count toward scoring; the evaluator also runs your solution on hidden samples with different parameters.
