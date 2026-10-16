# Agent image of one task: the dependency image (Dockerfile) with the task repository at /work.
# Build context: a package directory (scripts/build_package.py), which carries this file; see
# scripts/build_images.sh there.
ARG BASE=nv-sensing:latest
FROM ${BASE}
ARG TASK
COPY tasks/${TASK} /work
CMD ["bash"]
