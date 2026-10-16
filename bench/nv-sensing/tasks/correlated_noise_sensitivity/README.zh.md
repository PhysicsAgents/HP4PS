# correlated_noise_sensitivity：探测空间关联的磁噪声

[English](README.md) | 中文

## 系统

两颗 NV 色心处在同一个空间关联的磁噪声场中。噪声场的谱密度在探测频率附近是平坦的，均方根幅度为 σB。

可选的测量方案有两种：
- **`entangled`：** 把两颗 NV 制备成 Bell 态 |Φ⟩、|Ψ⟩（各用一半发次），比较两者的差信号。
- **`non-interacting`：** 两颗 NV 不纠缠，直接算它们读数之间的相关。

可选的读出方式有两种：
- **`conventional`：** 读出快，但读出噪声大；
- **`scc`：** 读出噪声小，但每次读出耗时长。

相干时间、纠缠门时长和读出参数见配置。

## 要测的量

在总实验时间 T 内能探测到的最弱关联场 σB。判据是 SNR = 1。

## 性能指标

在给定 T 下的最小可测 σB。等价地看：σB 固定时，SNR 越高越好。

## 接口

- 环境：`env = nvlab.env.load('correlated_noise_sensitivity')`
- 测量：`env.run({'protocol': ..., 'readout': ..., 't_s': ...}, shots=..., repeats=..., rng=...)` 返回估计量。其 SNR 取多次重复的均值除以标准差。
- 每发时长：`env.shot_time({...})`
- 要求：shots × 每发时长 ≤ T。

要实现 `solutions/correlated_noise_sensitivity/__init__.py` 中的 `design(env, T_s) -> dict(protocol, readout, t_s, shots)`。

## 评分

T 取 10³、10⁴、10⁶ s。评测把 σB 设为参考水平，检查两项：
1. 你的方案的 SNR 是否达到 1；
2. 相对"不纠缠 + 常规读出"的 SNR 增益。

之后还会在相干时间和门时长不同的隐藏样品上再跑一遍。

## 运行环境

- Python 3.12，依赖见 `requirements.txt`。
- 在仓库根目录用 `PYTHONPATH=.` 运行；环境用 `nvlab.env.load('correlated_noise_sensitivity')` 加载。
- 你的代码写在 `solutions/correlated_noise_sensitivity/__init__.py`。评测时使用原始的 `nvlab/` 和评测方自己的样品，你对 `nvlab/`、`configs/` 的修改不参与评分；评测还会在参数不同的隐藏样品上运行你的解法。
