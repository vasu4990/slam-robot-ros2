# TF Tree Contract

A healthy mapping setup needs these transforms:

```text
map -> odom -> base_link -> laser_link
```

## Ownership

- `slam_toolbox` publishes `map → odom` while mapping.
- The robot base/odometry system publishes `odom → base_link`.
- `robot_state_publisher` publishes fixed/dynamic transforms from the URDF, including `base_link → laser_link`.

Do not publish the same transform from two nodes. TF conflicts are a common cause of unstable maps.

## Verify

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo base_link laser_link
ros2 topic echo /tf --once
```
