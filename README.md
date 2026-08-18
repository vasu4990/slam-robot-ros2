# SLAM Robot — ROS 2

A ROS 2 mobile-robot SLAM starter workspace showing the core pieces needed to map an indoor environment with a 2D LiDAR and differential-drive base.

> **Status:** integration scaffold, not a claim of a fully calibrated physical robot. Frame names, LiDAR topic, wheel odometry, robot dimensions, and Nav2/SLAM parameters must be matched to the actual platform.

## Target stack

- ROS 2
- `slam_toolbox`
- 2D LiDAR publishing `sensor_msgs/LaserScan`
- Differential-drive odometry publishing `nav_msgs/Odometry`
- TF tree connecting `map → odom → base_link → laser`
- Optional Nav2 after mapping is stable

## Expected graph

```text
LiDAR ─────────────→ /scan ───────┐
                                  │
wheel odometry → /odom → TF       ├→ slam_toolbox → /map + map→odom TF
                                  │
robot_state_publisher → base TF ──┘
```

## Repository layout

```text
slam_robot_ros2/
├── launch/
│   └── mapping.launch.py
├── config/
│   └── slam_toolbox.yaml
└── README.md
```

## Prerequisites

Install ROS 2 for your platform plus `slam_toolbox`. Your robot must already provide a valid `/scan`, odometry, and TF chain.

## Run

From a ROS 2 workspace containing this package:

```bash
colcon build --symlink-install
source install/setup.bash
ros2 launch slam_robot_ros2 mapping.launch.py
```

Useful checks before blaming SLAM:

```bash
ros2 topic hz /scan
ros2 topic echo /odom --once
ros2 run tf2_tools view_frames
```

## Mapping quality checklist

1. LiDAR timestamps are current and stable.
2. Laser frame is rigidly connected to `base_link`.
3. Wheel odometry has realistic scale and sign.
4. Robot rotates in place without odometry exploding.
5. No duplicate publishers fight over `map→odom` or `odom→base_link`.
6. LiDAR minimum/maximum range is sensible.
7. Drive slowly during the first mapping tests.

## Next milestones

- [x] SLAM Toolbox parameter file
- [x] Mapping launch file
- [ ] Robot URDF/Xacro
- [ ] Base controller / encoder odometry
- [ ] Real LiDAR driver integration
- [ ] Saved map example
- [ ] Nav2 localization + navigation launch
- [ ] Mapping results and loop-closure screenshots
