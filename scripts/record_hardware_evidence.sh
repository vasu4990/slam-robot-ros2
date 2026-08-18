#!/usr/bin/env bash
set -euo pipefail
: "${ROBOT_ID:?Set ROBOT_ID before recording physical evidence}"
: "${OPERATOR:?Set OPERATOR before recording physical evidence}"
: "${ENVIRONMENT:?Set ENVIRONMENT before recording physical evidence}"
RUN_ID=${1:-$(date +%Y%m%d_%H%M%S)}
ROOT=${2:-artifacts/hardware_runs}
OUT="$ROOT/$RUN_ID"
mkdir -p "$OUT"

bash scripts/hardware_preflight.sh "$OUT/preflight"
cp config/hardware_profile.yaml "$OUT/hardware_profile.yaml"

cat > "$OUT/run_metadata.txt" <<META
run_id=$RUN_ID
utc_start=$(date -u +%Y-%m-%dT%H:%M:%SZ)
robot_id=$ROBOT_ID
operator=$OPERATOR
environment=$ENVIRONMENT
host=$(hostname)
ros_distro=${ROS_DISTRO:-unknown}
simulation=false
META

ros2 bag record \
  -o "$OUT/bag" \
  /scan /odom /tf /tf_static /diagnostics /map /cmd_vel &
BAG_PID=$!

echo "Recording PHYSICAL evidence to $OUT/bag"
echo "Drive the real robot through the planned mapping / loop-closure route."
echo "Press Enter to stop recording."
read -r
kill -INT "$BAG_PID" || true
wait "$BAG_PID" || true

ros2 bag info "$OUT/bag" > "$OUT/bag_info.txt"
echo "utc_end=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUT/run_metadata.txt"

RUN_ID="$RUN_ID" OUT="$OUT" ROBOT_ID="$ROBOT_ID" OPERATOR="$OPERATOR" ENVIRONMENT="$ENVIRONMENT" python - <<'PY'
import hashlib, os
from pathlib import Path
import yaml
out = Path(os.environ['OUT'])
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
manifest = {
  'hardware_run': {
    'run_id': os.environ['RUN_ID'],
    'date': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).date().isoformat(),
    'robot_id': os.environ['ROBOT_ID'],
    'operator': os.environ['OPERATOR'],
    'environment': os.environ['ENVIRONMENT'],
    'simulation': False,
    'hardware_profile': 'hardware_profile.yaml',
    'rosbag': 'bag/',
    'preflight': 'preflight/preflight.json',
    'tf_audit': 'preflight/tf_odom_base.txt',
    'mapping': {'map_pgm': None, 'map_yaml': None, 'loop_closure_observed': None, 'localization_repeated': None},
    'notes': 'Fill mapping/localization fields after the run; preserve failures as evidence.',
    'files': [
      {'path': 'hardware_profile.yaml', 'sha256': digest(out/'hardware_profile.yaml')},
      {'path': 'preflight/preflight.json', 'sha256': digest(out/'preflight/preflight.json')},
      {'path': 'bag_info.txt', 'sha256': digest(out/'bag_info.txt')},
    ]
  }
}
(out/'manifest.yaml').write_text(yaml.safe_dump(manifest, sort_keys=False), encoding='utf-8')
PY

python tools/evidence_manifest.py "$OUT/manifest.yaml" --check-files
echo "Physical evidence capture complete: $OUT"
echo "Next: save the map/pose graph, fill mapping fields in manifest.yaml, and preserve repeatability runs."
