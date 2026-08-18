# Hardware Bring-up

Before launching SLAM, validate each layer independently.

## LiDAR

- Confirm the driver publishes `sensor_msgs/LaserScan`.
- Verify `frame_id` corresponds to `laser_link` (or update the URDF/driver configuration).
- Check scan rate and sensible range values.

## Odometry

- Calibrate wheel radius and wheel separation in the base controller.
- Confirm `/odom` changes smoothly when the robot moves.
- Confirm `odom → base_link` exists and has the same timestamps/time base as sensor data.

## Robot model

Replace placeholder chassis and LiDAR pose dimensions with measurements from the physical robot.

## First mapping test

Drive slowly in a small area with clear planar features. Watch TF, scan alignment, and odometry before attempting large loops.
