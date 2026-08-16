#!/usr/bin/env bash
set -euo pipefail

base_url="${PARAKEET_HTTP_URL:-http://localhost:9000}"
base_url="${base_url%/}"

if ! command -v curl >/dev/null 2>&1; then
  echo "ERRO: curl é necessário para o readiness check." >&2
  exit 2
fi

echo "Parakeet HTTP endpoint: ${base_url}"
echo "Required: /v1/health/ready"
curl --fail-with-body --silent --show-error "${base_url}/v1/health/ready"
printf '\nRequired: /v1/models\n'
curl --fail-with-body --silent --show-error "${base_url}/v1/models"
printf '\nOptional: /v1/version\n'
curl --silent --show-error "${base_url}/v1/version" || echo "unavailable"
printf '\nOptional: /v1/metadata\n'
curl --silent --show-error "${base_url}/v1/metadata" || echo "unavailable"
printf '\nOptional: /v1/metrics\n'
curl --silent --show-error "${base_url}/v1/metrics" || echo "unavailable"
printf '\nReadiness: PASS\n'
