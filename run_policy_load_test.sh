#!/usr/bin/env bash
#
# Loads the finetuned policy inside the deployment container on the Jetson
# and reports GPU memory / load time, without sending any actions to the
# robot. Useful as a fast smoke test after a policy transfer.
#
# Configuration is read from environment variables (export them yourself,
# or copy .env.example to .env in the repo root and `source .env` before
# running this script).

set -uo pipefail

if [ -f "$(dirname "${BASH_SOURCE[0]}")/.env" ]; then
    # shellcheck disable=SC1091
    source "$(dirname "${BASH_SOURCE[0]}")/.env"
fi

: "${JETSON_WORK_DIR:?Set JETSON_WORK_DIR (local working directory on the Jetson)}"
: "${JETSON_HF_CACHE_DIR:?Set JETSON_HF_CACHE_DIR (Hugging Face cache directory on the Jetson)}"
: "${GR00T_DOCKER_IMAGE:=gr00t-orin:latest}"

REPO="$JETSON_WORK_DIR/repos/Isaac-GR00T"
DEPLOY="$JETSON_WORK_DIR/deploy/policy_C_v2_realonly"

STATUS="$JETSON_WORK_DIR/logs/policy_model_load.status"
LOCK="$JETSON_WORK_DIR/logs/policy_model_load.lock"

exec 9>"$LOCK"

if ! flock -n 9; then
    echo "Another policy model-load test is already running."
    exit 75
fi

rm -f "$STATUS"

sudo -n docker rm -f gr00t-policy-load-test >/dev/null 2>&1 || true

sudo -n docker run --rm \
  --name gr00t-policy-load-test \
  --runtime nvidia \
  --gpus all \
  --ipc=host \
  --network host \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -e HF_HOME=/root/.cache/huggingface \
  -e HF_HUB_OFFLINE=1 \
  -e TRANSFORMERS_OFFLINE=1 \
  -v "$JETSON_HF_CACHE_DIR:/root/.cache/huggingface:ro" \
  -v "$REPO:/workspace:ro" \
  -v "$DEPLOY:/policy:ro" \
  -v "$JETSON_WORK_DIR/load_policy_no_motion.py:/tmp/load_policy_no_motion.py:ro" \
  -w /workspace \
  "$GR00T_DOCKER_IMAGE" \
  python -u /tmp/load_policy_no_motion.py

RESULT=$?
echo "$RESULT" > "$STATUS"
exit "$RESULT"
