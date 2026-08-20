#!/usr/bin/env python3
"""Compute SE(2)-aligned ATE and fixed-delta RPE from benchmark trajectory CSV."""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Pose2:
    x: float
    y: float
    yaw: float


def wrap(angle: float) -> float:
    """Wrap an angle to [-pi, pi]."""
    return math.atan2(math.sin(angle), math.cos(angle))


def compose(a: Pose2, b: Pose2) -> Pose2:
    """Compose two planar rigid-body poses."""
    cos_yaw = math.cos(a.yaw)
    sin_yaw = math.sin(a.yaw)
    return Pose2(
        a.x + cos_yaw * b.x - sin_yaw * b.y,
        a.y + sin_yaw * b.x + cos_yaw * b.y,
        wrap(a.yaw + b.yaw),
    )


def inverse(pose: Pose2) -> Pose2:
    """Return the inverse of a planar pose."""
    cos_yaw = math.cos(pose.yaw)
    sin_yaw = math.sin(pose.yaw)
    return Pose2(
        -cos_yaw * pose.x - sin_yaw * pose.y,
        sin_yaw * pose.x - cos_yaw * pose.y,
        wrap(-pose.yaw),
    )


def relative(a: Pose2, b: Pose2) -> Pose2:
    """Return pose b expressed relative to pose a."""
    return compose(inverse(a), b)


def load(path: Path):
    """Load trajectory rows from the benchmark CSV schema."""
    rows = []
    with Path(path).open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            rows.append(
                (
                    float(row["stamp_s"]),
                    Pose2(
                        float(row["gt_x"]),
                        float(row["gt_y"]),
                        float(row["gt_yaw"]),
                    ),
                    Pose2(
                        float(row["est_x"]),
                        float(row["est_y"]),
                        float(row["est_yaw"]),
                    ),
                )
            )

    if len(rows) < 2:
        raise ValueError("at least two samples required")
    return rows


def align_se2(ground_truth: list[Pose2], estimated: list[Pose2]):
    """Rigidly align estimated XY positions to ground truth without scale correction."""
    gt_x = sum(pose.x for pose in ground_truth) / len(ground_truth)
    gt_y = sum(pose.y for pose in ground_truth) / len(ground_truth)
    est_x = sum(pose.x for pose in estimated) / len(estimated)
    est_y = sum(pose.y for pose in estimated) / len(estimated)

    cross = 0.0
    dot = 0.0
    for gt_pose, est_pose in zip(ground_truth, estimated):
        gt_dx = gt_pose.x - gt_x
        gt_dy = gt_pose.y - gt_y
        est_dx = est_pose.x - est_x
        est_dy = est_pose.y - est_y
        dot += est_dx * gt_dx + est_dy * gt_dy
        cross += est_dx * gt_dy - est_dy * gt_dx

    yaw = math.atan2(cross, dot)
    cos_yaw = math.cos(yaw)
    sin_yaw = math.sin(yaw)
    tx = gt_x - (cos_yaw * est_x - sin_yaw * est_y)
    ty = gt_y - (sin_yaw * est_x + cos_yaw * est_y)

    aligned = [
        Pose2(
            cos_yaw * pose.x - sin_yaw * pose.y + tx,
            sin_yaw * pose.x + cos_yaw * pose.y + ty,
            wrap(pose.yaw + yaw),
        )
        for pose in estimated
    ]
    transform = {"yaw_rad": yaw, "tx_m": tx, "ty_m": ty}
    return aligned, transform


def rms(values: list[float]) -> float:
    """Return root-mean-square, or zero for an empty sequence."""
    if not values:
        return 0.0
    return math.sqrt(sum(value * value for value in values) / len(values))


def evaluate(rows, delta: int = 10) -> dict:
    """Evaluate absolute and relative planar trajectory error."""
    ground_truth = [row[1] for row in rows]
    estimated = [row[2] for row in rows]
    aligned, transform = align_se2(ground_truth, estimated)

    ate = [
        math.hypot(gt_pose.x - est_pose.x, gt_pose.y - est_pose.y)
        for gt_pose, est_pose in zip(ground_truth, aligned)
    ]
    yaw_error = [
        abs(wrap(gt_pose.yaw - est_pose.yaw))
        for gt_pose, est_pose in zip(ground_truth, aligned)
    ]

    rpe_translation = []
    rpe_yaw = []
    for index in range(len(rows) - delta):
        gt_motion = relative(ground_truth[index], ground_truth[index + delta])
        est_motion = relative(aligned[index], aligned[index + delta])
        error = relative(gt_motion, est_motion)
        rpe_translation.append(math.hypot(error.x, error.y))
        rpe_yaw.append(abs(error.yaw))

    return {
        "samples": len(rows),
        "duration_s": rows[-1][0] - rows[0][0],
        "alignment_se2": transform,
        "ate_rmse_m": rms(ate),
        "ate_mean_m": sum(ate) / len(ate),
        "ate_max_m": max(ate),
        "yaw_rmse_rad": rms(yaw_error),
        "rpe_delta_samples": delta,
        "rpe_translation_rmse_m": rms(rpe_translation),
        "rpe_translation_max_m": max(rpe_translation) if rpe_translation else 0.0,
        "rpe_yaw_rmse_rad": rms(rpe_yaw),
        "rpe_yaw_max_rad": max(rpe_yaw) if rpe_yaw else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--delta", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    metrics = evaluate(load(args.csv), args.delta)
    text = json.dumps(metrics, indent=2)
    print(text)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
