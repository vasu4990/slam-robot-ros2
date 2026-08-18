#!/usr/bin/env bash
set -euo pipefail
TRAJ=${1:-artifacts/trajectory.csv}
MAP=${2:-artifacts/map.pgm}
mkdir -p artifacts
python tools/trajectory_metrics.py "$TRAJ" --output artifacts/trajectory-metrics.json
python tools/loop_closure_metrics.py "$TRAJ" --output artifacts/loop-metrics.json
if [[ -f "$MAP" ]]; then python tools/map_metrics.py "$MAP" --output artifacts/map-metrics.json; fi
ARGS=(--trajectory artifacts/trajectory-metrics.json --loop artifacts/loop-metrics.json --output artifacts/benchmark-gate.json)
[[ -f artifacts/map-metrics.json ]] && ARGS+=(--map artifacts/map-metrics.json)
python tools/benchmark_gate.py "${ARGS[@]}"
