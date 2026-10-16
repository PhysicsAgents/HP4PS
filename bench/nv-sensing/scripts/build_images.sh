#!/bin/sh
# Build the agent images from a package directory (scripts/build_package.py): the dependency image
# (Dockerfile), then one image per task with the task repository at /work (agent.Dockerfile).
# With --push the task images are pushed. Run from anywhere; PACKAGE_DIR is the build context.
#   usage: scripts/build_images.sh PACKAGE_DIR VERSION [--push]
#   images: $REGISTRY/<task>:VERSION, REGISTRY defaults to ghcr.io/physicsagents/hp4ps
set -eu
[ $# -ge 2 ] || { echo "usage: $0 PACKAGE_DIR VERSION [--push]" >&2; exit 2; }
PKG=$(cd "$1" && pwd)
VERSION=$2
PUSH=${3:-}
REGISTRY=${REGISTRY:-ghcr.io/physicsagents/hp4ps}
SOURCE=${SOURCE:-https://github.com/PhysicsAgents/HP4PS}
DOCKER=${DOCKER:-docker}
$DOCKER build --label "org.opencontainers.image.source=$SOURCE" -t "nv-sensing:$VERSION" -f "$PKG/Dockerfile" "$PKG"
for dir in "$PKG"/tasks/*/; do
    task=$(basename "$dir")
    $DOCKER build --build-arg "BASE=nv-sensing:$VERSION" --build-arg "TASK=$task" \
        --label "org.opencontainers.image.source=$SOURCE" -t "$REGISTRY/$task:$VERSION" -f "$PKG/agent.Dockerfile" "$PKG"
    if [ "$PUSH" = "--push" ]; then
        $DOCKER push "$REGISTRY/$task:$VERSION"
    fi
done
