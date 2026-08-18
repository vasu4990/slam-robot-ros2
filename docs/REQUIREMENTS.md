# Engineering Requirements

## Functional

- Accept a 2D `LaserScan` stream and local odometry.
- Maintain the canonical `map -> odom -> base_footprint` TF ownership model.
- Support online asynchronous mapping.
- Support localization against a serialized SLAM Toolbox map.
- Publish standard diagnostic messages for input/TF health.

## Quality

- All configuration and reference geometry must be machine-readable.
- Hardware-specific assumptions must be visibly marked unvalidated.
- Static contract tests must detect frame/config drift.
- ROS CI must build/test the package against the reference LTS distribution.
- Maturity claims must be evidence-gated.

## Safety/integrity

This package does not command motors directly. However, operators must preserve an independent stop mechanism during mapping and never use SLAM output as the sole safety system for collision avoidance.
