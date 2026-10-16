"""Readout slot: from the spin state (state labelled 1 / 0) to what is recorded.

Shot-by-shot implementations have sample(m, protocol, rng, nv); channels report probabilities;
large-N implementations have transform(mean, protocol) -> (mean of the estimate, per-shot standard deviation).
"""

from __future__ import annotations

import numpy as np

from nvlab.env.core import Impl, implementation


@implementation('readout', 'poisson_sigma_R')
class PoissonSigmaR(Impl):
    """Photon counting, Poisson with mean alpha_1 (state 1) or alpha_0 (state 0) per NV (Rovny 2022 SI Eq. S19-S25):
    alpha_0 - alpha_1 from the measured readout noise sigma_R = sqrt(1 + 2(a0 + a1)/(a0 - a1)^2), a0 + a1 = 2 x mean count."""

    def alphas(self, nv):
        q = self.p['nv'][nv]
        total = 2 * q['mean_count']
        diff = np.sqrt(2 * total / (q['sigma_R'] ** 2 - 1))
        return (total + diff) / 2, (total - diff) / 2

    def sample(self, m, protocol, rng, nv=0):
        a0, a1 = self.alphas(nv)
        return rng.poisson(np.where(m, a1, a0))


@implementation('readout', 'poisson_gain')
class PoissonGain(Impl):
    """Repetitive QND readout of a nuclear memory (Boss 2017 Eq. 3): y = Pois[C (1 - eps m)], C = c_per_readout x n."""

    def gain(self, n):
        return self.p['c_per_readout'] * n

    def sample(self, m, protocol, rng, nv=0):
        n = protocol['n']
        return rng.poisson(self.gain(n) * (1 - self.p['eps'] * m))


@implementation('readout', 'binary_channel')
class BinaryChannel(Impl):
    """Reported outcome 1 with probability p1_given1 (state 1) or p1_given0 (state 0): a readout of fidelity F
    (Xie 2021: p1_given1 = F, p1_given0 = 1 - F) or the authors' infidelity model (Santagati 2019)."""

    def probability(self, p_state1):
        return self.p['p1_given1'] * p_state1 + self.p['p1_given0'] * (1 - p_state1)

    def sample(self, m, protocol, rng, nv=0):
        return (rng.random(np.shape(m)) < np.where(m, self.p['p1_given1'], self.p['p1_given0'])).astype(int)


@implementation('readout', 'sigma_R')
class SigmaR(Impl):
    """Readout characterised by sigma_R only, large-N limit (Rovny 2025 SI Eq. S49-S51; Rovny 2022 Eq. S25, S36):
    entangled pair: estimate r_e / sigma_S with mean sqrt(2) r_e,ideal / sqrt(1 + sigma_R^2);
    two non-interacting NVs: Pearson r with mean r_ideal / sigma_R^2. Unit per-shot standard deviation."""

    def transform(self, mean, protocol):
        sR = self.p['sigma_R']
        if protocol.get('protocol') == 'entangled':
            return np.sqrt(2) * mean / np.sqrt(1 + sR ** 2), 1.0
        return mean / sR ** 2, 1.0


@implementation('readout', 'contrast_C')
class ContrastC(Impl):
    """Maze 2008 Methods: C^-2 = 1 + 2(a0 + a1 + a0 a1)/(a0 - a1)^2; the single-shot uncertainty of the
    signal S_B = P0 is 1/C (the value for which the paper's definitions give its Methods prediction)."""

    @property
    def C(self):
        a0, a1 = self.p['a0'], self.p['a1']
        return 1 / np.sqrt(1 + 2 * (a0 + a1 + a0 * a1) / (a0 - a1) ** 2)

    def transform(self, mean, protocol):
        return mean, 1 / self.C


@implementation('readout', 'photons_C_n')
class PhotonsCn(Impl):
    """Zhou 2025 SI Eq. S11 (in the form that gives Eq. S13): per-shot readout noise sqrt(1 + 1/(C^2 n_avg));
    the estimate is the slope signal in units of it."""

    def transform(self, mean, protocol):
        return mean / np.sqrt(1 + 1 / (self.p['C'] ** 2 * self.p['n_avg'])), 1.0


@implementation('readout', 'scc_charge')
class SCCCharge(Impl):
    """Hopper 2020 Eq. 6-7 and SI 'Calibrating spin SNR': NV- probability after spin-to-charge conversion
    beta_i F + beta_eps (1 - F) for spin i, read by a red probe (P_read_uW, tau_read_s) with photon threshold k."""

    def _tails(self, protocol):
        k = protocol['threshold']
        if int(k) != k or k < 1:
            raise ValueError('threshold must be a positive integer')
        if not protocol['tau_read_s'] > 0:
            raise ValueError('tau_R must be positive')
        k = int(k)
        charge = self.env.slot('system', protocol)
        P, t = protocol['P_read_uW'], protocol['tau_read_s']
        return (charge.photon_dist('-', P, t, nmax=max(80, k + 40))[k:].sum(),
                charge.photon_dist('0', P, t, nmax=max(80, k + 40))[k:].sum())

    def probabilities(self, F, protocol):
        """P(count >= threshold) for spin 0 and spin 1."""
        tm, t0 = self._tails(protocol)
        out = []
        for b in (self.p['beta0'], self.p['beta1']):
            beta = b * F + self.p['beta_eps'] * (1 - F)
            out.append(beta * tm + (1 - beta) * t0)
        return out[0], out[1]

    def sample(self, m, protocol, rng, nv_minus):
        """m: spin (0/1) per shot; nv_minus: charge state after initialization per shot."""
        tm, t0 = self._tails(protocol)
        b = np.where(m, self.p['beta1'], self.p['beta0'])
        after = np.where(nv_minus, rng.random(len(m)) < b, rng.random(len(m)) < self.p['beta_eps'])
        return rng.random(len(m)) < np.where(after, tm, t0)
