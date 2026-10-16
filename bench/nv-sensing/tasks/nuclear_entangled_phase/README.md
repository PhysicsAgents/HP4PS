# nuclear_entangled_phase: Measuring a phase with two nuclear spins

English | [中文](README.zh.md)

## System

A single NV center forms a three-qubit register under a strong magnetic field:
- the electron spin, using two levels;
- a ¹⁴N nuclear spin, using two levels;
- a strongly coupled ¹³C nuclear spin.

Available operations:
- **Microwave (MW) pulses:** act on the electron; multiple frequencies can be sent simultaneously, each segment specifying real and imaginary amplitudes. The electron transition frequency differs for different nuclear states.
- **Radio-frequency (RF) pulses:** act on ¹⁴N or ¹³C when the electron is in ms = 0.
- **Phase gates and waits.**
- **Readout:** only ¹³C can be read.

The control has quasi-static detuning and microwave amplitude fluctuations. State preparation, relaxation and readout are all imperfect; specific parameters are given in the configuration.

## Quantity to measure

A phase φ acting simultaneously on ¹⁴N and ¹³C. The evaluator inserts Uz(φ) between the two program segments you give.

## Performance metric

The gain of the Fisher information of the phase measurement relative to the standard quantum limit, in dB.

The evaluator scans the ¹³C readout fringe with 16 values of φ, fits P = c + (Vis/2)·sin(2φ + p), and takes the gain as 10·log10(2·Vis²). The fringe must be a single 2φ harmonic.

## Interface

- Environment: `env = nvlab.env.load('nuclear_entangled_phase')`
- Run a program: `env.run({'program': [...]})`, returns the probability of reading ¹³C as |−½⟩.
- A program consists of three kinds of operations:
  - `nvlab.env.Pulse(piece_s, mw=[{'offset_Hz', 're', 'im'}, ...], rf={'Nx'|'Ny'|'Cx'|'Cy': [...]})`
  - `nvlab.env.Uz(phi, qubits)`
  - `nvlab.env.Wait(t_s)`
- Parameters can be read via `env.slot('system').p` and similar.
- Constraint: total length of the whole program does not exceed 210 µs.

Implement `interferometer(env) -> (before, after)` in `solutions/nuclear_entangled_phase/__init__.py`.

## Scoring

The gain is compared with the reference level, and the run is repeated on hidden samples with different parameters.

## Runtime environment

- Python 3.12; dependencies are listed in `requirements.txt`.
- Run from the repository root with `PYTHONPATH=.`; load the environment with `nvlab.env.load('nuclear_entangled_phase')`.
- Write your code in `solutions/nuclear_entangled_phase/__init__.py`. Evaluation uses the original `nvlab/` and the evaluator's own samples; your modifications to `nvlab/` and `configs/` do not count toward scoring; the evaluator also runs your solution on hidden samples with different parameters.
