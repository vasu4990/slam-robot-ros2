# Hardware Bring-up

1. Lift the drive wheels and verify forward/reverse commands.
2. Confirm encoder signs agree with wheel direction.
3. Measure wheel radius and wheel separation.
4. Verify the LiDAR is mechanically rigid and its pose is measured.
5. Confirm `/scan` frame/rate/ranges.
6. Confirm `/odom` frame, child frame, rate and continuity.
7. Verify `odom -> base_footprint` and `base_link -> laser_link`.
8. Drive a measured straight distance and compare odometry scale.
9. Rotate a measured angle and compare heading.
10. Record a short bag before attempting a large map.

Do not compensate for bad base calibration by over-tuning SLAM.
