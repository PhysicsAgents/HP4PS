# NV sensing measurement tasks

English | [中文](README.zh.md)

Each task is an independent repository (`tasks/<task>/`); complete `solutions/<task>/__init__.py` according to its README.
Scoring is done by the evaluator: first compare with the reference level, then run once more on hidden samples with different parameters. Passing both gives 1 point, and the measurement precision actually measured in each condition is recorded.

| Task | Content |
|---|---|
| nuclear_entangled_phase | Measuring a phase with two nuclear spins |
| two_nv_correlation | Shot-by-shot correlation of two NVs |
| correlated_noise_sensitivity | Detecting spatially correlated magnetic noise |
| dark_spin_detection | Detecting a single dark spin |
| ac_field_echo | Measuring an AC magnetic field with a single NV |
| lockin_readout_gain | Readout gain in continuous-sampling measurement |
| charge_init_readout | Charge initialization and spin readout |
| field_tracking | Tracking a time-varying magnetic field |

## Containers

Published agent images, with the task repository at `/work`:

```
docker run -it --name <container> --network none ghcr.io/physicsagents/hp4ps/<task>:1.0.0
docker cp <container>:/work/solutions/<task> <dir handed to the evaluator>/<task>/solutions/<task>
```

## Building from source

This directory is the build context:

```
scripts/build_images.sh . 1.0.0                         # dependency image + one agent image per task
```

Or build only the dependency image and mount the task repository into it:

```
docker build -t nv-sensing:latest .
scripts/agent_container.sh tasks/<task> <container>       # task repository mounted at /work, no network
docker exec -w /work <container> python ...
```
