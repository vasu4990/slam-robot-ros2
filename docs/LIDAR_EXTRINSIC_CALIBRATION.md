# LiDAR extrinsic verification

The `base_link -> laser_link` transform must represent the physical sensor mounting, not the Gazebo reference model.

Measure X/Y/Z from a repeatable chassis datum and measure roll/pitch/yaw from the sensor mounting surfaces. Record the method, tool resolution and uncertainty.

After updating the robot description, verify:

```bash
ros2 run tf2_ros tf2_echo base_link laser_link
```

Then place the robot near long planar walls and rotate/translate it slowly. Gross extrinsic errors often appear as duplicated/curved walls or scan-matching inconsistency. Visual agreement is a diagnostic aid, not a substitute for dimensional measurement.

The hardware profile must not set `lidar_extrinsics_verified: true` until the transform has been measured and the runtime TF matches the recorded values.
