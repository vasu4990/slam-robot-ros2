#!/usr/bin/env bash
set -euo pipefail
NAME=${1:-gazebo_loop_square}
OUT=${2:-artifacts/bags/${NAME}}
mkdir -p "$(dirname "$OUT")"
exec ros2 bag record -o "$OUT" /scan /odom /ground_truth/odom /tf /tf_static /map /diagnostics /clock
