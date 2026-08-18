"""Pure-Python contract helpers shared by tests and offline tooling."""
from __future__ import annotations

REQUIRED_FRAMES = ("map", "odom", "base_footprint", "base_link", "laser")
REQUIRED_TOPICS = ("scan", "odom", "map", "cmd_vel", "diagnostics")

def validate_robot_contract(data: dict) -> list[str]:
    errors: list[str] = []
    frames = data.get("frames", {})
    topics = data.get("topics", {})
    rates = data.get("expected_rates_hz", {})
    geometry = data.get("robot_geometry", {})
    lidar = data.get("lidar", {})
    for key in REQUIRED_FRAMES:
        if not frames.get(key):
            errors.append(f"missing frame: {key}")
    for key in REQUIRED_TOPICS:
        value = topics.get(key)
        if not isinstance(value, str) or not value.startswith("/"):
            errors.append(f"topic {key} must be an absolute ROS name")
    for key in ("scan_min", "odom_min", "map_min"):
        if float(rates.get(key, 0.0)) <= 0:
            errors.append(f"expected rate {key} must be positive")
    for key in ("chassis_length_m", "chassis_width_m", "chassis_height_m",
                "wheel_radius_m", "wheel_separation_m", "wheel_width_m"):
        if float(geometry.get(key, 0.0)) <= 0:
            errors.append(f"geometry {key} must be positive")
    if float(lidar.get("min_range_m", 0.0)) < 0:
        errors.append("lidar min_range_m cannot be negative")
    if float(lidar.get("max_range_m", 0.0)) <= float(lidar.get("min_range_m", 0.0)):
        errors.append("lidar max_range_m must exceed min_range_m")
    if frames.get("map") == frames.get("odom"):
        errors.append("map and odom frames must be distinct")
    return errors
