# CPU and Memory Profiling

Use `tools/process_profile.py` while a benchmark is running. Example:
```bash
python tools/process_profile.py --duration 90 --match slam_toolbox --match gz --match ros_gz_bridge --output artifacts/resource-profile.json
```

Record CPU model, RAM, ROS distro, Gazebo version and whether Gazebo is headless. Resource numbers are not comparable without the same host and scenario.
