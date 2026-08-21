# Setup

This project has two separate compute environments: a Lambda GPU instance
used for fine-tuning, and a Jetson AGX Orin used for on-robot inference.
Neither environment is captured as an image/container export in this
repository — the steps below describe how to reconstruct them.

## 1. Upstream install

On both machines, install NVIDIA Isaac-GR00T at the pinned commit — see
[DEPENDENCIES.md](../DEPENDENCIES.md) for exact commands and version pins.

## 2. Fine-tuning environment (Lambda)

- Fine-tuning was run on a Lambda Cloud GPU instance.
- Entry point: upstream's `examples/finetune.sh` /
  `gr00t/experiment/launch_finetune.py`, using the SO-101 modality
  configuration in [`config/so101_policy_c_v2_config.py`](../config/so101_policy_c_v2_config.py)
  registered under `EmbodimentTag.NEW_EMBODIMENT`.
- Base model: `GR00T-N1.7-3B`.
- The exact dataset paths and output directories used on Lambda are
  intentionally **not** included here (they contained this project's local
  username and directory layout) — see [DEPLOYMENT.md](DEPLOYMENT.md) for
  what deployment metadata *is* preserved.

## 3. Jetson AGX Orin environment (inference)

- Platform: Jetson AGX Orin, JetPack 6.2, CUDA 12.6.
- Isaac-GR00T is installed inside a Docker image built from upstream's
  `scripts/deployment/orin/Dockerfile`, tagged `gr00t-orin:latest` by
  default (configurable — see `.env.example`).
- `run_policy_load_test.sh` is a smoke test that loads the policy inside
  that container without sending any actions to the robot.

## 4. Hardware

- SO-101 follower arm, connected via serial (see `SO101FollowerConfig.port`
  in the rollout scripts — this is a local device path you'll need to set
  for your own machine, e.g. `/dev/ttyACM*`).
- Two cameras (front, wrist/hand-eye), OpenCV-compatible, 640x480 @ 30fps.
  Device paths in the rollout scripts (`/dev/video_front`,
  `/dev/video_handeye`) assume udev rules that create stable symlinks for
  these two cameras — set up equivalent rules for your machine, or replace
  them with the raw `/dev/videoN` indices.

## 5. Configuration

Copy `.env.example` to `.env` in the repository root and fill in your own
Lambda host/user/key and Jetson working directory before running
`transfer_policy_from_lambda.sh` or `run_policy_load_test.sh`. See
[DEPENDENCIES.md](../DEPENDENCIES.md) for the `lerobot` reproducibility gap.
