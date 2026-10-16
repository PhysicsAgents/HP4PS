# field_tracking：跟踪随时间变化的磁场

[English](README.md) | 中文

## 系统

单个 NV 做 Ramsey 测量，条件理想：
- 不计退相干；
- 不计实验开销。

每个 epoch 做一次单发 Ramsey 测量：你给出相位积累时间 τ（µs），得到结果 0 或 1。

磁场对应的角频率随 epoch 序号 k 变化：ω(k) = ω0 + w·cos(νk + φ)。
- **已知：** w 和 ν，可以从 `env.slot('signal').p` 读取，是公开的先验。
- **未知：** ω0 和 φ，每次运行都不同，只能从测量结果推断。

读出模型的参数在 `env.slot('readout').p` 中。每次运行有固定数量的 epoch。

## 要测的量

每个 epoch 时的 ω。

## 性能指标

相对跟踪误差。先对每个 epoch 取各次运行"(估计值 − 真值)² / ω0²"的中位数，再对后段各 epoch 取中位数，最后开平方。

## 接口

- 环境：`env = nvlab.env.load('field_tracking')`
- 一次测量：`env.run({'tau_us': tau})`

要实现 `solutions/field_tracking/__init__.py` 中的 `track(env)`：
- 每个 epoch 恰好调用一次 `env.run`；
- 记录本 epoch 更新后对 ω 的估计；
- 返回每个 epoch 一个估计。

可以用任何算法和库，但所有代码和依赖都要放在 `solutions/field_tracking/` 目录内。

## 评分

评测在 ν 从慢到快的多种情形下，每种跑 100 次，与参考水平比较。评测时磁场放在独立进程里，不做测量就写出的轨迹会失败。之后还会在 ω0 范围和读出模型不同的隐藏样品上再跑一遍。

## 运行环境

- Python 3.12，依赖见 `requirements.txt`。
- 在仓库根目录用 `PYTHONPATH=.` 运行；环境用 `nvlab.env.load('field_tracking')` 加载。
- 你的代码写在 `solutions/field_tracking/__init__.py`。评测时使用原始的 `nvlab/` 和评测方自己的样品，你对 `nvlab/`、`configs/` 的修改不参与评分；评测还会在参数不同的隐藏样品上运行你的解法。
