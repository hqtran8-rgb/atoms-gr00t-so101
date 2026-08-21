# Results

This project has **two separate experiment stages**. The code in this
repository belongs to the first stage; the headline quantitative numbers
below belong to the second. **They are not the same policy checkpoint,**
and the second stage's training/evaluation code is not included here.

## Stage 1 — Policy C v2 (code included in this repository)

`checkpoint-3000` of Policy C v2 was deployed to the Jetson AGX Orin and
driven via the rollout scripts in this repository
(`run_policy_c_v2_rollout.py`, `run_policy_c_v2_pause_fix.py`,
`run_policy_c_v2_recovery.py`) against the physical SO-101 arm. See
[DEPLOYMENT.md](DEPLOYMENT.md) for its configuration.

**No formal quantitative evaluation metrics (MSE/MAE or task success rate)
for Policy C v2 / checkpoint-3000 were present in the source archive this
repository was built from.** What exists is deployment metadata only
(architecture, dimensions, task string) and the rollout scripts themselves.
If such metrics exist elsewhere, add them here with their source.

## Stage 2 — Policy C v3 (code NOT included in this repository)

Policy C v3 was trained on a separate 150-demonstration dataset
(`policy_c_v3_150`). Two checkpoints exist on the Jetson but were
**intentionally excluded** from this archive (weights are never
republished — see [NOTICE.md](../NOTICE.md)):

| Checkpoint | MSE | MAE |
|---|---|---|
| 9000 | 14.80 | 2.309 |
| 10000 | 16.92 | 2.332 |

Checkpoint 9000 had the **lowest offline error** of the two (both MSE and
MAE). Checkpoint 10000 was the **highest available training step** but
scored **slightly worse offline** than checkpoint 9000 — more training
steps did not translate into a lower validation error here. **Offline
MSE/MAE measure action-prediction error against a held-out validation set;
they do not by themselves prove successful real-world task completion** —
see the qualitative section below for what physical testing actually
showed.

**The training and evaluation code that produced these numbers is not
present in this archive.** Only the numeric results and the dataset name
are known. Do not treat `run_policy_c_v2_*.py` in this repository as the
code that produced these Policy C v3 metrics — those scripts predate v3
and were written against Policy C v2's checkpoint and config. If the v3
training/eval scripts are recovered later, they belong in a clearly
separate `policy_c_v3/` location with their own documentation, not merged
into the v2 rollout scripts.

## Qualitative physical evaluation — read before drawing conclusions

**Do not treat any of the above as evidence of reliable physical task
completion.** Real-robot testing on the SO-101 arm surfaced the following
limitations, and none of them are resolved by the MSE/MAE numbers above
(which measure action-prediction error against a validation set, not
end-to-end task success):

- **Camera visibility** — the model's ability to correctly perceive the
  scene was not consistently reliable across trials.
- **Grasping** — the policy did not reliably close the gripper on the
  target object.
- **Lifting** — successful grasps did not consistently translate into a
  stable lift.
- **Positioning** — the arm did not reliably position the object over the
  target bowl.
- **Release** — release timing/placement was not consistently accurate
  even when the preceding steps succeeded.

Any public-facing description of this project (README, portfolio writeup,
demo video captions) should reflect these limitations rather than imply a
working end-to-end pick-and-place system.
