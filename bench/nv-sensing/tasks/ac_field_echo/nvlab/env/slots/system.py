"""System slot: the quantum system or charge model a paper specifies at the Hamiltonian / rate level.

- register_e_N_C: NV electron + 14N + 13C at 8066 G (Xie 2021 Methods Eq. 3-14), coherent evolution by QuTiP.
- nv_charge: two-state NV-/NV0 charge dynamics under red light (Hopper 2020 SI Eq. 1-9, Shields 2015 SI S4-S5).
"""

from __future__ import annotations

import numpy as np
import qutip as qt
import simos.constants as sc
from numpy.polynomial.legendre import leggauss
from scipy.special import gammaln, i0e, i1e

from nvlab.env.core import Impl, implementation

TWO_PI = 2 * np.pi
US = 1e-6


# -- program operations (register_e_N_C) --------------------------------------------------------------
class Pulse:
    """Piecewise-constant controls. mw: list of tones {'offset_Hz': d, 're': [...], 'im': [...]} with amplitudes
    in Hz (Rabi frequency of the reduced two-level electron); rf: dict with optional 'Nx', 'Ny', 'Cx', 'Cy'
    amplitude lists in Hz. All lists have one value per piece."""

    def __init__(self, piece_s, mw=(), rf=None):
        self.piece_s = float(piece_s)
        self.mw = list(mw)
        self.rf = dict(rf or {})
        lens = {len(t['re']) for t in self.mw} | {len(t['im']) for t in self.mw} | {len(v) for v in self.rf.values()}
        if len(lens) != 1:
            raise ValueError('all control lists need the same number of pieces')
        self.n = lens.pop()

    @property
    def duration(self):
        return self.n * self.piece_s


class Uz:
    """Phase gate Uz(phi) = exp(-i phi O_z) on the listed qubits ('e', 'N', 'C'), from MW / RF phase shifts (Eq. 20)."""

    def __init__(self, phi, qubits):
        self.phi, self.qubits = float(phi), str(qubits)


class Wait:
    def __init__(self, t_s, field_T=0.0):
        self.t_s, self.field_T = float(t_s), float(field_T)


def duration(op):
    return op.duration if isinstance(op, Pulse) else op.t_s if isinstance(op, Wait) else 0.0


# basis order: electron (|0>, |-1>) x 14N (|+1>, |0>) x 13C (|+1/2>, |-1/2>)
_E0, _EM = qt.basis(2, 0), qt.basis(2, 1)
_N1, _N0 = qt.basis(2, 0), qt.basis(2, 1)
_CU, _CD = qt.basis(2, 0), qt.basis(2, 1)
_I2 = qt.qeye(2)
_BLOCKS = {(+1, -0.5): (_N1, _CD), (+1, +0.5): (_N1, _CU), (0, -0.5): (_N0, _CD), (0, +0.5): (_N0, _CU)}


def _proj(n, c):
    return qt.tensor(n * n.dag(), c * c.dag())


@implementation('system', 'register_e_N_C')
class RegisterENC(Impl):
    """Xie 2021 Methods Eq. 3-13 in the interaction picture (Eq. 4): MW tones act on the electron in each nuclear
    block with the cross-talk phases (d - o_j) t, o_j = 0, Azz, A_par, A_par + Azz for (+1,-1/2), (+1,+1/2),
    (0,-1/2), (0,+1/2); RF acts on the nuclei in ms = 0; quasi-static detuning delta and MW amplitude factor alpha."""

    dim = 8

    def __init__(self, params, env):
        super().__init__(params, env)
        s = self.p
        self.A_par = TWO_PI * s['A_par_Hz'] * US
        self.A_zz = TWO_PI * s['A_zz_Hz'] * US
        self.offsets = {(+1, -0.5): 0.0, (+1, +0.5): self.A_zz, (0, -0.5): self.A_par, (0, +0.5): self.A_par + self.A_zz}
        sx, sy = qt.sigmax() / 2, qt.sigmay() / 2
        self.Sx = {k: qt.tensor(sx, _proj(*v)) for k, v in _BLOCKS.items()}
        self.Sy = {k: qt.tensor(sy, _proj(*v)) for k, v in _BLOCKS.items()}
        e0 = _E0 * _E0.dag()
        self.rf_ops = {'Nx': qt.tensor(e0, sx, _I2), 'Ny': qt.tensor(e0, sy, _I2),
                       'Cx': qt.tensor(e0, _I2, sx), 'Cy': qt.tensor(e0, _I2, sy)}
        self.Pm1 = qt.tensor(_EM * _EM.dag(), _I2, _I2)
        self.Iz = {'e': qt.tensor(qt.sigmaz() / 2, _I2, _I2), 'N': qt.tensor(_I2, qt.sigmaz() / 2, _I2),
                   'C': qt.tensor(_I2, _I2, qt.sigmaz() / 2)}

    def pulse_unitary(self, pulse, delta_Hz=0.0, alpha=1.0):
        T = pulse.duration / US

        def piece(t):
            return min(int(t / (pulse.piece_s / US)), pulse.n - 1)

        H = [TWO_PI * delta_Hz * US * self.Pm1]
        for tone in pulse.mw:
            d = TWO_PI * tone['offset_Hz'] * US
            re = TWO_PI * alpha * np.asarray(tone['re'], float) * US
            im = TWO_PI * alpha * np.asarray(tone['im'], float) * US
            for k, o in self.offsets.items():
                w = d - o
                H.append([self.Sx[k], lambda t, re=re, im=im, w=w: re[piece(t)] * np.cos(w * t) - im[piece(t)] * np.sin(w * t)])
                H.append([self.Sy[k], lambda t, re=re, im=im, w=w: re[piece(t)] * np.sin(w * t) + im[piece(t)] * np.cos(w * t)])
        for key, amp in pulse.rf.items():
            a = TWO_PI * np.asarray(amp, float) * US
            H.append([self.rf_ops[key], lambda t, a=a: a[piece(t)]])
        # ODE integration: the MW terms oscillate within a piece, so QuTiP's piecewise_t (constant H per piece) is not valid here
        U = qt.propagator(qt.QobjEvo(H), T, options={'atol': 1e-10, 'rtol': 1e-10, 'max_step': pulse.piece_s / US / 4, 'nsteps': 10 ** 7})
        return U.full()

    def wait_unitary(self, t_s, delta_Hz=0.0, field_T=0.0):
        """Free evolution: quasi-static detuning and a sensed field (Methods Eq. 1: +gamma_e B Sz, -gamma_N B Iz_N,
        -gamma_C B Iz_C) with the gyromagnetic ratios of SimOS (CODATA); the paper gives none."""
        ge, gn, gc = abs(sc.ye) / TWO_PI, sc.yN14 / TWO_PI, sc.yC13 / TWO_PI
        H = TWO_PI * delta_Hz * self.Pm1 + TWO_PI * field_T * (
            -ge * self.Pm1 - gn * qt.tensor(_I2, _N1 * _N1.dag(), _I2) - gc * self.Iz['C'])
        return (-1j * H * t_s).expm().full()

    def uz(self, phi, qubits):
        O = sum(self.Iz[q] for q in qubits)
        return (-1j * phi * O).expm().full()

    def initial_state(self):
        """|ms=0, mN=+1, mC=-1/2> (Methods Eq. 18); its imperfections are in the decoherence (budget) slot."""
        return qt.tensor(_E0 * _E0.dag(), _N1 * _N1.dag(), _CD * _CD.dag()).full()

    def p_read(self, rho):
        """Population of the read state, 13C |-1/2>."""
        P = qt.tensor(_I2, _I2, _CD * _CD.dag()).full()
        return float(np.real(np.trace(P @ rho)))

    def unitary(self, op, delta, alpha, cache):
        if isinstance(op, Pulse):
            key = (id(op), delta, alpha)
            if key not in cache:
                cache[key] = (op, self.pulse_unitary(op, delta, alpha))
            return cache[key][1]
        if isinstance(op, Uz):
            return self.uz(op.phi, op.qubits)
        if isinstance(op, Wait):
            return self.wait_unitary(op.t_s, delta, op.field_T)
        raise TypeError(f'operation {type(op).__name__} is not allowed (Pulse, Uz, Wait only)')


# -- charge model (nv_charge) ------------------------------------------------------------------------
_X, _W = leggauss(400)


def _pois(mu, n):
    return np.exp(n * np.log(np.maximum(mu, 1e-300)) - mu - gammaln(n + 1))


@implementation('system', 'nv_charge')
class NVCharge(Impl):
    """Hopper 2020 SI 'Charge readout model' (Eq. 1-4, from Shields 2015 SI Eq. S4-S5): photon rates gamma_-, gamma_0
    and interconversion Gamma_Ion, Gamma_Rec; p(n|-) sums the odd- and even-transition terms (normalised to 1),
    p(n|0) swaps Ion <-> Rec and gamma_- <-> gamma_0. Rates vs red power (SI Eq. 6-9, Table I)."""

    def rates(self, P_uW):
        r = self.p
        return (r['C_minus_Hz_per_uW'] * P_uW, r['C_0_Hz_per_uW'] * P_uW + r['D_Hz'],
                r['C_ion_Hz_per_uW2'] * P_uW ** 2, r['C_rec_Hz_per_uW2'] * P_uW ** 2)

    @staticmethod
    def _dist(g1, g0, G1, G0, tR, nmax):
        t = 0.5 * tR * (_X + 1)
        wt = 0.5 * tR * _W
        n = np.arange(nmax + 1)[:, None]
        arg = 2 * np.sqrt(G1 * G0 * t * (tR - t))
        base = (G0 - G1) * t - G0 * tR
        odd = G1 * np.exp(base + arg) * i0e(arg)
        even = np.sqrt(G1 * G0 * t / (tR - t)) * np.exp(base + arg) * i1e(arg)
        P = _pois(g1 * t + g0 * (tR - t), n)
        return (P * (odd + even) * wt).sum(1) + np.exp(-G1 * tR) * _pois(g1 * tR, n[:, 0])

    def photon_dist(self, start, P_uW, t_s, nmax=60):
        """p(n | initial charge state `start` ('-' or '0')) for n = 0..nmax during a red probe."""
        if not 0 < P_uW <= self.p['P_max_uW']:
            raise ValueError(f'red power {P_uW} uW outside (0, {self.p["P_max_uW"]}] uW, the range the paper applies its charge model to')
        gm, g0, Gi, Gr = self.rates(P_uW)
        if start == '-':
            return self._dist(gm, g0, Gi, Gr, t_s, nmax)
        if start == '0':
            return self._dist(g0, gm, Gr, Gi, t_s, nmax)
        raise ValueError("start must be '-' or '0'")
