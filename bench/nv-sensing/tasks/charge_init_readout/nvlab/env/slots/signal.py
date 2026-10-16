"""Signal slot: the field the sensor is exposed to. Values marked 'evaluator' are set with Env.set_signal."""

from __future__ import annotations

import numpy as np

from nvlab.env.core import Impl, implementation


class _Signal(Impl):
    def set(self, **values):
        for k, v in values.items():
            if k not in self.p:
                raise KeyError(f'{self.name} has no parameter {k}')
            self.p[k] = v


@implementation('signal', 'random_phase_ac')
class RandomPhaseAC(_Signal):
    """Random-phase AC signal with a line-broadened spectrum (Rovny 2022 SI Eq. S18, Fig. S2):
    per shot a frequency f from a Lorentzian (centre f0_Hz, fwhm_Hz) restricted to f_range_Hz and a
    uniform phase alpha. a_per_s is the J0 argument coefficient 4 gamma B0 of Eq. (S18)."""

    def sample(self, rng, shots, protocol=None):
        lo, hi = self.p['f_range_Hz']
        hw, f0 = self.p['fwhm_Hz'] / 2, self.p['f0_Hz']
        c_lo, c_hi = np.arctan((lo - f0) / hw), np.arctan((hi - f0) / hw)
        f = f0 + hw * np.tan(rng.uniform(c_lo, c_hi, shots))
        return {'f': f, 'alpha': rng.uniform(0, 2 * np.pi, shots), 'a': self.p['a_per_s']}

    def line(self, n=8001):
        """Frequencies and normalised Lorentzian weights over f_range_Hz (for the closed form)."""
        fs = np.linspace(*self.p['f_range_Hz'], n)
        w = 1 / (1 + ((fs - self.p['f0_Hz']) / (self.p['fwhm_Hz'] / 2)) ** 2)
        return fs, w / w.sum()


@implementation('signal', 'gaussian_noise')
class GaussianNoise(_Signal):
    """Correlated Gaussian noise with flat spectral density S_C = gamma^2 sigma_B^2 / Hz around the
    detection frequency (Rovny 2025 SI Eq. S57-S59). sigma_B_T: evaluator."""

    def chi(self, t_s):
        return t_s * self.p['gamma_e'] ** 2 * self.p['sigma_B_T'] ** 2 / np.pi


@implementation('signal', 'ac_tone')
class ACTone(_Signal):
    """B(t) = B_AC_T cos(2 pi nu_Hz t + phi_AC) along the NV axis (Maze 2008 Fig. 1d). nu_Hz, B_AC_T: evaluator."""


@implementation('signal', 'lockin_tone')
class LockinTone(_Signal):
    """A tone sampled synchronously (Boss 2017 Eq. 1, S8): phi_k = phi_max cos(2 pi j0 k / N + alpha),
    the power in one Fourier bin j0 of the N-sample record (Eq. 5 / S39 condition)."""

    @property
    def j0(self):
        return int(round(self.p['N'] * ((self.p['f_signal_Hz'] * self.p['t_s_bin_s']) % 1.0)))

    def sample(self, rng, shots, protocol=None):
        alpha = rng.uniform(0, 2 * np.pi)
        k = np.arange(shots)
        return {'phi': self.p['phi_max'] * np.cos(2 * np.pi * self.j0 * k / self.p['N'] + alpha)}


@implementation('signal', 'tracking_tone')
class TrackingTone(_Signal):
    """w(k) = w0 + w_amp cos(nu k + phi) per epoch k (Santagati 2019 Sec. IV, authors' TrackPrecModel):
    the datum of epoch k is taken at the current w, then w advances. Public: w_amp, nu (the authors'
    tracking model takes them as known). w0 and phi are drawn per run within w0_range / phase_random."""

    def __init__(self, params, env):
        super().__init__(params, env)
        self.reset()

    def reset(self, rng=None):
        rng = np.random.default_rng() if rng is None else rng
        lo, hi = self.p['w0_range']
        self._w0 = float(rng.uniform(lo, hi)) if hi > lo else float(lo)
        self._phi = float(rng.uniform(0, 2 * np.pi)) if self.p.get('phase_random') else 0.0
        self._w, self._true, self.epoch = self._w0, [], 0

    def step(self):
        """Current w for this epoch's datum; then advance (TrackPrecModel.est_prec order)."""
        w = self._w
        self._w = self._w0 + self.p['w_amp'] * np.cos(self.p['nu'] * self.epoch + self._phi)
        self._true.append(self._w)
        self.epoch += 1
        return w

    def truth(self):
        return {'w0': self._w0, 'phi': self._phi, 'true_after': list(self._true)}


@implementation('signal', 'deer_shift')
class DeerShift(_Signal):
    """Shift delta_tp_s of the target spin's pi pulse in DEER slope detection (Zhou 2025 SI Sec. 7). Evaluator."""
