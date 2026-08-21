import runpy
import time

import torch

print("=== GR00T N1.7 no-motion model-load test ===", flush=True)
print("Torch:", torch.__version__, flush=True)
print("CUDA available:", torch.cuda.is_available(), flush=True)

if not torch.cuda.is_available():
    raise RuntimeError("CUDA is unavailable inside the container")

print("GPU:", torch.cuda.get_device_name(0), flush=True)

free_before, total = torch.cuda.mem_get_info()
print(f"GPU memory before: {free_before / 1024**3:.2f} GiB free / "
      f"{total / 1024**3:.2f} GiB total", flush=True)

print("\nRegistering custom SO-101 modality configuration...", flush=True)
runpy.run_path("/policy/config/so101_policy_c_v2_config.py")
print("Custom modality registration: PASSED", flush=True)

from gr00t.data.embodiment_tags import EmbodimentTag
from gr00t.policy.gr00t_policy import Gr00tPolicy

print("\nLoading fine-tuned policy weights...", flush=True)
start = time.monotonic()

policy = Gr00tPolicy(
    embodiment_tag=EmbodimentTag.NEW_EMBODIMENT,
    model_path="/policy/model",
    device="cuda",
    strict=True,
)

torch.cuda.synchronize()
elapsed = time.monotonic() - start

free_after, total = torch.cuda.mem_get_info()
allocated = torch.cuda.memory_allocated()
reserved = torch.cuda.memory_reserved()

print("\n=== Model-load results ===", flush=True)
print(f"Load time: {elapsed:.1f} seconds", flush=True)
print(f"GPU memory after: {free_after / 1024**3:.2f} GiB free", flush=True)
print(f"Torch allocated: {allocated / 1024**3:.2f} GiB", flush=True)
print(f"Torch reserved: {reserved / 1024**3:.2f} GiB", flush=True)
print("Policy class:", type(policy).__name__, flush=True)
print("Embodiment: NEW_EMBODIMENT", flush=True)

print("\nMODEL LOAD TEST: PASSED", flush=True)
print("No observations were submitted and no actions were generated.", flush=True)
