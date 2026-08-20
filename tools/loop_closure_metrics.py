#!/usr/bin/env python3
"""Detect ground-truth loop revisits and score long-horizon relative-pose error."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

try:
    from tools.trajectory_metrics import load, relative, wrap
except ModuleNotFoundError:
    from trajectory_metrics import load, relative, wrap


def cumulative(ground_truth) -> list[float]:
    """Return cumulative XY path length for the ground-truth trajectory."""
    distances = [0.0]
    for previous, current in zip(ground_truth, ground_truth[1:]):
        step = math.hypot(current.x - previous.x, current.y - previous.y)
        distances.append(distances[-1] + step)
    return distances


def detect(
    rows,
    radius: float = 0.30,
    min_path: float = 3.0,
    min_gap_samples: int = 50,
) -> list[dict]:
    """Detect spatial revisits separated by enough travelled distance and samples."""
    ground_truth = [row[1] for row in rows]
    estimated = [row[2] for row in rows]
    path_distance = cumulative(ground_truth)

    events = []
    last_event_end = -min_gap_samples

    for end_index in range(min_gap_samples, len(rows)):
        best_match = None

        for start_index in range(0, end_index - min_gap_samples):
            travelled = path_distance[end_index] - path_distance[start_index]
            if travelled < min_path:
                continue

            revisit_distance = math.hypot(
                ground_truth[end_index].x - ground_truth[start_index].x,
                ground_truth[end_index].y - ground_truth[start_index].y,
            )

            if revisit_distance <= radius and (
                best_match is None or revisit_distance < best_match[0]
            ):
                best_match = (revisit_distance, start_index)

        if best_match is None or end_index - last_event_end < min_gap_samples:
            continue

        revisit_distance, start_index = best_match
        gt_motion = relative(ground_truth[start_index], ground_truth[end_index])
        est_motion = relative(estimated[start_index], estimated[end_index])
        error = relative(gt_motion, est_motion)

        events.append(
            {
                "start_index": start_index,
                "end_index": end_index,
                "path_length_m": path_distance[end_index] - path_distance[start_index],
                "gt_revisit_distance_m": revisit_distance,
                "relative_translation_error_m": math.hypot(error.x, error.y),
                "relative_yaw_error_rad": abs(wrap(error.yaw)),
            }
        )
        last_event_end = end_index

    return events


def evaluate(rows, **kwargs) -> dict:
    """Aggregate loop-revisit error statistics."""
    events = detect(rows, **kwargs)
    if not events:
        return {
            "loop_events": 0,
            "mean_relative_translation_error_m": None,
            "mean_relative_yaw_error_rad": None,
            "events": [],
        }

    translation_errors = [
        event["relative_translation_error_m"] for event in events
    ]
    yaw_errors = [event["relative_yaw_error_rad"] for event in events]

    return {
        "loop_events": len(events),
        "mean_relative_translation_error_m": sum(translation_errors)
        / len(translation_errors),
        "max_relative_translation_error_m": max(translation_errors),
        "mean_relative_yaw_error_rad": sum(yaw_errors) / len(yaw_errors),
        "max_relative_yaw_error_rad": max(yaw_errors),
        "events": events,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--radius", type=float, default=0.30)
    parser.add_argument("--min-path", type=float, default=3.0)
    parser.add_argument("--min-gap-samples", type=int, default=50)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    metrics = evaluate(
        load(args.csv),
        radius=args.radius,
        min_path=args.min_path,
        min_gap_samples=args.min_gap_samples,
    )
    text = json.dumps(metrics, indent=2)
    print(text)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
