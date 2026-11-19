#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
agy plugin install .
echo "[OK] ai-ops-starter installed! Please restart or open a new Antigravity window."
