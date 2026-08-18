# SLAM Tuning Strategy

Tune in this order.

## 1. Geometry and timestamps

Before mapper parameters, fix wheel radius/separation, LiDAR pose, scan frame, odometry frame IDs, timestamp source and TF latency.

## 2. Laser range

Set `max_laser_range` to the **usable** range of the real sensor/environment, not an optimistic marketing maximum.

## 3. Motion gating

`minimum_travel_distance` and `minimum_travel_heading` control how often new scans become graph nodes. Lower values increase graph density and compute cost.

## 4. Map resolution

The reference 0.05 m resolution is a starting point. Smaller cells increase memory/CPU and can imply precision your sensors do not possess.

## 5. Scan matching

Only tune scan-matcher search/penalty parameters after inputs are trustworthy. Keep a known-good rosbag so changes can be replayed against the same dataset.

## 6. Loop closure

False-positive loop closures can corrupt a good map. Increase aggressiveness only with a controlled benchmark and visual/pose-graph inspection.

## Experimental discipline

Change one family of parameters at a time, replay the same bag, save map artifacts, and record both qualitative and quantitative results.
