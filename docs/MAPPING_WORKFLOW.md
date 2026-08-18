# Mapping Workflow

## 1. Hardware preflight

Verify power, wheel direction, encoder polarity, LiDAR orientation and emergency stop behavior.

## 2. Graph preflight

```bash
ros2 topic hz /scan
ros2 topic hz /odom
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 run tf2_ros tf2_echo base_link laser_link
ros2 run slam_robot_ros2 diagnostics
ros2 run slam_robot_ros2 tf_monitor
```

## 3. Start mapping

```bash
ros2 launch slam_robot_ros2 bringup.launch.py mode:=mapping
```

## 4. Drive for observability

Use smooth motion. Avoid only rotating in one spot or driving long textureless corridors at high speed. Revisit previously mapped areas from useful angles to create loop-closure opportunities.

## 5. Inspect failure signals

Watch `/diagnostics`, SLAM console messages, scan alignment in RViz, and TF continuity. Fix upstream sensor/odometry problems before adjusting loop-closure thresholds.

## 6. Save evidence

Record the rosbag and note:

- robot geometry revision
- SLAM config git commit
- battery state
- LiDAR model/rate
- wheel/encoder calibration
- test environment
- map screenshots and map files
- observed loop closures

## 7. Promote maturity only with evidence

Set validation flags only after the corresponding evidence exists. `tools/release_gate.py` intentionally blocks unsupported maturity claims.
