"""Init slot: how the sensor is prepared (and, for projective sequences, the phase theta of the final pulse)."""

from __future__ import annotations

import numpy as np

from nvlab.env.core import Impl, implementation


@implementation('init', 'phases')
class Phases(Impl):
    """Fixed preparation: theta (in units of pi) per NV in p = (1 + V cos(phi - theta))/2, the probability of the
    state labelled 1 by the readout slot. E.g. Rovny 2022 Fig. 2A: parallel NVs read sin(phi) (theta = pi/2 each),
    antiparallel NV2 reads -sin(phi) (theta = -pi/2)."""

    def theta(self, protocol):
        return [np.pi * t for t in self.p['theta_pi']]


@implementation('init', 'protocol_phase')
class ProtocolPhase(Impl):
    """theta of the last pi/2 pulse chosen by the protocol (Maze 2008 Fig. 2 caption: 90 deg turns cos into sin)."""

    def theta(self, protocol):
        return [protocol['theta']]


@implementation('init', 'charge_rti')
class ChargeRTI(Impl):
    """Real-time charge initialization (Hopper 2020 main text Eq. 2-5, 9): repeat green pump + red probe until at
    least nu photons; F = (1 - eps_T)(1 - eps_D), tau_I = (tau_pump + tau_overhead + tau_probe) n_bar."""

    def initialization(self, protocol):
        P, tp, nu = protocol['P_probe_uW'], protocol['tau_probe_s'], protocol['nu']
        if int(nu) != nu or nu < 1:
            raise ValueError('threshold nu must be a positive integer')
        if not tp > 0:
            raise ValueError('tau_probe must be positive')
        nu = int(nu)
        charge = self.env.slot('system', protocol)
        pm = charge.photon_dist('-', P, tp, nmax=max(60, nu + 30))
        p0 = charge.photon_dist('0', P, tp, nmax=max(60, nu + 30))
        sm, s0 = pm[nu:].sum(), p0[nu:].sum()
        Pm = self.p['P_minus']
        q = Pm * sm + (1 - Pm) * s0
        eps_T = (1 - Pm) * s0 / q
        eps_D = 1 - np.exp(-self.p['tau_delay_s'] * charge.rates(P)[2])
        n_bar = 1 / q
        return {'F': (1 - eps_T) * (1 - eps_D), 'eps_T': eps_T, 'eps_D': eps_D, 'n_bar': n_bar, 'success': q,
                'tau_I': (self.p['tau_pump_s'] + self.p['tau_overhead_s'] + tp) * n_bar}

    def sample_time(self, protocol, shots, rng):
        ini = self.initialization(protocol)
        attempts = rng.geometric(ini['success'], shots)
        return attempts.sum() * (self.p['tau_pump_s'] + self.p['tau_overhead_s'] + protocol['tau_probe_s'])


@implementation('init', 'charge_ssi')
class ChargeSSI(Impl):
    """Steady-state initialization: 2 us of 532 nm light, NV- population 75.3 % (Hopper 2020 Fig. 1b)."""

    def initialization(self, protocol):
        return {'F': self.p['F'], 'tau_I': self.p['tau_s']}

    def sample_time(self, protocol, shots, rng):
        return shots * self.p['tau_s']
