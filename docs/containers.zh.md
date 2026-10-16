# 容器

[English](containers.md) | 中文

基准测试样本和以容器交付的工具，都发布到 PhysicsAgents 组织下的 GitHub 容器仓库。

## 命名

- 镜像：`ghcr.io/physicsagents/hp4ps/<name>:<version>`，其中 `<name>` 是小写的样本编号或工具名。
- 每个镜像都带标签 `org.opencontainers.image.source=https://github.com/PhysicsAgents/HP4PS`，这样它会出现在仓库的 Packages 列表里。

## 发布

1. 用带 `write:packages` 权限的 GitHub token 登录一次：

   ```bash
   gh auth token | docker login ghcr.io -u <github-user> --password-stdin
   ```

2. 构建并推送：

   ```bash
   docker build --label org.opencontainers.image.source=https://github.com/PhysicsAgents/HP4PS -t ghcr.io/physicsagents/hp4ps/<name>:<version> .
   docker push ghcr.io/physicsagents/hp4ps/<name>:<version>
   ```

3. 新的包默认是私有的。在包页面的 *Package settings → Change visibility* 里设为公开，只需设置一次。

## 从源码构建

不想拉取镜像时，可以用本仓库里的源码在本地构建出同样的镜像。`bench/<集合>/` 是一组样本的构建上下文，其中 `tasks/<样本编号>/` 是交给智能体的题目仓库。例如 NV 传感样本：

```bash
cd bench/nv-sensing
scripts/build_images.sh . 1.0.0
```

脚本先构建依赖镜像，再为每个样本构建 `ghcr.io/physicsagents/hp4ps/<样本编号>:1.0.0`，题目仓库在 `/work`。不加 `--push` 时只在本机构建。评分需要隐藏样品和测试，不在本仓库中。

全部已发布镜像：[https://github.com/orgs/PhysicsAgents/packages?repo_name=HP4PS](https://github.com/orgs/PhysicsAgents/packages?repo_name=HP4PS)
