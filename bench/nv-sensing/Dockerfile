# One image for the agent and the evaluator: Python and the pinned dependencies only.
# No task, solution, test or sample is baked in; they are mounted at run time (docs/containers.md):
#   agent:     a task repository at /work
#   evaluator: the source repository at /src (read-only), the agent's repositories at /agent (read-only)
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=/work
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
# simos imports tkinter on load, which needs the Tk runtime library
RUN apt-get update && apt-get install -y --no-install-recommends libtk8.6 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
CMD ["bash"]
