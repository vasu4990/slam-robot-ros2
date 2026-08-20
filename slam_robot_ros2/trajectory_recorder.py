"""Record synchronized ground-truth and SLAM-estimated planar trajectories to CSV."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import rclpy
from nav_msgs.msg import Odometry
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener


def yaw_from_quaternion(quaternion) -> float:
    """Convert a geometry_msgs quaternion to planar yaw."""
    return math.atan2(
        2.0
        * (
            quaternion.w * quaternion.z
            + quaternion.x * quaternion.y
        ),
        1.0
        - 2.0
        * (
            quaternion.y * quaternion.y
            + quaternion.z * quaternion.z
        ),
    )


class TrajectoryRecorder(Node):
    """Record ground-truth odometry alongside the SLAM-estimated map pose."""

    def __init__(self) -> None:
        super().__init__("trajectory_recorder")

        self.declare_parameter("output_path", "artifacts/trajectory.csv")
        self.declare_parameter("ground_truth_topic", "/ground_truth/odom")
        self.declare_parameter("map_frame", "map")
        self.declare_parameter("base_frame", "base_footprint")
        self.declare_parameter("sample_rate_hz", 10.0)

        self.latest_ground_truth: Odometry | None = None
        self.rows: list[tuple[float, float, float, float, float, float, float]] = []

        self.tf_buffer = Buffer(cache_time=Duration(seconds=30.0))
        self.tf_listener = TransformListener(self.tf_buffer, self)

        ground_truth_topic = self.get_parameter("ground_truth_topic").value
        self.create_subscription(
            Odometry,
            ground_truth_topic,
            self._ground_truth_callback,
            20,
        )

        sample_rate_hz = max(
            float(self.get_parameter("sample_rate_hz").value),
            0.1,
        )
        self.create_timer(1.0 / sample_rate_hz, self._sample)

    def _ground_truth_callback(self, message: Odometry) -> None:
        self.latest_ground_truth = message

    def _sample(self) -> None:
        if self.latest_ground_truth is None:
            return

        map_frame = self.get_parameter("map_frame").value
        base_frame = self.get_parameter("base_frame").value

        try:
            transform = self.tf_buffer.lookup_transform(
                map_frame,
                base_frame,
                Time(),
            )
        except TransformException:
            return

        ground_truth_pose = self.latest_ground_truth.pose.pose
        estimated_translation = transform.transform.translation
        estimated_rotation = transform.transform.rotation
        stamp_s = self.get_clock().now().nanoseconds / 1e9

        self.rows.append(
            (
                stamp_s,
                ground_truth_pose.position.x,
                ground_truth_pose.position.y,
                yaw_from_quaternion(ground_truth_pose.orientation),
                estimated_translation.x,
                estimated_translation.y,
                yaw_from_quaternion(estimated_rotation),
            )
        )

    def close(self) -> None:
        """Persist all collected trajectory samples."""
        output_path = Path(self.get_parameter("output_path").value)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "stamp_s",
                    "gt_x",
                    "gt_y",
                    "gt_yaw",
                    "est_x",
                    "est_y",
                    "est_yaw",
                ]
            )
            writer.writerows(self.rows)

        self.get_logger().info(
            f"wrote {len(self.rows)} aligned trajectory samples to {output_path}"
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TrajectoryRecorder()

    try:
        rclpy.spin(node)
    finally:
        node.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
