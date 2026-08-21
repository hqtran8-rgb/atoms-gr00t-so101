# Deployment architecture

## Policy-server / rollout-client split

Inference on the Jetson AGX Orin used **two separate Docker images**,
communicating over `127.0.0.1:5555` with host networking:

- **Policy server** — image `gr00t-orin:latest`, running upstream's
  `gr00t/eval/run_gr00t_server.py`, serving the fine-tuned policy over ZMQ.
- **SO-101 rollout client** — image `gr00t-so101-client:saved-20260730`.
  The Python rollout scripts in this repository
  (`run_policy_c_v2_rollout.py`, `run_policy_c_v2_pause_fix.py`,
  `run_policy_c_v2_recovery.py`) were executed through this client
  image/container during the documented deployment, and talk to the policy
  server via `gr00t.policy.server_client.PolicyClient`. **Do not assume
  these scripts ran directly on the Jetson host** — the recorded
  deployment ran them inside `gr00t-so101-client:saved-20260730`.

**The `gr00t-so101-client` Dockerfile/image definition is not included in
this archive.** Only the Python scripts that were run inside it are
preserved here. Reproducing the exact client container environment (base
image, installed `lerobot` version, camera/serial device passthrough
configuration, etc.) is therefore **incomplete from this repository
alone** — see [DEPENDENCIES.md](../DEPENDENCIES.md) for what is and isn't
known about that environment, and treat any local re-run of these scripts
as happening in a reconstructed environment, not a byte-identical one.

Client and server communicate over loopback: `host="127.0.0.1"`,
`port=5555` (see `POLICY_SERVER_HOST` / `POLICY_SERVER_PORT` in
`.env.example` if you need to run them on separate hosts).

## Transfer pipeline (Lambda → Jetson)

`transfer_policy_from_lambda.sh` rsyncs a finished deploy bundle
(`deploy/policy_C_v2_realonly/` — model config + weights, not included in
this repository) from the Lambda training host to the Jetson, verifies it
against a `SHA256SUMS` manifest, and atomically swaps it into the working
deploy directory. It requires `LAMBDA_SSH_HOST`, `LAMBDA_SSH_USER`,
`LAMBDA_SSH_KEY`, `LAMBDA_REMOTE_DEPLOY_PATH`, and `JETSON_WORK_DIR` — see
`.env.example`.

`run_policy_load_test.sh` then loads the transferred policy inside the
Docker container as a smoke test (`load_policy_no_motion.py`), reporting
load time and GPU memory usage without commanding the robot.

## Policy C v2 deployment metadata

The scripts in this repository were used to deploy and roll out
**Policy C v2**, specifically **checkpoint-3000**:

| Field | Value |
|---|---|
| Policy | `policy_C_v2_realonly` |
| Checkpoint | `checkpoint-3000` |
| Architecture | NVIDIA GR00T N1.7 (`Gr00tN1d7`) |
| Embodiment | `NEW_EMBODIMENT` |
| Robot | SO-101 |
| Cameras | front, wrist |
| State dimensions | 6 |
| Action dimensions | 6 |
| Action chunk | 16 |
| Internal model action horizon | 40 |
| Task | "pick up the green cylinder and place it in the black bowl on the left" |

This is a **separate experiment stage** from the Policy C v3 checkpoints
described in [RESULTS.md](RESULTS.md) — see that document for why the code
and the headline evaluation numbers in this project do not belong to the
same policy version.

## Safety

See [SAFETY.md](SAFETY.md) for the physical safety behavior built into the
rollout scripts (joint/gripper boundaries, torque handling, manual
controls).
