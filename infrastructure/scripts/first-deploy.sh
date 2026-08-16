#!/usr/bin/env bash
set -euo pipefail

: "${HELM_RELEASE:?HELM_RELEASE is required}"
: "${HELM_NAMESPACE:?HELM_NAMESPACE is required}"
: "${ASTERA_IMAGE_TAG:?ASTERA_IMAGE_TAG is required}"

helm upgrade --install "${HELM_RELEASE}" infrastructure/helm/astera \
  --namespace "${HELM_NAMESPACE}" \
  --create-namespace \
  --set "image.tag=${ASTERA_IMAGE_TAG}" \
  --atomic \
  --wait \
  --timeout 10m

kubectl -n "${HELM_NAMESPACE}" rollout status \
  "deployment/${HELM_RELEASE}" \
  --timeout=10m

kubectl -n "${HELM_NAMESPACE}" get service "${HELM_RELEASE}"
