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

## Building from source

Instead of pulling an image, the same image can be built locally from the sources in this repository. `bench/<set>/` is the build context of a set of samples, and `tasks/<sample-id>/` in it is the task repository handed to the agent. For example, the NV sensing samples:

```bash
cd bench/nv-sensing
scripts/build_images.sh . 1.0.0
```

The script builds the dependency image first, then `ghcr.io/physicsagents/hp4ps/<sample-id>:1.0.0` for every sample, with the task repository at `/work`. Without `--push` it only builds locally. Scoring needs the hidden samples and tests and is not part of this repository.

All published images: [https://github.com/orgs/PhysicsAgents/packages?repo_name=HP4PS](https://github.com/orgs/PhysicsAgents/packages?repo_name=HP4PS)
