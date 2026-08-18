#!/usr/bin/env bash
set -euo pipefail
BAG=${1:?usage: replay_benchmark.sh BAG_DIR [RATE]}
RATE=${2:-1.0}
exec ros2 bag play "$BAG" --clock --rate "$RATE"
