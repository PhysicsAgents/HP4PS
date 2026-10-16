# nuclear_entangled_phase：用两个核自旋测相位

[English](README.md) | 中文

## 系统

单个 NV 色心，在强磁场下组成一个三量子比特寄存器：
- 电子自旋取两个能级；
- 一个 ¹⁴N 核自旋取两个能级；
- 一个强耦合的 ¹³C 核自旋。

能做的操作：
- **微波（MW）脉冲：** 作用在电子上，可以同时发多个频率，每段给出实部和虚部幅度。不同核态下电子的跃迁频率不同。
- **射频（RF）脉冲：** 电子处于 ms = 0 时作用在 ¹⁴N 或 ¹³C 上。
- **相位门和等待。**
- **读出：** 只能读 ¹³C。

控制存在准静态失谐和微波幅度的涨落。态制备、弛豫和读出都不完美，具体参数见配置。

## 要测的量

一个同时作用在 ¹⁴N 和 ¹³C 上的相位 φ。评测会把 Uz(φ) 插在你给出的两段程序之间。

## 性能指标

相位测量的 Fisher 信息相对标准量子极限的增益，单位 dB。

评测用 16 个 φ 值扫出 ¹³C 的读出条纹，拟合 P = c + (Vis/2)·sin(2φ + p)，增益取 10·log10(2·Vis²)。条纹必须是单一的 2φ 谐波。

## 接口

- 环境：`env = nvlab.env.load('nuclear_entangled_phase')`
- 执行程序：`env.run({'program': [...]})`，返回把 ¹³C 读成 |−½⟩ 的概率。
- 程序由三种操作组成：
  - `nvlab.env.Pulse(piece_s, mw=[{'offset_Hz', 're', 'im'}, ...], rf={'Nx'|'Ny'|'Cx'|'Cy': [...]})`
  - `nvlab.env.Uz(phi, qubits)`
  - `nvlab.env.Wait(t_s)`
- 参数可通过 `env.slot('system').p` 等读取。
- 约束：整段程序总长不超过 210 µs。

要实现 `solutions/nuclear_entangled_phase/__init__.py` 中的 `interferometer(env) -> (before, after)`。

## 评分

增益与参考水平比较，并在参数不同的隐藏样品上再跑一遍。

## 运行环境

- Python 3.12，依赖见 `requirements.txt`。
- 在仓库根目录用 `PYTHONPATH=.` 运行；环境用 `nvlab.env.load('nuclear_entangled_phase')` 加载。
- 你的代码写在 `solutions/nuclear_entangled_phase/__init__.py`。评测时使用原始的 `nvlab/` 和评测方自己的样品，你对 `nvlab/`、`configs/` 的修改不参与评分；评测还会在参数不同的隐藏样品上运行你的解法。
