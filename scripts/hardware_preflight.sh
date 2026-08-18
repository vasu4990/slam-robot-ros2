#!/usr/bin/env bash
set -euo pipefail
OUT=${1:-artifacts/hardware}
mkdir -p "$OUT"

echo "[1/5] Hardware profile template contract"
python tools/hardware_profile_lint.py

echo "[2/5] Required ROS graph"
ros2 topic list > "$OUT/topics.txt"
for topic in /scan /odom /tf /tf_static; do
  grep -qx "$topic" "$OUT/topics.txt" || { echo "missing topic: $topic"; exit 1; }
done

echo "[3/5] TF audit"
(timeout 5s ros2 run tf2_ros tf2_echo odom base_footprint || true) > "$OUT/tf_odom_base.txt" 2>&1
(timeout 5s ros2 run tf2_ros tf2_echo base_link laser_link || true) > "$OUT/tf_base_laser.txt" 2>&1
grep -q "Translation" "$OUT/tf_odom_base.txt" || { echo "odom -> base_footprint unavailable"; exit 1; }
grep -q "Translation" "$OUT/tf_base_laser.txt" || { echo "base_link -> laser_link unavailable"; exit 1; }

echo "[4/5] Timed sensor/odom audit"
ros2 run slam_robot_ros2 hardware_audit --ros-args \
  -p duration_sec:=20.0 -p output:="$OUT/preflight.json"

echo "[5/5] Bag subsystem"
ros2 bag --help > "$OUT/rosbag_help.txt"

echo "hardware preflight evidence written to $OUT"
