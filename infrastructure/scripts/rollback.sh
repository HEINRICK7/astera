#!/usr/bin/env bash
set -euo pipefail

: "${HELM_RELEASE:?HELM_RELEASE is required}"
: "${HELM_NAMESPACE:?HELM_NAMESPACE is required}"
: "${HELM_REVISION:?HELM_REVISION is required}"

helm rollback "${HELM_RELEASE}" "${HELM_REVISION}" \
  --namespace "${HELM_NAMESPACE}" \
  --wait \
  --timeout 10m
