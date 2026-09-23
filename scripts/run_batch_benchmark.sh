#!/usr/bin/env sh
set -eu
MAX_PER_CLASS="${1:-25}"
python python/run_batch_benchmark.py --max-per-class "$MAX_PER_CLASS"
