#!/usr/bin/env sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
"$ROOT/scripts/run_sv_tests.sh"
"$ROOT/scripts/run_ai_demo.sh"
