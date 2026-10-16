"""Decoherence slot: the visibility V that multiplies the signal (per NV where there are several)."""

from __future__ import annotations

import numpy as np

from nvlab.env.core import Impl, implementation


@implementation('decoherence', 'constant')
class Constant(Impl):
    """Measured decoherence factors e^{-chi}, one per NV, at the operating point (Rovny 2022 Fig. S2A)."""

    def visibility(self, protocol, shots=None, rng=None):
        return list(self.p['factors'])


@implementation('decoherence', 'exp_T2')
class ExpT2(Impl):
    """e^{-t/T2} per NV during sensing and, for gate-based protocols, e^{-chi_e(2 te)} = e^{-4 te/T2} for the
    pair (Rovny 2025 Eq. S59). Returns the factor on the pair's correlation."""

    def visibility(self, protocol, shots=None, rng=None):
        T2 = self.p['T2_s']
        v = np.exp(-2 * protocol['t_s'] / T2)
        if protocol.get('protocol') in self.p.get('gate_protocols', []):
            v *= np.exp(-4 * self.p['te_s'] / T2)
        return v


@implementation('decoherence', 'stretched_exp')
class StretchedExp(Impl):
    """exp(-(t/T2)^p) (Zhou 2025 SI Eq. S12-S13, Table I)."""

    def visibility(self, protocol, shots=None, rng=None):
        return np.exp(-(protocol['t_s'] / self.p['T2_s']) ** self.p['p'])


@implementation('decoherence', 'echo_13c_envelope')
class Echo13C(Impl):
    """Maze 2008 Methods: F(tau) = exp(-(tau/T2)^4) (1 - [(a^2 - b^2)/a^2] sin^2(2 pi a tau) sin^2(2 pi b tau))."""

    def F(self, tau):
        a, b, T2 = self.p['a_Hz'], self.p['b_Hz'], self.p['T2_s']
        return np.exp(-(tau / T2) ** 4) * (1 - (a ** 2 - b ** 2) / a ** 2 * np.sin(2 * np.pi * a * tau) ** 2 * np.sin(2 * np.pi * b * tau) ** 2)

    def visibility(self, protocol, shots=None, rng=None):
        return self.F(protocol['tau_s'])


@implementation('decoherence', 'memory_depolarization')
class MemoryDepolarization(Impl):
    """Boss 2017 Eq. S41: the stored state survives n QND readouts with probability e^{-Gamma n}; otherwise the
    information is lost (V = 0 for that sample)."""

    def visibility(self, protocol, shots=None, rng=None):
        kept = rng.random(shots) < np.exp(-self.p['Gamma'] * protocol['n'])
        return kept.astype(float)


@implementation('decoherence', 'budget')
class Budget(Impl):
    """Xie 2021 Fig. 3D error budget: the fraction of shots that carry the phase,
    NV- preparation x survival x pol_e x pol_13C^2 x pol_14N^2 x T1 survival (measured for a 210 us sequence)."""

    def informative(self, duration_s):
        b = self.p
        if duration_s > b['T1_survival_max_s'] * (1 + 1e-9):
            raise ValueError(f'sequence {duration_s:.3e} s longer than the measured T1 survival point ({b["T1_survival_max_s"]} s)')
        return b['nv_prep'] * b['nv_survival'] * b['pol_e'] * b['pol_13C'] ** 2 * b['pol_14N'] ** 2 * b['T1_survival']
