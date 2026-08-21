# Safety

This document describes the physical-safety behavior that is actually
implemented in the rollout scripts in this repository — it is not a
general robot-safety policy, only a record of what the code does.

## Startup checks

All three rollout scripts (`run_policy_c_v2_rollout.py`,
`run_policy_c_v2_pause_fix.py`, `run_policy_c_v2_recovery.py`) require the
arm to be within a validated joint-angle window before torque is enabled
or before the rollout begins (`validate_start`, checked against
`START_RANGES`):

| Joint | Safe start range (deg) |
|---|---|
| shoulder_pan | -20.0 to 35.0 |
| shoulder_lift | -70.0 to -25.0 |
| elbow_flex | 20.0 to 80.0 |
| wrist_flex | 35.0 to 80.0 |
| wrist_roll | -20.0 to 20.0 |
| gripper | 0.0 to 45.0 |

Operators are prompted to place a padded support under the arm before
connecting, and to remove it only after the script confirms the arm is
holding its starting pose under torque.

## During rollout

- `max_relative_target=4.0` on `SO101FollowerConfig` limits how large a
  single commanded joint move can be, bounding worst-case jump distance
  per control step.
- `validate_position` is checked after every physical action and raises
  (stopping the rollout) if any of the first five joints leaves a
  ±88–92° soft boundary (script-dependent) or the gripper leaves
  approximately -2° to 102°.
- Control period is fixed (0.12s) rather than running open-loop as fast as
  possible.
- `run_policy_c_v2_pause_fix.py` additionally supports live hotkeys during
  a rollout: `p` to pause (holds current pose), `o` to manually open the
  gripper in small steps while paused, `r` to resume with a fresh
  observation, `q` to stop.

## Shutdown

- `disable_torque_on_disconnect=True` is set on the robot config in every
  script, so torque is dropped whenever the connection is closed.
- All three scripts wrap the rollout in `try/except/finally` so that
  `Ctrl+C`, a validation failure, or any other exception triggers a
  disconnect (and torque disable) before the script exits.
- `run_policy_c_v2_rollout.py` additionally catches a failed disconnect
  itself and prints an explicit instruction to turn off the follower arm's
  power manually — treat that message as an actionable warning, not a log
  line, if you ever see it.

## What this does *not* cover

These are software-level safeguards only. They assume the physical
workspace has already been cleared of obstacles/cables and that a human
operator is present and able to cut power manually. See
[RESULTS.md](RESULTS.md) for the physical task-completion limitations
observed during testing — the safety boundaries above bound the *range* of
motion, they do not guarantee the *task* is performed correctly.
