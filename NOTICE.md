# Notice

This file documents attribution for upstream, third-party dependencies.
It does not describe authorship of the code in this repository — for that,
and for this project's ATOMS/Arizona State University team context, see
the "Authorship and Project Context" section of [README.md](README.md).

This project builds on [NVIDIA Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T),
licensed under the Apache License, Version 2.0
(https://www.apache.org/licenses/LICENSE-2.0).

- Upstream project: https://github.com/NVIDIA/Isaac-GR00T
- Pinned commit used for this work: `23ace64f17aa5015259b8609d371eb61a357c776`
  ("GR00T N1.7 Release")

**No NVIDIA source code is vendored in this repository.** The scripts here
are original code written against the upstream `gr00t` Python package's
public interfaces (`gr00t.policy.gr00t_policy.Gr00tPolicy`,
`gr00t.policy.server_client.PolicyClient`,
`gr00t.eval.real_robot.SO100.eval_so100.So100Adapter`,
`gr00t.configs.data.embodiment_configs.register_modality_config`, etc.).
To reproduce this work you need to separately clone the upstream repository
at the pinned commit and install it per its own `LICENSE`, `ATTRIBUTIONS.md`,
and `CONTRIBUTING.md`.

This repository also does not include NVIDIA's `ATTRIBUTIONS.md`
(third-party notices for the upstream package's own dependencies) — refer to
the upstream repository directly for that file.

See [LICENSE-TODO.md](LICENSE-TODO.md) for the licensing status of the
original code in this repository.
