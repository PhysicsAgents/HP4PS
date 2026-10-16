# ac_field_echo：用单个 NV 测交流磁场

[English](README.md) | 中文

## 系统

块体金刚石中的单个 NV 电子自旋，用自旋回波测量频率为 ν（1–10 kHz）的交流磁场 B_AC·cos(2πνt + φ_AC)。

每一发的流程：
1. 极化；
2. π/2 – τ/2 – π – τ/2 – π/2；
3. 读出。

回波包络受 ¹³C 核自旋浴的影响。读出光子数很少，单发噪声大。极化和读出的时长、回波包络、光子数等参数见配置。

## 要测的量

交流磁场幅度 B_AC。

## 性能指标

T 秒平均后的最小可测场 δB_min = σ(S̄)/|dS̄/dB_AC|，单位 T。另一个指标是它随平均时间的标度。

## 接口

- 环境：`env = nvlab.env.load('ac_field_echo')`
- 测量：`env.run(d, T_s=T, repeats=..., rng=...)` 返回 T 秒平均后的信号。d 即下面 `design` 返回的字典。
- ν 和 B_AC 由评测设定。
- 约束：
  - 0 < τ ≤ 1 ms；
  - 每发周期 ≥ 极化 + τ + 读出；
  - 发次 N = floor(T / 周期)。

要实现 `solutions/ac_field_echo/__init__.py` 中的 `design(env, nu_Hz, T_s) -> dict(tau_s, period_s, phi_ac, theta)`。

## 评分

评测在 1.4–7.4 kHz 的若干频率、T = 1 s 下测 δB_min，并在 0.3–155 s 范围内测平均时间标度，与参考水平比较。之后还会在样品参数和频率都不同的隐藏样品上再跑一遍。

## 运行环境

- Python 3.12，依赖见 `requirements.txt`。
- 在仓库根目录用 `PYTHONPATH=.` 运行；环境用 `nvlab.env.load('ac_field_echo')` 加载。
- 你的代码写在 `solutions/ac_field_echo/__init__.py`。评测时使用原始的 `nvlab/` 和评测方自己的样品，你对 `nvlab/`、`configs/` 的修改不参与评分；评测还会在参数不同的隐藏样品上运行你的解法。
