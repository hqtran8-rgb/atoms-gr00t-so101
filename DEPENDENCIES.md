# Dependencies

This repository contains only the ATOMS-authored scripts. It depends on the
upstream `gr00t` package and the `lerobot` package, neither of which is
vendored here.

## NVIDIA Isaac-GR00T (`gr00t`)

Clone and install the upstream repository at the pinned commit:

```bash
git clone https://github.com/NVIDIA/Isaac-GR00T.git
cd Isaac-GR00T
git checkout 23ace64f17aa5015259b8609d371eb61a357c776
uv sync --all-extras   # or: pip install -e .
```

Version pins observed in the upstream repo at that commit (see its own
`pyproject.toml` / `scripts/deployment/orin/pyproject.toml` for the
authoritative, platform-specific list):

| Package | dGPU (x86_64) | Jetson Orin (aarch64, JetPack 6.2) |
|---|---|---|
| Python | 3.10.* | 3.10.* |
| torch | 2.7.1 | 2.10.0 |
| torchvision | 0.22.1 | 0.25.0 |
| transformers | 4.57.3 | 4.57.6 |
| CUDA | 12.8 | 12.6 |

## LeRobot (`lerobot`)

The rollout scripts (`run_policy_c_v2_rollout.py`,
`run_policy_c_v2_pause_fix.py`, `run_policy_c_v2_recovery.py`) import
`lerobot.robots.so101_follower` and `lerobot.cameras.opencv` from Hugging
Face's [LeRobot](https://github.com/huggingface/lerobot) package.

**Reproducibility gap:** the exact `lerobot` version used during
deployment is not recorded anywhere in the source archive this repository
was cleaned from. Before relying on these scripts, install a current
`lerobot` release that provides the SO-101 follower robot class and pin the
exact version you used by running `pip show lerobot` in your working
environment and recording it here.

## Docker (Jetson Orin inference)

`run_policy_load_test.sh` runs against a container image built from
upstream's `scripts/deployment/orin/Dockerfile` (not included in this
repository — build it from the cloned upstream repo). The image is
referenced here only by tag (`GR00T_DOCKER_IMAGE`, default
`gr00t-orin:latest` — see `.env.example`).

## Robot hardware

- SO-101 follower arm (via `lerobot.robots.so101_follower`)
- Two USB/OpenCV-compatible cameras: front and wrist ("hand-eye"), 640x480 @ 30fps
