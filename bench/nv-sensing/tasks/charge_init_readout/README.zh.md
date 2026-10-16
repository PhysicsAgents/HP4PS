# charge_init_readout：电荷初始化与自旋读出

[English](README.md) | 中文

## 系统

单个 NV 色心，每次测量由三步组成。

1. **电荷初始化，二选一：**
   - **实时初始化（`rti`）：** 反复执行"绿光泵浦 + 红光探测"，直到探测到的光子数达到阈值 ν；
   - **稳态初始化（`ssi`）：** 固定一段绿光。
2. **自旋操作：** 时长 τO。
3. **SCC 读出：** 先做自旋到电荷转换，再用红光探测电荷态，按光子数阈值判读。

红光下的电荷动力学、转换效率等参数见配置。红光功率上限为 200 µW。

## 要测的量

自旋态。

## 性能指标

读出效率 ξ = SNR/√(τI + τO + τR)，以及由它决定的交流磁场灵敏度，单位 T/√Hz。

## 你能控制的

| 键 | 含义 |
|---|---|
| `init` | `'rti'` 或 `'ssi'` |
| `P_probe_uW`、`tau_probe_s`、`nu` | 实时初始化的探测功率、时长、阈值 |
| `P_read_uW`、`tau_read_s`、`threshold` | 电荷读出的功率、时长、阈值 |

## 接口

- 环境：`env = nvlab.env.load('charge_init_readout')`
- 逐发测量：`env.run(dict(d, spin=0 或 1), shots=..., rng=...)`，返回每发的判读结果和总耗时。
- 模型：`env.slot('init', d).initialization(d)`、`env.slot('readout', d).probabilities(F, d)`、`env.shot_time(dict(d, tau_O_s=...))`。

要实现 `solutions/charge_init_readout/__init__.py` 中的 `protocol(env, tau_O_s) -> dict`。

## 评分

评测取 τO 等于相干时间，计算你的方案的灵敏度，并逐发执行核对 SNR，与参考水平比较。之后还会在相干时间、亮度、背景都不同的隐藏样品上再跑一遍。

## 运行环境

- Python 3.12，依赖见 `requirements.txt`。
- 在仓库根目录用 `PYTHONPATH=.` 运行；环境用 `nvlab.env.load('charge_init_readout')` 加载。
- 你的代码写在 `solutions/charge_init_readout/__init__.py`。评测时使用原始的 `nvlab/` 和评测方自己的样品，你对 `nvlab/`、`configs/` 的修改不参与评分；评测还会在参数不同的隐藏样品上运行你的解法。
