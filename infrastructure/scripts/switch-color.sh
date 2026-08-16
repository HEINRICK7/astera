#!/usr/bin/env bash
set -euo pipefail

: "${TARGET_COLOR:?TARGET_COLOR is required}"
: "${KUBE_NAMESPACE:?KUBE_NAMESPACE is required}"

case "${TARGET_COLOR}" in
  blue|green) ;;
  *) echo "TARGET_COLOR must be blue or green" >&2; exit 2 ;;
esac

kubectl -n "${KUBE_NAMESPACE}" patch service astera-runtime \
  --type merge \
  --patch "{\"spec\":{\"selector\":{\"app.kubernetes.io/name\":\"astera-runtime\",\"astera.io/color\":\"${TARGET_COLOR}\"}}}"
