# Rosbag Regression Benchmark

A rosbag turns SLAM tuning into a reproducible experiment.

## Record

```bash
ros2 bag record \
  /scan /odom /tf /tf_static /diagnostics
```

Include IMU topics if they feed odometry.

## Replay

```bash
ros2 bag play <bag> --clock
ros2 launch slam_robot_ros2 mapping.launch.py use_sim_time:=true
```

## Compare revisions

For each config/git commit capture:
- map file and screenshot
- bag identifier
- SLAM console log
- total processing time
- CPU/memory if measured
- loop-closure count/locations if available
- visible map defects
- map occupancy metrics

Never compare two parameter sets using different driving paths and call the result a controlled benchmark.
