# ATOMS — SO-101 + NVIDIA Isaac-GR00T N1.7

Configuration, deployment, rollout, and evaluation documentation from an
ATOMS project that fine-tuned
[NVIDIA Isaac-GR00T N1.7](https://github.com/NVIDIA/Isaac-GR00T) for an
SO-101 robotic arm.

This repository includes the Policy C v2 modality configuration and
deployment/rollout scripts. **It does not include the Policy C v3
fine-tuning/evaluation implementation** — that code is not present in this
archive at all. See "Two separate experiment stages" below and
[docs/RESULTS.md](docs/RESULTS.md).

- **Hardware:** SO-101 follower arm, front + wrist cameras
- **Fine-tuning:** performed on a Lambda Cloud GPU instance
- **Inference:** two separate Docker images on a Jetson AGX Orin — a
  policy-server container (`gr00t-orin:latest`) and a separate SO-101
  rollout-client container (`gr00t-so101-client:saved-20260730`) —
  communicating over `127.0.0.1:5555` with host networking. See
  [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for details, including what is
  and isn't reproducible from this archive.

## Attribution

This project is built on top of **NVIDIA Isaac-GR00T**
(https://github.com/NVIDIA/Isaac-GR00T, Apache License 2.0), pinned to
commit `23ace64f17aa5015259b8609d371eb61a357c776` ("GR00T N1.7 Release").

**NVIDIA's source code is not vendored in this repository.** To reproduce
this work, clone the upstream repository yourself at the pinned commit —
see [DEPENDENCIES.md](DEPENDENCIES.md). Everything in this repository is
original code written against `gr00t`'s public Python interfaces.

**Model weights and training/demonstration datasets are not included in
this repository.** Only source code and documentation are published here.
See [NOTICE.md](NOTICE.md) for full attribution details and
[LICENSE-TODO.md](LICENSE-TODO.md) for this repository's own (currently
unresolved) licensing status.

## Two separate experiment stages — read this before the results

This repository's code and its most notable quantitative results **belong
to two different policy versions** and should not be conflated:

- The rollout/deployment scripts in this repository
  (`run_policy_c_v2_rollout.py`, `run_policy_c_v2_pause_fix.py`,
  `run_policy_c_v2_recovery.py`, `load_policy_no_motion.py`) were built for
  and used to deploy **Policy C v2** (`checkpoint-3000`).
- The headline evaluation numbers referenced for this project — checkpoint
  9000 (MSE 14.80, MAE 2.309) and checkpoint 10000 (MSE 16.92, MAE
  2.332) — belong to **Policy C v3**, trained on a separate
  150-demonstration dataset (`policy_c_v3_150`).
- **The training and evaluation code for Policy C v3 is not present in
  this archive.** Only the numeric results are known. Do not present the
  Policy C v2 code in this repository as the code that produced the Policy
  C v3 numbers.

See [docs/RESULTS.md](docs/RESULTS.md) for the full breakdown of both
stages.

## Physical performance — read before assuming this works reliably

**This project does not demonstrate reliable physical task completion.**
Real-robot testing on the SO-101 arm surfaced limitations across the full
pipeline:

- Camera visibility was not consistently reliable
- Grasping did not reliably succeed
- Lifting did not consistently follow a successful grasp
- Positioning over the target was not reliable
- Release timing/placement was inconsistent

See [docs/RESULTS.md](docs/RESULTS.md) for details. Treat this as a
research/engineering artifact documenting a deployment pipeline and a
fine-tuning experiment, not as a demonstration of a working autonomous
pick-and-place system.

## Repository layout

```
.
├── config/
│   └── so101_policy_c_v2_config.py   # SO-101 modality config (Policy C v2)
├── load_policy_no_motion.py          # no-motion model-load smoke test
├── run_policy_c_v2_rollout.py        # main closed-loop rollout
├── run_policy_c_v2_pause_fix.py      # rollout with live pause/resume hotkeys
├── run_policy_c_v2_recovery.py       # recovery-mode rollout variant
├── run_policy_load_test.sh           # runs load_policy_no_motion.py in the deploy container
├── transfer_policy_from_lambda.sh    # rsync + checksum-verified transfer, Lambda -> Jetson
├── .env.example                      # required environment variables (copy to .env)
├── docs/
│   ├── SETUP.md                      # environments, install, hardware
│   ├── DEPLOYMENT.md                 # policy-server/rollout-client architecture
│   ├── RESULTS.md                    # Policy C v2 vs v3, honest limitations
│   └── SAFETY.md                     # joint/gripper boundaries, torque handling
├── DEPENDENCIES.md                   # gr00t / lerobot / docker version notes
├── NOTICE.md                         # NVIDIA Isaac-GR00T attribution
└── LICENSE-TODO.md                   # licensing status (unresolved — see file)
```

## Getting started

1. Read [DEPENDENCIES.md](DEPENDENCIES.md) and install upstream Isaac-GR00T
   at the pinned commit.
2. Read [docs/SETUP.md](docs/SETUP.md) for the Lambda/Jetson environment
   split and hardware requirements.
3. Copy `.env.example` to `.env` and fill in your own Lambda/Jetson
   connection details — no real hosts, usernames, or key paths are
   committed to this repository.
4. Read [docs/SAFETY.md](docs/SAFETY.md) before running any rollout script
   against a physical arm.
5. Read [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for how the policy-server
   and rollout-client containers fit together.

## Authorship and Project Context

ATOMS was developed as a team capstone project at Arizona State
University. The GR00T workflow documented in this repository—including
data preparation, policy configuration and fine-tuning, checkpoint
evaluation, Lambda-to-Jetson transfer, Dockerized inference deployment,
rollout scripting, and physical debugging—was implemented by Hung Tran.

The broader ATOMS team included Daniel Grosjean, Muhamed Rai, and Aarthak
Jindal. Their inclusion here acknowledges the shared capstone project
context and does not imply authorship of the code in this repository.

No project sponsor is identified here, since none is documented in the
source material this repository was built from. This repository does not
claim ownership of NVIDIA Isaac-GR00T or any other upstream dependency —
see [NOTICE.md](NOTICE.md) for that attribution.
