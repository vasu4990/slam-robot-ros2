# TF Contract

Required tree:

```text
map
└── odom
    └── base_footprint
        └── base_link
            ├── laser_link
            ├── left_wheel_link
            └── right_wheel_link
```

## Rules

1. `slam_toolbox` owns `map -> odom`.
2. The wheel-odometry/state-estimation stack owns `odom -> base_footprint`.
3. `robot_state_publisher` owns geometry-only transforms below `base_footprint`.
4. The LiDAR message `header.frame_id` must resolve to `laser_link` or a documented sensor frame.
5. TF timestamps must be recent enough for the LaserScan timestamps to transform through the tree.

## Preflight

```bash
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 run tf2_ros tf2_echo base_link laser_link
ros2 topic echo /scan --once
ros2 topic echo /odom --once
```

Do not start tuning SLAM parameters until these invariants are correct.
