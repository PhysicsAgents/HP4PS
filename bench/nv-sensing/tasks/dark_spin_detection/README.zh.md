# dark_spin_detection：探测单个暗自旋

[English](README.md) | 中文

## 系统

一对相互耦合的 NV 色心旁边有暗自旋（目标 `DS1`、`DS2+`），用 DEER 斜率法来探测：在 DEER 时间 t_DEER 内，把目标自旋 π 脉冲的位置平移 δt_p，信号随之线性变化。

可选的传感器有两种：
- **`NV1`：** 单个 NV；
- **`psi2`：** 两颗 NV 的纠缠态。

每种"传感器–目标"组合都有各自的有效耦合、相干衰减、读出对比度、光子数和每次重复的额外开销，具体见配置。

## 要测的量

π 脉冲平移 δt_p。

## 性能指标

灵敏度：总时间 1 s 内使 SNR = 1 的最小 δt_p，越小越好。另一个指标是传感器选择：为每个目标选出灵敏度更好的那个传感器。

## 接口

- 环境：`env = nvlab.env.load('dark_spin_detection')`
- 测量：`env.run({'sensor': ..., 'target': ..., 't_s': t_DEER, 'delta_tp_s': 你施加的平移}, T_s=1.0, repeats=..., rng=...)`，返回平均后的斜率信号，以单发读出噪声为单位。
- 约束：t_DEER 在 (0, 20 µs] 之间。

要实现 `solutions/dark_spin_detection/__init__.py` 中的两个函数：
- `best_t_DEER(env, sensor, target) -> float`
- `choose_sensor(env, target) -> str`

## 评分

评测在你给出的 t_DEER 处测两种传感器的灵敏度，检查两项：
1. 两者之比和传感器选择是否达到参考水平；
2. 在参数不同的隐藏样品上，你选的 t_DEER 和传感器是否仍然最优。

## 运行环境

- Python 3.12，依赖见 `requirements.txt`。
- 在仓库根目录用 `PYTHONPATH=.` 运行；环境用 `nvlab.env.load('dark_spin_detection')` 加载。
- 你的代码写在 `solutions/dark_spin_detection/__init__.py`。评测时使用原始的 `nvlab/` 和评测方自己的样品，你对 `nvlab/`、`configs/` 的修改不参与评分；评测还会在参数不同的隐藏样品上运行你的解法。
