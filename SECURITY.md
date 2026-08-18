# Security and Operational Safety

This repository participates in a mobile-robot software stack. Incorrect transforms, odometry or localization can cause downstream navigation systems to make unsafe decisions.

- Do not treat SLAM/localization as a collision-avoidance safety layer.
- Maintain a physical or independent emergency stop during development.
- Validate maps and localization before enabling autonomous motion.
- Treat rosbag files as potentially sensitive: maps may reveal private building layouts.
- Do not publish credentials, network secrets or private facility maps in issues.

Report software security issues privately where possible; report robotics-safety defects with enough reproduction detail to prevent unsafe reuse.
