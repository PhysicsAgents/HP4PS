#!/bin/sh
# Start a detached agent container for one task repository; the agent then works with
#   docker exec -w /work NAME <command>      e.g. docker exec -w /work NAME python -c "..."
# The repository is mounted read-write at /work; the container has no network.
# usage: scripts/agent_container.sh TASK_REPO NAME [IMAGE]
set -eu
[ $# -ge 2 ] || { echo "usage: $0 TASK_REPO NAME [IMAGE]" >&2; exit 2; }
REPO=$(cd "$1" && pwd)
NAME=$2
IMAGE=${3:-nv-sensing:latest}
DOCKER=${DOCKER:-docker}
$DOCKER run -d --name "$NAME" --network none -v "$REPO":/work "$IMAGE" sleep infinity
