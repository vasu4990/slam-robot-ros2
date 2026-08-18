# SLAM Robot — ROS 2

[![Engineering CI](https://github.com/vasu4990/slam-robot-ros2/actions/workflows/checks.yml/badge.svg)](https://github.com/vasu4990/slam-robot-ros2/actions/workflows/checks.yml)

An engineering-grade ROS 2 stack for a small differential-drive robot performing **2D LiDAR SLAM and pose-graph localization with `slam_toolbox`**.

The project is built around a strict robotics contract: sensor/odometry quality first, unambiguous TF ownership, lifecycle-managed mapping/localization, standard diagnostics, repeatable rosbag experiments, machine-readable validation state, and CI that checks both offline contracts and a real ROS build.

> **Reference platform:** ROS 2 **Lyrical Luth (LTS)**.  
> **Status:** software/reference architecture upgraded; simulation and physical-robot mapping/localization remain explicitly unvalidated until evidence is recorded.

## Why this repository is different

A basic SLAM repository often contains a launch file, a YAML file and a URDF. This repository also includes:

- mapping **and localization** lifecycle launches;
- canonical `map -> odom -> base_footprint -> base_link -> laser_link` ownership;
- `slam_toolbox` mapping/localization parameter profiles;
- a structured differential-drive xacro model;
- standard `/diagnostics` health reporting for scan, odometry, map and TF;
- deterministic synthetic scan/odometry input for graph-level smoke tests;
- machine-readable robot/topic/frame/geometry contracts;
- config and URDF contract linters;
- evidence-based maturity gates;
- P2/P5 occupancy-map metrics;
- odometry trace metrics;
- reproducible rosbag benchmark guidance;
- Lyrical build/test CI using ROS tooling;
- failure-mode, tuning, validation and performance documentation.

## Architecture

```mermaid
flowchart LR
    L[LiDAR driver] -->|/scan| S[slam_toolbox]
    O[Odometry / state estimator] -->|/odom| S
    O -->|odom -> base_footprint| TF[TF]
    R[robot_state_publisher] -->|base_footprint -> base_link -> laser_link| TF
    S -->|map -> odom| TF
    S -->|/map| MAP[Occupancy map]
    L --> H[Health monitor]
    O --> H
    MAP --> H
    TF --> T[TF monitor]
    H --> D[/diagnostics]
    T --> D
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## TF contract

```text
map                         <- slam_toolbox
└── odom                    <- local odometry frame
    └── base_footprint      <- base driver/state estimator publishes this edge
        └── base_link       <- robot_state_publisher
            ├── laser_link
            ├── left_wheel_link
            └── right_wheel_link
```

**No two nodes should publish the same TF edge.** See [`docs/TF_CONTRACT.md`](docs/TF_CONTRACT.md).

## Repository structure

```text
.
├── config/
│   ├── robot.yaml
│   ├── diagnostics.yaml
│   ├── slam_toolbox.yaml
│   ├── slam_localization.yaml
│   └── validation.yaml
├── launch/
│   ├── bringup.launch.py
│   ├── mapping.launch.py
│   ├── localization.launch.py
│   ├── diagnostics.launch.py
│   ├── robot_state.launch.py
│   └── synthetic_smoke.launch.py
├── slam_robot_ros2/
│   ├── contracts.py
│   ├── diagnostics.py
│   ├── synthetic_inputs.py
│   └── tf_monitor.py
├── urdf/robot.urdf.xacro
├── tools/
│   ├── config_lint.py
│   ├── generate_report.py
│   ├── map_metrics.py
│   ├── odom_metrics.py
│   ├── release_gate.py
│   └── urdf_lint.py
├── tests/
├── examples/
└── docs/
```

## Build

On a supported ROS 2 Lyrical system:

```bash
mkdir -p ~/slam_ws/src
cd ~/slam_ws/src
git clone https://github.com/vasu4990/slam-robot-ros2.git
cd ~/slam_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## Preflight before mapping

Your hardware stack must already provide `/scan`, `/odom`, and `odom -> base_footprint`.

```bash
ros2 topic hz /scan
ros2 topic hz /odom
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 run tf2_ros tf2_echo base_link laser_link
```

Then run the monitors:

```bash
ros2 launch slam_robot_ros2 diagnostics.launch.py
ros2 topic echo /diagnostics
```

## Mapping

```bash
ros2 launch slam_robot_ros2 bringup.launch.py mode:=mapping use_sim_time:=false
```

Or only the SLAM lifecycle node:

```bash
ros2 launch slam_robot_ros2 mapping.launch.py
```

## Localization

Use a **serialized SLAM Toolbox pose graph**:

```bash
ros2 launch slam_robot_ros2 localization.launch.py \
  map_file_name:=/absolute/path/to/site_map
```

See [`docs/LOCALIZATION_WORKFLOW.md`](docs/LOCALIZATION_WORKFLOW.md).

## Synthetic graph smoke test

```bash
ros2 launch slam_robot_ros2 synthetic_smoke.launch.py
```

This publishes deterministic fake `/scan`, `/odom` and `odom -> base_footprint` so the package graph/diagnostics can be exercised without hardware.

**It is not a physics simulation and must not be used as SLAM-performance evidence.**

## Offline engineering checks

```bash
python -m pip install -r requirements-dev.txt
pytest -q
python tools/config_lint.py
python tools/urdf_lint.py
python tools/map_metrics.py examples/sample_map.pgm
python tools/odom_metrics.py examples/sample_odom.csv
python tools/generate_report.py
python tools/release_gate.py reference
```

## Evidence-based maturity

The source of truth is [`config/robot.yaml`](config/robot.yaml).

| Gate | Current |
|---|---|
| Static engineering reference | ✅ |
| ROS build ready | ❌ until ROS CI/build evidence |
| Launch smoke validated | ❌ |
| Simulation SLAM validated | ❌ |
| Hardware TF validated | ❌ |
| Hardware mapping validated | ❌ |
| Loop closure validated | ❌ |
| Localization validated | ❌ |

The gates are deliberately conservative. A green README checkbox is not evidence.

## Calibration warning

The URDF dimensions are **reference placeholders**, not measured geometry. Before using a real robot:

- measure wheel radius;
- measure wheel separation;
- measure LiDAR XYZ/RPY pose;
- calibrate odometry scale/heading;
- verify scan timestamps/ranges/frame;
- record a short rosbag and inspect TF.

See [`docs/HARDWARE_BRINGUP.md`](docs/HARDWARE_BRINGUP.md).

## Reproducible SLAM tuning

Do not tune from memory. Record a bag:

```bash
ros2 bag record /scan /odom /tf /tf_static /diagnostics
```

Replay the same dataset for competing parameter sets and preserve map/metric artifacts. See [`docs/ROSBAG_BENCHMARK.md`](docs/ROSBAG_BENCHMARK.md) and [`docs/TUNING.md`](docs/TUNING.md).

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [TF contract](docs/TF_CONTRACT.md)
- [Sensor/odometry contract](docs/SENSOR_ODOMETRY_CONTRACT.md)
- [Hardware bring-up](docs/HARDWARE_BRINGUP.md)
- [Mapping workflow](docs/MAPPING_WORKFLOW.md)
- [Localization workflow](docs/LOCALIZATION_WORKFLOW.md)
- [SLAM tuning](docs/TUNING.md)
- [Rosbag benchmark](docs/ROSBAG_BENCHMARK.md)
- [Validation plan](docs/VALIDATION_PLAN.md)
- [Failure modes](docs/FAILURE_MODES.md)
- [Performance benchmark](docs/PERFORMANCE_BENCHMARK.md)
- [Engineering requirements](docs/REQUIREMENTS.md)

## License

MIT — see [`LICENSE`](LICENSE).
