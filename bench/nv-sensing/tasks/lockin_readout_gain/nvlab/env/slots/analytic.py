"""Analytic slot: the paper's closed-form results, called by name with Env.predict(name, ...).

The configuration lists which forms a paper enables (`enabled`); each form uses the parameters of the
other slots, so the closed form and the simulation always share one set of values.
"""

from __future__ import annotations

import numpy as np
import simos.constants as sc
from scipy.special import j0

from nvlab.env.core import Impl, implementation
from nvlab.env.slots.accumulation import HBAR, MU_B, W_cp

FORMS = {}


def form(name):
    def deco(f):
        FORMS[name] = f
        return f
    return deco


@implementation('analytic', 'closed_forms')
class ClosedForms(Impl):
    def call(self, name, *args, **kw):
        if name not in self.p['enabled']:
            raise ValueError(f'{name!r} is not enabled for this paper ({self.p["enabled"]})')
        return FORMS[name](self.env, *args, **kw)


# -- Rovny 2022 ---------------------------------------------------------------------------------------
@form('expected_r')
def expected_r(env, tau, init='parallel'):
    """Eq. (1) with Eq. (S18) averaged over the line and Eq. (S26): the expected Pearson r at spacing tau."""
    proto = {'tau_s': tau, 'init': init}
    env.check(proto)
    fs, w = env.slot('signal', proto).line()
    n = env.slot('accumulation', proto).p['n_pulses']
    a = env.slot('signal', proto).p['a_per_s']
    d1, d2 = env.slot('decoherence', proto).visibility(proto)
    ro = env.slot('readout', proto).p['nv']
    th = env.slot('init', proto).theta(proto)
    sign = np.sin(th[0]) * np.sin(th[1])
    r_ideal = 0.5 * d1 * d2 * np.sum(w * (1 - j0(a * W_cp(fs, tau, n) * n * tau)))
    return sign * r_ideal / (ro[0]['sigma_R'] * ro[1]['sigma_R'])


# -- Rovny 2025 ---------------------------------------------------------------------------------------
@form('sigma_B_min')
def sigma_B_min(env, protocol, readout, t_s, T_s):
    """Eq. (S59) for the entangled protocol and Rovny 2022 Eq. (S39) for two non-interacting NVs."""
    proto = {'protocol': protocol, 'readout': readout, 't_s': t_s}
    ro = env.slot('readout', proto).p
    sR, tR = ro['sigma_R'], ro['t_R_s']
    dec = env.slot('decoherence', proto).p
    T2, te = dec['T2_s'], dec['te_s']
    gamma = env.slot('signal', proto).p['gamma_e']
    if protocol in dec.get('gate_protocols', []):
        a = np.sqrt(2) * sR * np.exp(2 * (t_s + 2 * te) / T2) / np.sqrt(T_s / (t_s + 2 * te + tR))
    else:
        a = 2 * sR ** 2 * np.exp(2 * t_s / T2) / np.sqrt(T_s / (t_s + tR))
    return np.sqrt(-np.pi / (4 * gamma ** 2 * t_s) * np.log(1 - a)) if a < 1 else np.inf


# -- Zhou 2025 ----------------------------------------------------------------------------------------
@form('eta')
def eta(env, sensor, target, t_s):
    """SI Eq. (S13)."""
    proto = {'sensor': sensor, 'target': target, 't_s': t_s}
    A = env.slot('accumulation', proto).p['A_eff_Hz']
    dec = env.slot('decoherence', proto).p
    ro = env.slot('readout', proto).p
    t_ext = env.slot('timing', proto).p['t_ext_s']
    return (np.sqrt(1 + 1 / (ro['C'] ** 2 * ro['n_avg'])) * np.sqrt(1 + t_ext / t_s)
            / (np.pi * A * np.sqrt(t_s) * np.exp(-(t_s / dec['T2_s']) ** dec['p'])))


# -- Maze 2008 ----------------------------------------------------------------------------------------
@form('eta_methods')
def eta_methods(env, nu):
    """Methods prediction (solid curve in Fig. 3a): pi hbar sqrt(nu) / (g muB C F(1/nu)), T Hz^-1/2."""
    g = env.slot('accumulation').p['g']
    C = env.slot('readout').C
    return np.pi * HBAR * np.sqrt(nu) / (g * MU_B * C * env.slot('decoherence').F(1 / nu))


# -- Boss 2017 ----------------------------------------------------------------------------------------
@form('snr_s43')
def snr_s43(env, n):
    """Eq. (S43): Eq. (6) times e^{-2 Gamma n}, for this sample's signal."""
    ro, sig = env.slot('readout').p, env.slot('signal').p
    C, e = ro['c_per_readout'] * n, ro['eps']
    G = env.slot('decoherence').p['Gamma']
    return C ** 2 * e ** 2 * sig['N'] * np.exp(-2 * G * n) * sig['phi_max'] ** 2 / 16 / (C ** 2 * e ** 2 / 4 + C * (1 - e / 2))


@form('spectral_snr')
def spectral_snr(env, y, guard=50):
    """Eq. (4): peak power Y_j0 over the standard deviation of the noise floor (all positive-frequency bins away
    from DC and from the signal and its odd harmonics, S11)."""
    N, j0_ = env.slot('signal').p['N'], env.slot('signal').j0
    Y = np.abs(np.fft.rfft(y)) ** 2
    j = np.arange(len(Y))
    mask = j > guard
    for h in (1, 3, 5):
        a = (h * j0_) % N
        a = min(a, N - a)
        mask &= np.abs(j - a) > guard
    return Y[j0_] / Y[mask].std()


# -- Hopper 2020 --------------------------------------------------------------------------------------
@form('initialization')
def initialization(env, protocol):
    return env.slot('init', protocol).initialization(protocol)


@form('snr')
def snr(env, protocol):
    """Single-shot spin SNR = |p0 - p1| / sqrt(p0(1-p0) + p1(1-p1)) (SI 'Calibrating spin SNR')."""
    F = initialization(env, protocol)['F']
    p0, p1 = env.slot('readout', protocol).probabilities(F, protocol)
    return abs(p0 - p1) / np.sqrt(p0 * (1 - p0) + p1 * (1 - p1))


@form('efficiency')
def efficiency(env, protocol, tau_O_s):
    """Eq. 8: xi = SNR / sqrt(tau_I + tau_O + tau_R)."""
    return snr(env, protocol) / np.sqrt(env.shot_time(dict(protocol, tau_O_s=tau_O_s)))


@form('sensitivity')
def sensitivity(env, protocol):
    """Eq. 11-12 with tau_O = T2: (pi hbar / 2 g muB) sqrt(T2 + tau_I + tau_R) / T2 * sigma_R, sigma_R = sqrt(1 + 2/SNR^2);
    pi hbar / (2 g muB) = pi / (2 gamma_e), gamma_e from SimOS (CODATA)."""
    T2 = env.slot('decoherence', protocol).p['T2_s']
    tI = initialization(env, protocol)['tau_I']
    sR = np.sqrt(1 + 2 / snr(env, protocol) ** 2)
    return np.pi / (2 * abs(sc.ye)) * np.sqrt(T2 + tI + protocol['tau_read_s']) / T2 * sR


# -- Santagati 2019 -----------------------------------------------------------------------------------
@form('peak_speed_uT_per_ms')
def peak_speed(env, nu):
    """Authors' notebook cell 55: w nu / (2 pi) * N / T_axis * 1e3 (kHz/ms), then / gamma (kHz/uT)."""
    a = env.slot('analytic').p
    w_amp = env.slot('signal').p['w_amp']
    return w_amp * nu / (2 * np.pi) * a['n_epochs'] / a['axis_time_ms'] * 1e3 / a['gamma_kHz_per_uT']


@form('nms')
def nms(env, estimates, truths, w0, skip=50):
    """Median over runs per epoch of the squared error / w0^2, then median over epochs skip .. N-2 (notebook cells 20, 49)."""
    w0 = np.asarray(w0, dtype=float).reshape(-1, 1)
    med = np.median((np.asarray(estimates) - np.asarray(truths)) ** 2 / w0 ** 2, axis=0)
    return float(np.median(med[skip:-1]))


# -- Xie 2021 -----------------------------------------------------------------------------------------
@form('gate_fidelity')
def gate_fidelity(env, pulse, U_target, nodes=7):
    """Methods Eq. 14 averaged over the paper's noise model: F = |Tr(U^dagger U_target)| / dim."""
    sys_ = env.slot('system')
    F = 0.0
    for delta, alpha, w in env.slot('statistics').nodes(nodes):
        U = sys_.pulse_unitary(pulse, delta, alpha)
        F += w * abs(np.trace(U.conj().T @ U_target)) / sys_.dim
    return F
