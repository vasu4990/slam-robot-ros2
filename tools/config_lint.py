#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import sys, yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from slam_robot_ros2.contracts import validate_robot_contract

def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def lint(root: Path = ROOT) -> list[str]:
    errors = validate_robot_contract(load(root / "config/robot.yaml"))
    robot = load(root / "config/robot.yaml")
    for name in ("slam_toolbox.yaml", "slam_localization.yaml"):
        slam = load(root / "config" / name)["slam_toolbox"]["ros__parameters"]
        frames = robot["frames"]
        expected = {
            "map_frame": frames["map"],
            "odom_frame": frames["odom"],
            "base_frame": frames["base_footprint"],
        }
        for key, value in expected.items():
            if slam.get(key) != value:
                errors.append(f"{name}: {key}={slam.get(key)!r}, expected {value!r}")
        if float(slam.get("max_laser_range", 0)) > float(robot["lidar"]["max_range_m"]):
            errors.append(f"{name}: max_laser_range exceeds robot lidar profile")
        if float(slam.get("resolution", 0)) <= 0:
            errors.append(f"{name}: resolution must be positive")
    return errors

def main() -> None:
    errors = lint()
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        raise SystemExit(1)
    print("configuration contracts: PASS")

if __name__ == "__main__":
    main()
