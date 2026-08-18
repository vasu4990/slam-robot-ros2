#!/usr/bin/env python3
"""Validate the physical-hardware profile without pretending measurements exist."""
from __future__ import annotations
import argparse
from pathlib import Path
import yaml

REQUIRED_SECTIONS = ("lidar", "encoders", "drivetrain", "odometry", "calibration", "evidence")


def lint(data: dict, require_measured: bool = False) -> list[str]:
    errors: list[str] = []
    profile = data.get("hardware_profile")
    if not isinstance(profile, dict):
        return ["missing hardware_profile mapping"]
    for section in REQUIRED_SECTIONS:
        if not isinstance(profile.get(section), dict):
            errors.append(f"missing section: {section}")

    lidar = profile.get("lidar", {})
    if lidar.get("frame") != "laser_link":
        errors.append("lidar.frame must remain laser_link unless the TF contract is intentionally changed")
    if lidar.get("scan_topic") != "/scan":
        errors.append("lidar.scan_topic must match the repository /scan contract")

    odom = profile.get("odometry", {})
    if odom.get("topic") != "/odom":
        errors.append("odometry.topic must match /odom")
    if odom.get("parent_frame") != "odom" or odom.get("child_frame") != "base_footprint":
        errors.append("odometry TF contract must be odom -> base_footprint")

    drivetrain = profile.get("drivetrain", {})
    for key in ("wheel_radius_m", "wheel_separation_m"):
        block = drivetrain.get(key, {})
        nominal = block.get("nominal") if isinstance(block, dict) else None
        if nominal is None or float(nominal) <= 0:
            errors.append(f"{key}.nominal must be positive")
        calibrated = block.get("calibrated") if isinstance(block, dict) else None
        if calibrated is not None and float(calibrated) <= 0:
            errors.append(f"{key}.calibrated must be positive when provided")

    if require_measured:
        encoders = profile.get("encoders", {})
        required_values = {
            "robot_id": profile.get("robot_id"),
            "measurement_date": profile.get("measurement_date"),
            "operator": profile.get("operator"),
            "lidar.model": lidar.get("model"),
            "lidar.timestamp_source": lidar.get("timestamp_source"),
            "lidar.measured_rate_hz": lidar.get("measured_rate_hz"),
            "lidar.range_min_m": lidar.get("range_min_m"),
            "lidar.range_max_m": lidar.get("range_max_m"),
            "encoders.counts_per_revolution": encoders.get("counts_per_revolution"),
            "encoders.gear_ratio": encoders.get("gear_ratio"),
            "encoders.left_sign": encoders.get("left_sign"),
            "encoders.right_sign": encoders.get("right_sign"),
            "encoders.timestamp_source": encoders.get("timestamp_source"),
            "odometry.measured_rate_hz": odom.get("measured_rate_hz"),
            "wheel_radius.calibrated": drivetrain.get("wheel_radius_m", {}).get("calibrated"),
            "wheel_separation.calibrated": drivetrain.get("wheel_separation_m", {}).get("calibrated"),
        }
        for name, value in required_values.items():
            if value in (None, ""):
                errors.append(f"measured hardware profile missing: {name}")
        if lidar.get("pose_measured") is not True:
            errors.append("measured hardware profile requires lidar.pose_measured=true")
        if any(v is None for v in lidar.get("xyz_m", [])) or len(lidar.get("xyz_m", [])) != 3:
            errors.append("measured hardware profile requires three lidar xyz values")
        if any(v is None for v in lidar.get("rpy_rad", [])) or len(lidar.get("rpy_rad", [])) != 3:
            errors.append("measured hardware profile requires three lidar rpy values")
        if odom.get("covariance_configured") is not True:
            errors.append("measured hardware profile requires odometry.covariance_configured=true")
        calibration = profile.get("calibration", {})
        for flag in ("wheel_radius_calibrated", "wheel_separation_calibrated", "lidar_extrinsics_verified"):
            if calibration.get(flag) is not True:
                errors.append(f"measured hardware profile requires {flag}=true")
    return errors


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", type=Path, default=Path("config/hardware_profile.yaml"))
    p.add_argument("--require-measured", action="store_true")
    args = p.parse_args()
    data = yaml.safe_load(args.profile.read_text(encoding="utf-8"))
    errors = lint(data, args.require_measured)
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        raise SystemExit(1)
    print("hardware profile: PASS")


if __name__ == "__main__":
    main()
