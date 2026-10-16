"""Timing slot: the duration of one repetition of the protocol (initialization is included where the paper does)."""

from __future__ import annotations

from nvlab.env.core import Impl, implementation


@implementation('timing', 'sense_gates_readout')
class SenseGatesReadout(Impl):
    """t + 2 te (gate-based protocols) + t_R of the chosen readout; initialization ignored (Rovny 2025 Eq. S59, S39).
    te and the gate-based protocols are those of the decoherence slot (one value for both)."""

    def shot_time(self, protocol):
        dec = self.env.slot('decoherence', protocol).p
        gates = 2 * dec['te_s'] if protocol.get('protocol') in dec.get('gate_protocols', []) else 0.0
        return protocol['t_s'] + gates + self.env.slot('readout', protocol).p['t_R_s']


@implementation('timing', 'sense_plus_overhead')
class SensePlusOverhead(Impl):
    """t + t_ext (Zhou 2025 SI Eq. S11: N = T / (t_DEER + t_ext))."""

    def shot_time(self, protocol):
        return protocol['t_s'] + self.p['t_ext_s']


@implementation('timing', 'period')
class Period(Impl):
    """Shots repeat every period_s, which must hold polarization + echo + readout (Maze 2008 Fig. 1d, Methods)."""

    def shot_time(self, protocol):
        if protocol['period_s'] < self.p['tau_p_s'] + self.p['tau_r_s'] + protocol['tau_s'] - 1e-15:
            raise ValueError('period shorter than polarization + echo + readout')
        return protocol['period_s']


@implementation('timing', 'init_operation_readout')
class InitOperationReadout(Impl):
    """tau_I + tau_O + tau_R (Hopper 2020 Eq. 8)."""

    def shot_time(self, protocol):
        tI = self.env.slot('init', protocol).initialization(protocol)['tau_I']
        return tI + protocol['tau_O_s'] + protocol['tau_read_s']
