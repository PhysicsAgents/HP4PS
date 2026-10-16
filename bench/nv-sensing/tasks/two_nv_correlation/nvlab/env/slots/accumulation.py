"""Accumulation slot: the phase (or its moment) the sensor acquires from the signal during sensing.

Shot-by-shot implementations return phi; the statistics slot projects with
p = (1 + V cos(phi - theta)) / 2, V from the decoherence slot and theta from the init slot.
Moment implementations return the mean ideal signal for the large-N Gaussian statistics.
"""

from __future__ import annotations

import numpy as np
import scipy.constants as K

from nvlab.env.core import Impl, implementation

HBAR = K.hbar
MU_B = K.physical_constants['Bohr magneton'][0]


def W_cp(f, tau, n):
    """Filter of a CP-type sequence: sinc(pi f n tau) [1 - sec(pi f tau)] (Degen RMP Eq. 66; Rovny 2022 Eq. S18)."""
    return np.sinc(f * n * tau) * (1 - 1 / np.cos(np.pi * f * tau))


@implementation('accumulation', 'filter_function')
class FilterFunction(Impl):
    """phi = (a/2) W(f, tau) n tau cos(alpha) for a random-phase AC signal under n pulses spaced tau, so that
    <cos 2 phi> = <J0(a W t)> as in Rovny 2022 Eq. (S18); both NVs see the same phase (Eq. S16-S18)."""

    def phase(self, s, protocol):
        n, tau = self.p['n_pulses'], protocol['tau_s']
        return 0.5 * s['a'] * W_cp(s['f'], tau, n) * n * tau * np.cos(s['alpha'])


@implementation('accumulation', 'lockin')
class Lockin(Impl):
    """The lock-in phase phi_k itself (Boss 2017 Eq. 1); the projection gives p_k = (1 - sin phi_k)/2 (Eq. 2)."""

    def phase(self, s, protocol):
        return s['phi']


@implementation('accumulation', 'ramsey')
class Ramsey(Impl):
    """phi = w tau for one Ramsey sequence, tau in us and w in rad/us (Santagati 2019 Eq. 4, T2* -> inf)."""

    def phase(self, w, protocol):
        return w * protocol['tau_us']


@implementation('accumulation', 'echo_phase')
class EchoPhase(Impl):
    """Maze 2008 Methods Eq. 2: dphi = (4 g muB B_AC / (2 pi nu hbar)) sin^2(pi nu tau / 2) cos(pi nu tau + phi_AC),
    with the AC phase of shot k phi_AC + 2 pi nu k period (all shots equal when period nu is an integer)."""

    def phase(self, sig, protocol, shots):
        nu, B, g = sig['nu_Hz'], sig['B_AC_T'], self.p['g']
        lo, hi = self.p['nu_range_Hz']
        if not lo <= nu <= hi:
            raise ValueError(f'nu = {nu} Hz outside the characterised range {lo}-{hi} Hz')
        tau, period = protocol['tau_s'], protocol['period_s']
        k = np.arange(shots) if abs(nu * period - round(nu * period)) > 1e-12 else np.zeros(1)
        phi_ac = protocol['phi_ac'] + 2 * np.pi * nu * period * k
        return 4 * g * MU_B * B / (2 * np.pi * nu * HBAR) * np.sin(np.pi * nu * tau / 2) ** 2 * np.cos(np.pi * nu * tau + phi_ac)


@implementation('accumulation', 'correlated_moment')
class CorrelatedMoment(Impl):
    """<sin phi_Ca sin phi_Cb> = e^{-2 chi_C} sinh(2 chi_C) for Gaussian correlated phases (Rovny 2022 SI Sec. V;
    Rovny 2025 SI Eq. S58), chi_C from the signal slot."""

    def moment(self, protocol):
        chi = self.env.slot('signal', protocol).chi(protocol['t_s'])
        return np.exp(-2 * chi) * np.sinh(2 * chi)


@implementation('accumulation', 'deer_slope')
class DeerSlope(Impl):
    """DEER slope detection (Zhou 2025 SI Eq. S12): a pi-pulse shift delta_tp moves the signal by
    (1/2) nu delta_tp = pi A_eff t_DEER delta_tp before decoherence. The shift is the signal's, or one the
    protocol applies itself (protocol['delta_tp_s'], e.g. to calibrate the slope)."""

    def moment(self, protocol):
        d = protocol.get('delta_tp_s', self.env.slot('signal', protocol).p['delta_tp_s'])
        return np.pi * self.p['A_eff_Hz'] * protocol['t_s'] * d
