# NV 传感测量题目

[English](README.md) | 中文

每道题是一个独立仓库（`tasks/<题目>/`），按其 README 完成 `solutions/<题目>/__init__.py`。
评分由出题方进行：先与参考水平比较，再在参数不同的隐藏样品上运行一遍。两项都通过得 1 分，并记录各工况实际测得的测量精度。

| 题目 | 内容 |
|---|---|
| nuclear_entangled_phase | 用两个核自旋测相位 |
| two_nv_correlation | 两颗 NV 的逐发关联 |
| correlated_noise_sensitivity | 探测空间关联的磁噪声 |
| dark_spin_detection | 探测单个暗自旋 |
| ac_field_echo | 用单个 NV 测交流磁场 |
| lockin_readout_gain | 连续采样测量中的读出增益 |
| charge_init_readout | 电荷初始化与自旋读出 |
| field_tracking | 跟踪随时间变化的磁场 |

## 容器

已发布的做题镜像，题目仓库在 `/work`：

```
docker run -it --name <容器名> --network none ghcr.io/physicsagents/hp4ps/<题目>:1.0.0
docker cp <容器名>:/work/solutions/<题目> <交给评测方的目录>/<题目>/solutions/<题目>
```

## 从源码构建

本目录就是构建上下文：

```
scripts/build_images.sh . 1.0.0                         # 依赖镜像 + 每道题一个做题镜像
```

或者只构建依赖镜像，把题目仓库挂载进去：

```
docker build -t nv-sensing:latest .
scripts/agent_container.sh tasks/<题目> <容器名>       # 题目仓库挂载到 /work，不联网
docker exec -w /work <容器名> python ...
```
