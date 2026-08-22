#!/usr/bin/env bash
#
# Provision object storage for THIS project against a single, SHARED local MinIO.
# Creates TWO buckets: public (anonymous read) and private (app-user only).
#
# Usage: ./scripts/ensure_minio.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

if [ -f "$REPO_ROOT/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    . "$REPO_ROOT/.env"
    set +a
fi

# --- Configuration -------------------------------------------------------
CONTAINER_NAME="${MINIO_CONTAINER_NAME:-minio}"
IMAGE="${MINIO_IMAGE:-minio/minio:latest}"
MC_IMAGE="${MINIO_MC_IMAGE:-minio/mc:latest}"
VOLUME_NAME="${MINIO_VOLUME_NAME:-minio-data}"

MINIO_ROOT_USER="${MINIO_ROOT_USER:-minioadmin}"
MINIO_ROOT_PASSWORD="${MINIO_ROOT_PASSWORD:-minioadmin}"
MINIO_PORT="${MINIO_PORT:-9000}"
MINIO_CONSOLE_PORT="${MINIO_CONSOLE_PORT:-9001}"
MINIO_WAIT_TIMEOUT="${MINIO_WAIT_TIMEOUT:-60}"

PUBLIC_BUCKET="${MINIO_PUBLIC_BUCKET:?MINIO_PUBLIC_BUCKET is required}"
PRIVATE_BUCKET="${MINIO_PRIVATE_BUCKET:?MINIO_PRIVATE_BUCKET is required}"
APP_USER="${MINIO_APP_USER:?MINIO_APP_USER is required}"
APP_PASSWORD="${MINIO_APP_PASSWORD:?MINIO_APP_PASSWORD is required}"
POLICY_NAME="${APP_USER}-policy"

if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: docker is required but not found on PATH." >&2
    exit 1
fi

# --- 1. Ensure MinIO container is running --------------------------------
if docker inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    state="$(docker inspect -f '{{.State.Status}}' "$CONTAINER_NAME")"
    if [ "$state" = "running" ]; then
        echo "MinIO container '$CONTAINER_NAME' already running — reusing it."
    else
        echo "MinIO container '$CONTAINER_NAME' exists ($state) — starting..."
        docker start "$CONTAINER_NAME" >/dev/null
    fi
else
    echo "Creating MinIO container '$CONTAINER_NAME'..."
    docker volume create "$VOLUME_NAME" >/dev/null 2>&1 || true
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p "${MINIO_PORT}:9000" \
        -p "${MINIO_CONSOLE_PORT}:9001" \
        -e "MINIO_ROOT_USER=${MINIO_ROOT_USER}" \
        -e "MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}" \
        -v "${VOLUME_NAME}:/data" \
        --restart unless-stopped \
        "$IMAGE" server /data --console-address ":9001" >/dev/null
    echo "MinIO started:"
    echo "  API:     http://localhost:${MINIO_PORT}"
    echo "  Console: http://localhost:${MINIO_CONSOLE_PORT}"
fi

# --- 2. Create buckets + app user + policies -----------------------------
echo "Provisioning buckets '$PUBLIC_BUCKET' (public) and '$PRIVATE_BUCKET' (private)..."

render_policy() {
    local file="$1" bucket="$2" content
    [ -f "$file" ] || return 0
    content="$(cat "$file")"
    printf '%s' "${content//bucket_name/$bucket}"
}

PUBLIC_READ_POLICY="$(render_policy "$REPO_ROOT/minio/policies/bucket-public-read.json" "$PUBLIC_BUCKET")"

docker run --rm \
    --add-host=host.docker.internal:host-gateway \
    -e "MINIO_HOST=http://host.docker.internal:${MINIO_PORT}" \
    -e "MINIO_ROOT_USER=${MINIO_ROOT_USER}" \
    -e "MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}" \
    -e "PUBLIC_BUCKET=${PUBLIC_BUCKET}" \
    -e "PRIVATE_BUCKET=${PRIVATE_BUCKET}" \
    -e "APP_USER=${APP_USER}" \
    -e "APP_PASSWORD=${APP_PASSWORD}" \
    -e "POLICY_NAME=${POLICY_NAME}" \
    -e "PUBLIC_READ_POLICY=${PUBLIC_READ_POLICY}" \
    -e "CONTAINER_NAME=${CONTAINER_NAME}" \
    -e "WAIT_TIMEOUT=${MINIO_WAIT_TIMEOUT}" \
    --entrypoint sh \
    "$MC_IMAGE" -c '
set -e
echo "  Waiting for MinIO at $MINIO_HOST (timeout: ${WAIT_TIMEOUT}s) ..."
waited=0
until mc alias set local "$MINIO_HOST" "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null 2>&1; do
    waited=$((waited + 1))
    if [ "$waited" -ge "$WAIT_TIMEOUT" ]; then
        echo "ERROR: MinIO did not respond at $MINIO_HOST within ${WAIT_TIMEOUT}s." >&2
        exit 1
    fi
    sleep 1
done

echo "  Ensuring bucket $PUBLIC_BUCKET (public) ..."
mc mb --ignore-existing "local/$PUBLIC_BUCKET"
if [ -n "$PUBLIC_READ_POLICY" ]; then
    printf "%s" "$PUBLIC_READ_POLICY" > /tmp/public-read.json
    mc anonymous set-json /tmp/public-read.json "local/$PUBLIC_BUCKET"
fi

echo "  Ensuring bucket $PRIVATE_BUCKET (private) ..."
mc mb --ignore-existing "local/$PRIVATE_BUCKET"
mc anonymous set none "local/$PRIVATE_BUCKET" || true

echo "  Ensuring app user $APP_USER ..."
mc admin user add local "$APP_USER" "$APP_PASSWORD" 2>/dev/null || true

echo "  Creating combined policy for both buckets ..."
cat > /tmp/user-combined.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucketMultipartUploads",
        "s3:ListMultipartUploadParts",
        "s3:PutObject",
        "s3:AbortMultipartUpload",
        "s3:DeleteObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::$PUBLIC_BUCKET",
        "arn:aws:s3:::$PUBLIC_BUCKET/*",
        "arn:aws:s3:::$PRIVATE_BUCKET",
        "arn:aws:s3:::$PRIVATE_BUCKET/*"
      ]
    }
  ]
}
EOF

mc admin policy create local "$POLICY_NAME" /tmp/user-combined.json 2>/dev/null || \
    mc admin policy update local "$POLICY_NAME" /tmp/user-combined.json
mc admin policy attach local "$POLICY_NAME" --user "$APP_USER" 2>/dev/null || true
'

echo ""
echo "Done."
echo "  Public bucket:  $PUBLIC_BUCKET  (anonymous read)"
echo "  Private bucket: $PRIVATE_BUCKET (app-user only)"
echo "  App user:       $APP_USER"
echo "  Console:        http://localhost:${MINIO_CONSOLE_PORT}  (root: ${MINIO_ROOT_USER}/${MINIO_ROOT_PASSWORD})"
echo "  Endpoint:       http://localhost:${MINIO_PORT}  (containers: http://host.docker.internal:${MINIO_PORT})"