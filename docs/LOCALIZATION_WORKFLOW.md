# Localization Workflow

`slam_toolbox` localization uses a serialized pose graph, not merely a PNG/PGM occupancy image.

Start with a known serialized map base path:

```bash
ros2 launch slam_robot_ros2 localization.launch.py \
  map_file_name:=/absolute/path/to/site_map \
  use_sim_time:=false
```

## Validation

Confirm:

1. the localization node becomes active;
2. `map -> odom` is published by exactly one source;
3. `/scan` transforms into the configured base frame at scan timestamps;
4. the robot pose remains consistent after motion;
5. relocalization behavior is tested from multiple starting poses.

Do not mark `localization_validated` true from a single successful startup. Use repeated trials and preserve the rosbag/log evidence.
