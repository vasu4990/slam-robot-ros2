# Mapping Workflow

1. Start the LiDAR driver.
2. Start the base controller/odometry publisher.
3. Verify `/scan`, `/odom`, and TF.
4. Launch `mapping.launch.py`.
5. Drive slowly with smooth turns and overlap previously seen areas.
6. Watch for scan tearing or TF jumps; fix sensor/odometry issues before tuning SLAM parameters.
7. Close loops by revisiting recognizable areas.
8. Save the occupancy map and, if needed, serialize the pose graph for later localization/continued mapping.

## Tune in this order

1. Sensor timestamp/frame correctness
2. Wheel odometry calibration
3. LiDAR pose in URDF
4. SLAM movement thresholds and scan settings

Trying to compensate for bad odometry or TF by changing SLAM parameters usually produces a fragile map.
