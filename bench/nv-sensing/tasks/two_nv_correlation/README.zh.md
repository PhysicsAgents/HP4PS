# two_nv_correlation：两颗 NV 的逐发关联

[English](README.md) | 中文

## 系统

两颗浅层 NV 色心，可以分别读出。

- 它们共同感受一个外加的随机相位交流磁场。
- 两颗都用 XY8 动态解耦序列感应，序列可选平行或反平行初始化。
- 读出方式是自旋到电荷转换（SCC），记录每一发的光子数。

当前的工作点：
- XY8-4，共 32 个脉冲；
- 电离时间 200 ns；
- 脉冲间隔 τ 在 200–300 ns 之间。

## 要测的量

两颗 NV 逐发读数之间的 Pearson 相关系数 r，以及使相关最强的脉冲间隔。

## 性能指标

相关系数 r 的大小和符号。平行初始化时 r 为正，反平行时为负。

## 接口

- 环境：`env = nvlab.env.load('two_nv_correlation')`
- 测量：`env.run({'tau_s': tau, 'init': 'parallel' 或 'antiparallel'}, shots=..., rng=...)`，返回两颗 NV 各自的逐发光子数。

要实现 `solutions/two_nv_correlation/__init__.py` 中的两个函数：
- `resonant_tau(env, rng=None) -> float`
- `pearson(c1, c2) -> float`

## 评分

评测在你给出的 τ 处，平行和反平行各测 2000 万发，用你的 `pearson` 计算相关，并与参考水平比较。之后还会在信号频率不同的隐藏样品上再跑一遍。

## 运行环境

- Python 3.12，依赖见 `requirements.txt`。
- 在仓库根目录用 `PYTHONPATH=.` 运行；环境用 `nvlab.env.load('two_nv_correlation')` 加载。
- 你的代码写在 `solutions/two_nv_correlation/__init__.py`。评测时使用原始的 `nvlab/` 和评测方自己的样品，你对 `nvlab/`、`configs/` 的修改不参与评分；评测还会在参数不同的隐藏样品上运行你的解法。
