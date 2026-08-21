#!/usr/bin/env bash
#
# Rsyncs a finetuned policy deploy bundle from the Lambda training host to
# the Jetson, verifies it against SHA256SUMS, then atomically swaps it into
# place.
#
# Configuration is read from environment variables (export them yourself,
# or copy .env.example to .env in the repo root and `source .env` before
# running this script). No host, user, key path, or local mount point is
# hardcoded here — see .env.example for the variables this script requires.

set -uo pipefail

if [ -f "$(dirname "${BASH_SOURCE[0]}")/.env" ]; then
    # shellcheck disable=SC1091
    source "$(dirname "${BASH_SOURCE[0]}")/.env"
fi

: "${LAMBDA_SSH_HOST:?Set LAMBDA_SSH_HOST (Lambda instance address) in your environment or .env}"
: "${LAMBDA_SSH_USER:?Set LAMBDA_SSH_USER (SSH username on the Lambda instance)}"
: "${LAMBDA_SSH_KEY:?Set LAMBDA_SSH_KEY (path to your SSH private key)}"
: "${LAMBDA_REMOTE_DEPLOY_PATH:?Set LAMBDA_REMOTE_DEPLOY_PATH (deploy bundle path on the Lambda instance)}"
: "${JETSON_WORK_DIR:?Set JETSON_WORK_DIR (local working directory on the Jetson)}"

REMOTE_DEPLOY="$LAMBDA_REMOTE_DEPLOY_PATH"
LOCAL_TMP="$JETSON_WORK_DIR/deploy/policy_C_v2_realonly.tmp"
LOCAL_DEPLOY="$JETSON_WORK_DIR/deploy/policy_C_v2_realonly"
STATUS="$JETSON_WORK_DIR/logs/policy_transfer.status"

rm -f "$STATUS"
mkdir -p "$LOCAL_TMP" "$JETSON_WORK_DIR/logs"

rsync -a \
  --partial \
  --partial-dir=.rsync-partial \
  --info=progress2,stats2 \
  -e "ssh -i $LAMBDA_SSH_KEY -o IdentitiesOnly=yes" \
  "${LAMBDA_SSH_USER}@${LAMBDA_SSH_HOST}:${REMOTE_DEPLOY}/" \
  "$LOCAL_TMP/"

RESULT=$?

if [ "$RESULT" -ne 0 ]; then
    echo "$RESULT" > "$STATUS"
    exit "$RESULT"
fi

cd "$LOCAL_TMP" || {
    echo 20 > "$STATUS"
    exit 20
}

sha256sum -c SHA256SUMS
RESULT=$?

if [ "$RESULT" -ne 0 ]; then
    echo "$RESULT" > "$STATUS"
    exit "$RESULT"
fi

if [ -e "$LOCAL_DEPLOY" ]; then
    rm -rf "$LOCAL_DEPLOY"
fi

mv "$LOCAL_TMP" "$LOCAL_DEPLOY"
RESULT=$?

echo "$RESULT" > "$STATUS"
exit "$RESULT"
