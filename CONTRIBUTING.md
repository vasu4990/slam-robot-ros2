# Contributing

- Keep hardware-specific drivers separate from the generic SLAM orchestration package.
- Document topic and TF assumptions for every launch/config change.
- Validate XML/YAML/Python syntax before opening a PR.
- Run `colcon build --symlink-install` in a ROS 2 workspace for runtime-affecting changes.
- Do not present placeholder robot dimensions or unmeasured odometry parameters as calibrated hardware values.
