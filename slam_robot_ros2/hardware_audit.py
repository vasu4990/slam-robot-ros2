#!/usr/bin/env python3
"""Runtime audit for physical /scan, /odom and required TF edges."""
from __future__ import annotations
import json, math, time
from pathlib import Path
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from tf2_ros import Buffer, TransformListener


def stamp_to_sec(stamp) -> float:
    return float(stamp.sec) + float(stamp.nanosec) * 1e-9


class HardwareAudit(Node):
    def __init__(self):
        super().__init__("hardware_evidence_audit")
        self.declare_parameter("duration_sec", 20.0)
        self.declare_parameter("output", "artifacts/hardware/preflight.json")
        self.scan_times: list[float] = []
        self.odom_times: list[float] = []
        self.last_scan_stamp = None
        self.last_odom_stamp = None
        self.scan_stamp_regressions = 0
        self.odom_stamp_regressions = 0
        self.total_ranges = 0
        self.nan_ranges = 0
        self.inf_ranges = 0
        self.finite_outside_range = 0
        self.odom_covariance_nonzero_seen = False
        self.start = time.monotonic()
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.create_subscription(LaserScan, "/scan", self.on_scan, 20)
        self.create_subscription(Odometry, "/odom", self.on_odom, 50)
        self.create_timer(0.25, self.tick)

    def on_scan(self, msg: LaserScan):
        self.scan_times.append(time.monotonic())
        stamp = stamp_to_sec(msg.header.stamp)
        if self.last_scan_stamp is not None and stamp < self.last_scan_stamp:
            self.scan_stamp_regressions += 1
        self.last_scan_stamp = stamp
        for value in msg.ranges:
            self.total_ranges += 1
            if math.isnan(value):
                self.nan_ranges += 1
            elif math.isinf(value):
                self.inf_ranges += 1
            elif value < msg.range_min or value > msg.range_max:
                self.finite_outside_range += 1

    def on_odom(self, msg: Odometry):
        self.odom_times.append(time.monotonic())
        stamp = stamp_to_sec(msg.header.stamp)
        if self.last_odom_stamp is not None and stamp < self.last_odom_stamp:
            self.odom_stamp_regressions += 1
        self.last_odom_stamp = stamp
        if any(abs(v) > 0.0 for v in msg.pose.covariance + msg.twist.covariance):
            self.odom_covariance_nonzero_seen = True

    @staticmethod
    def rate(times: list[float]) -> float:
        if len(times) < 2:
            return 0.0
        dt = times[-1] - times[0]
        return (len(times) - 1) / dt if dt > 0 else 0.0

    def has_tf(self, target: str, source: str) -> bool:
        try:
            return self.tf_buffer.can_transform(target, source, rclpy.time.Time())
        except Exception:
            return False

    def tick(self):
        if time.monotonic() - self.start < float(self.get_parameter("duration_sec").value):
            return
        total = max(self.total_ranges, 1)
        result = {
            "simulation": False,
            "duration_sec": time.monotonic() - self.start,
            "scan_messages": len(self.scan_times),
            "scan_rate_hz": self.rate(self.scan_times),
            "scan_stamp_regressions": self.scan_stamp_regressions,
            "odom_messages": len(self.odom_times),
            "odom_rate_hz": self.rate(self.odom_times),
            "odom_stamp_regressions": self.odom_stamp_regressions,
            "odom_covariance_nonzero_seen": self.odom_covariance_nonzero_seen,
            "scan_nan_ratio": self.nan_ranges / total,
            "scan_no_return_inf_ratio": self.inf_ranges / total,
            "scan_finite_outside_range_ratio": self.finite_outside_range / total,
            "tf_odom_to_base_footprint": self.has_tf("odom", "base_footprint"),
            "tf_base_link_to_laser_link": self.has_tf("base_link", "laser_link"),
        }
        output = Path(str(self.get_parameter("output").value))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        self.get_logger().info(json.dumps(result))
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = HardwareAudit()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
