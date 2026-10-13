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

全部已发布镜像：[https://github.com/orgs/PhysicsAgents/packages?repo_name=HP4PS](https://github.com/orgs/PhysicsAgents/packages?repo_name=HP4PS)
