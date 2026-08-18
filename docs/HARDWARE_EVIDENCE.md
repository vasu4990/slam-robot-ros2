# Physical LiDAR + Encoder Evidence Pipeline

Simulation evidence must never be relabeled as hardware evidence. This repository provides the capture and validation machinery, but the measurements must come from the physical robot.

## Required chain

```text
measured wheel radius/separation
        +
real encoder resolution/sign/timestamps
        +
real LiDAR identity/rate/timestamps
        +
measured base_link -> laser_link extrinsics
        ↓
hardware profile
        ↓
ROS graph + TF preflight
        ↓
physical rosbag
        ↓
map + loop-closure runs
        ↓
repeatability/localization runs
        ↓
compact evidence manifest + metrics
```

## 1. Fill the hardware profile

Edit `config/hardware_profile.yaml`. Null values are intentional: they force the physical robot to supply facts that software cannot know.

```bash
python tools/hardware_profile_lint.py
python tools/hardware_profile_lint.py --require-measured
```

The second command must remain blocked until the profile contains actual measurements.

## 2. Calibrate differential-drive geometry

Follow `docs/WHEEL_ODOMETRY_CALIBRATION.md`. Save the generated JSON and copy only defensible calibrated values into the hardware profile.

## 3. Verify LiDAR extrinsics

Follow `docs/LIDAR_EXTRINSIC_CALIBRATION.md`. The runtime `base_link -> laser_link` transform must match the physical measurement record.

## 4. Run preflight

With the physical base and LiDAR drivers running:

```bash
bash scripts/hardware_preflight.sh
```

It checks required topics, both critical TF edges, sensor/odometry rates, timestamp regressions, odometry covariance presence and LiDAR return statistics.

## 5. Record a physical run

```bash
export ROBOT_ID=robot01
export OPERATOR=<name>
export ENVIRONMENT=<location_or_track>
bash scripts/record_hardware_evidence.sh robot01_mapping_run01
```

The script runs preflight first, records `/scan`, `/odom`, `/tf`, `/tf_static`, `/diagnostics`, `/map` and `/cmd_vel`, writes bag metadata, calculates checksums for compact evidence files and generates a run manifest.

## 6. Preserve compact evidence

Validate the generated manifest:

```bash
python tools/evidence_manifest.py artifacts/hardware_runs/<run>/manifest.yaml --check-files
```

Raw bags can remain external; commit compact map/metric/calibration summaries where practical.

## 7. Repeatability

A single successful map is not enough. Record multiple runs of the same route, including at least one cold-start localization run against a saved pose graph/map. Preserve failures too.

## Maturity

`hardware-data-ready` requires a measured profile, physical preflight, captured rosbag and evidence manifest. `hardware-calibrated` additionally requires wheel calibration and LiDAR-extrinsic verification. Mapping/localization gates remain false until their own measured evidence exists.
