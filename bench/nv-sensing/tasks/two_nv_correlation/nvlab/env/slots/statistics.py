"""Statistics slot: how a measurement is executed, i.e. the level of detail.

- exact_probability: probability of reporting 1 for a program, averaged over quasi-static noise nodes (Xie 2021).
- per_shot: shot by shot, p = (1 + V cos(phi - theta))/2 per NV, then the readout samples the record.
- epoch: one adaptive shot at a time with a time-dependent signal (Santagati 2019).
- charge_spin: charge initialization, spin preparation and SCC readout shot by shot (Hopper 2020).
- gaussian: the large-N limit, estimate = mean + sd z / sqrt(N) (Rovny 2025, Zhou 2025, Maze 2008).
"""

from __future__ import annotations

import numpy as np

from nvlab.env.core import Impl, implementation
from nvlab.env.slots.system import duration


def _rng(rng):
    return np.random.default_rng() if rng is None else rng


@implementation('statistics', 'exact_probability')
class ExactProbability(Impl):
    """protocol {'program': [Pulse | Uz | Wait, ...]} -> probability to report 1 (Xie 2021: 13C |-1/2>).
    Gauss-Hermite nodes over the quasi-static detuning (sigma_mag_Hz) and MW amplitude error (sigma_amp)."""

    def __init__(self, params, env):
        super().__init__(params, env)
        self._cache = {}

    def nodes(self, n):
        sys_ = self.env.slot('system')
        x, w = np.polynomial.hermite_e.hermegauss(n)
        w = w / w.sum()
        sm, sa = sys_.p['sigma_mag_Hz'], sys_.p['sigma_amp']
        return [(xi * sm, 1 + xj * sa, wi * wj) for xi, wi in zip(x, w) for xj, wj in zip(x, w)]

    def run(self, protocol, nodes=None):
        program = protocol['program']
        sys_ = self.env.slot('system', protocol)
        q = self.env.slot('decoherence', protocol).informative(sum(duration(op) for op in program))
        rho0 = sys_.initial_state()
        p = 0.0
        for delta, alpha, w in self.nodes(nodes or self.p['nodes']):
            U = np.eye(sys_.dim, dtype=complex)
            for op in program:
                U = sys_.unitary(op, delta, alpha, self._cache) @ U
            p += w * sys_.p_read(U @ rho0 @ U.conj().T)
        return q * self.env.slot('readout', protocol).probability(p) + (1 - q) * 0.5


@implementation('statistics', 'per_shot')
class PerShot(Impl):
    """run(protocol, shots, rng) -> recorded data per NV (a list if there are several NVs)."""

    def run(self, protocol, shots, rng=None):
        rng = _rng(rng)
        sig = self.env.slot('signal', protocol).sample(rng, shots, protocol)
        phi = self.env.slot('accumulation', protocol).phase(sig, protocol)
        V = self.env.slot('decoherence', protocol).visibility(protocol, shots, rng)
        thetas = self.env.slot('init', protocol).theta(protocol)
        readout = self.env.slot('readout', protocol)
        out = []
        for i, th in enumerate(thetas):
            v = V[i] if isinstance(V, list) else V
            m = rng.random(shots) < 0.5 * (1 + v * np.cos(phi - th))
            out.append(readout.sample(m, protocol, rng, nv=i))
        return out if len(out) > 1 else out[0]


@implementation('statistics', 'epoch')
class Epoch(Impl):
    """run({'tau_us': tau}) -> reported outcome (0 or 1) of one Ramsey sequence at the signal's current value."""

    def run(self, protocol, rng=None):
        sig = self.env.slot('signal', protocol)
        if sig.epoch >= self.p['max_epochs']:
            raise RuntimeError(f'only {self.p["max_epochs"]} epochs per run')
        tau = float(protocol['tau_us'])
        if not np.isfinite(tau) or tau < 0:
            raise ValueError('tau must be a finite non-negative time in us')
        rng = _rng(rng)
        phi = self.env.slot('accumulation', protocol).phase(sig.step(), protocol)
        th = self.env.slot('init', protocol).theta(protocol)[0]
        m = rng.random() < 0.5 * (1 + np.cos(phi - th))
        return int(self.env.slot('readout', protocol).sample(np.array(m), protocol, rng))


@implementation('statistics', 'charge_spin')
class ChargeSpin(Impl):
    """run(protocol, shots, rng) with protocol['spin'] in {0, 1} -> (outcomes: count >= threshold, time in s
    excluding the operation time)."""

    def run(self, protocol, shots, rng=None):
        rng = _rng(rng)
        if protocol.get('spin') not in (0, 1):
            raise ValueError('spin must be 0 or 1')
        init = self.env.slot('init', protocol)
        t_init = init.sample_time(protocol, shots, rng)
        nv_minus = rng.random(shots) < init.initialization(protocol)['F']
        m = np.full(shots, protocol['spin'])
        out = self.env.slot('readout', protocol).sample(m, protocol, rng, nv_minus)
        return out, t_init + shots * protocol['tau_read_s']


@implementation('statistics', 'gaussian')
class Gaussian(Impl):
    """run(protocol, shots=None, T_s=None, repeats=1, rng=None) -> `repeats` estimates of N shots, N = shots or
    floor(T_s / shot_time). The mean is the accumulation moment times V (or, for projective sequences, the mean
    of (1 + V cos(phi - theta))/2 over the shots), mapped by the readout; the noise is its sd / sqrt(N)."""

    def shots(self, protocol, shots=None, T_s=None):
        N = int(shots) if shots is not None else int(T_s // self.env.shot_time(protocol) + 1e-9)
        if N < 1:
            raise ValueError('no shot fits in the total time')
        return N

    def mean(self, protocol, N):
        acc = self.env.slot('accumulation', protocol)
        V = self.env.slot('decoherence', protocol).visibility(protocol)
        if hasattr(acc, 'moment'):
            ideal = acc.moment(protocol) * V
        else:
            phi = acc.phase(self.env.slot('signal', protocol).p, protocol, N)
            th = self.env.slot('init', protocol).theta(protocol)[0]
            ideal = float(np.mean(0.5 * (1 + V * np.cos(phi - th))))
        return self.env.slot('readout', protocol).transform(ideal, protocol)

    def run(self, protocol, shots=None, T_s=None, repeats=1, rng=None):
        if self.env.has('timing'):
            self.env.shot_time(protocol)                   # timing checks (e.g. the period must hold the sequence)
        N = self.shots(protocol, shots, T_s)
        mean, sd = self.mean(protocol, N)
        return mean + sd * _rng(rng).standard_normal(repeats) / np.sqrt(N)
