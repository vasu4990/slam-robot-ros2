#!/usr/bin/env python3
"""Estimate wheel-radius and wheel-separation corrections from physical calibration runs."""
from __future__ import annotations
import argparse, csv, json, statistics
from pathlib import Path


def radius_scale(measured_distance_m: float, odom_distance_m: float) -> float:
    if measured_distance_m <= 0 or odom_distance_m <= 0:
        raise ValueError("distances must be positive")
    return measured_distance_m / odom_distance_m


def separation_scale(measured_yaw_rad: float, odom_yaw_rad: float) -> float:
    if abs(measured_yaw_rad) < 1e-9 or abs(odom_yaw_rad) < 1e-9:
        raise ValueError("yaw magnitudes must be non-zero")
    return odom_yaw_rad / measured_yaw_rad


def load_runs(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summarize(path: Path, nominal_radius: float, nominal_separation: float) -> dict:
    radius_scales, separation_scales = [], []
    for row in load_runs(path):
        kind = row["kind"].strip().lower()
        if kind == "straight":
            radius_scales.append(radius_scale(float(row["measured"]), float(row["odom"])))
        elif kind == "rotation":
            separation_scales.append(separation_scale(float(row["measured"]), float(row["odom"])))
        else:
            raise ValueError(f"unsupported run kind: {kind}")
    if not radius_scales or not separation_scales:
        raise ValueError("need at least one straight and one rotation run")
    r_scale = statistics.fmean(radius_scales)
    s_scale = statistics.fmean(separation_scales)
    return {
        "straight_runs": len(radius_scales),
        "rotation_runs": len(separation_scales),
        "wheel_radius_scale": r_scale,
        "wheel_radius_calibrated_m": nominal_radius * r_scale,
        "wheel_separation_scale": s_scale,
        "wheel_separation_calibrated_m": nominal_separation * s_scale,
        "radius_scale_stddev": statistics.pstdev(radius_scales) if len(radius_scales) > 1 else 0.0,
        "separation_scale_stddev": statistics.pstdev(separation_scales) if len(separation_scales) > 1 else 0.0,
        "input_is_physical_measurement_required": True,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("csv", type=Path, help="CSV columns: kind,measured,odom")
    p.add_argument("--nominal-radius", type=float, required=True)
    p.add_argument("--nominal-separation", type=float, required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = summarize(args.csv, args.nominal_radius, args.nominal_separation)
    text = json.dumps(result, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
