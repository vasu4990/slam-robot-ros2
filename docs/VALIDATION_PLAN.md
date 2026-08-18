# Validation Plan

## Gate A — static reference

Evidence:
- Python tooling/tests pass
- YAML/XML parse
- robot/TF/config contracts pass

## Gate B — ROS build ready

Evidence:
- Lyrical `rosdep` resolution
- `colcon build`
- `colcon test`
- package resources installed correctly

## Gate C — launch smoke

Evidence:
- `synthetic_smoke.launch.py` starts
- `/scan`, `/odom`, TF and `/diagnostics` become visible
- no node crashes during a timed smoke run

Synthetic inputs prove graph integration only; they are **not** SLAM-accuracy evidence.

## Gate D — simulation SLAM

Use a physics simulator with a differential-drive base, realistic LiDAR and known world. Record:
- map completeness
- loop closures
- pose/trajectory error if ground truth exists
- CPU/memory
- failure/recovery behavior

## Gate E — hardware mapping

Record a real rosbag and demonstrate:
- valid TF chain
- stable scan/odometry rates
- repeated closed-loop route
- credible loop closure
- map saved and reproducible from the bag

## Gate F — localization

Repeatedly localize against a serialized map from varied start poses and preserve success/failure statistics.

All hardware/simulation validation flags remain false until these tests are actually run.
