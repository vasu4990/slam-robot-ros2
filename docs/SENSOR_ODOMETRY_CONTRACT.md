# Sensor and Odometry Contract

SLAM quality is bounded by input quality. A perfectly tuned mapper cannot repair broken timestamps, incorrect frames, wheel slip, or a bad LiDAR extrinsic.

## LaserScan

Expected reference profile:

- topic: `/scan`
- frame: `laser_link`
- rate: at least 5 Hz
- usable range: 0.10–12 m
- timestamps from the same ROS time domain as TF
- NaN/Inf values only where the sensor legitimately has no return

Validate `angle_min`, `angle_max`, `angle_increment`, `range_min`, `range_max`, and message rate.

## Odometry

Expected reference profile:

- topic: `/odom`
- frame: `odom`
- child frame: `base_footprint`
- reference minimum rate: 15 Hz
- continuous local frame with no arbitrary global resets during mapping

Wheel radius and separation errors show up as scale and heading drift. Measure them physically and calibrate the base driver before SLAM tuning.

## Covariance

Do not blindly publish all-zero covariance. If a base driver or filter supports covariance, populate it with meaningful values so downstream tools can reason about uncertainty.

## Rosbag evidence

A useful mapping dataset should record at minimum:

```bash
ros2 bag record /scan /odom /tf /tf_static /diagnostics
```

Also record `/imu/data` if an IMU participates in the state estimator.
