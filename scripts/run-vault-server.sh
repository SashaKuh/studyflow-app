#!/usr/bin/env bash
set -euo pipefail
app_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
subject_root="$(cd "$app_root/../.." && pwd)"
export STUDYFLOW_VAULT_PATH="$app_root/../studyflow-knowledge-base"
export PYTHONPATH="$app_root"
exec "$subject_root/.venv/bin/python" -m harness.vault_server
