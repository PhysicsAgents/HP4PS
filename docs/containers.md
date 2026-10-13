# Containers

English | [中文](containers.zh.md)

Benchmark samples and container-delivered tools are published to the GitHub Container Registry under the PhysicsAgents organization.

## Naming

- Image: `ghcr.io/physicsagents/hp4ps/<name>:<version>`, where `<name>` is the sample id or tool name in lower case.
- Every image carries the label `org.opencontainers.image.source=https://github.com/PhysicsAgents/HP4PS`, so it is listed under the repository's packages.

## Publishing

1. Log in once, with a GitHub token that has the `write:packages` scope:

   ```bash
   gh auth token | docker login ghcr.io -u <github-user> --password-stdin
   ```

2. Build and push:

   ```bash
   docker build --label org.opencontainers.image.source=https://github.com/PhysicsAgents/HP4PS -t ghcr.io/physicsagents/hp4ps/<name>:<version> .
   docker push ghcr.io/physicsagents/hp4ps/<name>:<version>
   ```

3. A new package starts private. Make it public once under the package's *Package settings → Change visibility*.

All published images: [https://github.com/orgs/PhysicsAgents/packages?repo_name=HP4PS](https://github.com/orgs/PhysicsAgents/packages?repo_name=HP4PS)
