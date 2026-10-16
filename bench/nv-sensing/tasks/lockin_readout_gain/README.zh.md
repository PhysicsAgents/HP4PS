# lockin_readout_gain：连续采样测量中的读出增益

[English](README.md) | 中文

## 系统

一个 NV 色心对一个交流信号做同步（锁相）采样，每个采样点输出一次光子计数。

每个采样点内：
1. 自旋累积相位；
2. 把相位存进一个核自旋存储；
3. 对这个存储做 n 次重复的非破坏性读出。

读出次数 n 越多，收集的光子越多，但存储每读一次都有一定概率退极化，信息随之丢失。一条记录有 N 个采样点。光学对比度、每次读出的光子数、退极化率见配置。

## 要测的量

记录频谱中的信号峰。

## 性能指标

频谱 SNR：信号所在频率分量的功率 |Σ y_k e^{−2πikj/N}|²，除以噪声底的标准差。

## 接口

- 环境：`env = nvlab.env.load('lockin_readout_gain')`
- 测量：`env.run({'n': n}, shots=N, rng=...)` 返回一条 N 点记录的光子计数。
- n 为整数，取值 1–2000。

要实现 `solutions/lockin_readout_gain/__init__.py` 中的 `choose_n(env) -> int`。

## 评分

评测在你给出的 n 处录多条记录，求平均频谱 SNR，与参考水平比较。之后还会在对比度、退极化率和信号幅度都不同的隐藏样品上再跑一遍。

## 运行环境

- Python 3.12，依赖见 `requirements.txt`。
- 在仓库根目录用 `PYTHONPATH=.` 运行；环境用 `nvlab.env.load('lockin_readout_gain')` 加载。
- 你的代码写在 `solutions/lockin_readout_gain/__init__.py`。评测时使用原始的 `nvlab/` 和评测方自己的样品，你对 `nvlab/`、`configs/` 的修改不参与评分；评测还会在参数不同的隐藏样品上运行你的解法。
