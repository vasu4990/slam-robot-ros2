"""ROS diagnostics for SLAM input freshness and rate health."""
from __future__ import annotations
from dataclasses import dataclass
import time

import rclpy
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from nav_msgs.msg import OccupancyGrid, Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile
from sensor_msgs.msg import LaserScan

@dataclass
class TopicState:
    count: int = 0
    last_monotonic: float | None = None

class SlamHealthMonitor(Node):
    def __init__(self) -> None:
        super().__init__("slam_health_monitor")
        self.declare_parameter("scan_topic", "/scan")
        self.declare_parameter("odom_topic", "/odom")
        self.declare_parameter("map_topic", "/map")
        self.declare_parameter("diagnostics_topic", "/diagnostics")
        self.declare_parameter("scan_min_hz", 5.0)
        self.declare_parameter("odom_min_hz", 15.0)
        self.declare_parameter("scan_stale_sec", 1.0)
        self.declare_parameter("odom_stale_sec", 0.5)
        self.declare_parameter("map_stale_sec", 8.0)
        self.declare_parameter("report_period_sec", 1.0)

        self.scan = TopicState()
        self.odom = TopicState()
        self.map = TopicState()
        self.window_start = time.monotonic()

        self.pub = self.create_publisher(
            DiagnosticArray, self.get_parameter("diagnostics_topic").value, 10
        )
        self.create_subscription(
            LaserScan, self.get_parameter("scan_topic").value, lambda _m: self._mark(self.scan),
            qos_profile_sensor_data
        )
        self.create_subscription(
            Odometry, self.get_parameter("odom_topic").value, lambda _m: self._mark(self.odom),
            QoSProfile(depth=20)
        )
        self.create_subscription(
            OccupancyGrid, self.get_parameter("map_topic").value, lambda _m: self._mark(self.map),
            QoSProfile(depth=5)
        )
        self.create_timer(float(self.get_parameter("report_period_sec").value), self.report)

    @staticmethod
    def _mark(state: TopicState) -> None:
        state.count += 1
        state.last_monotonic = time.monotonic()

    @staticmethod
    def _topic_status(name: str, state: TopicState, hz: float, min_hz: float,
                      stale_sec: float, now: float) -> DiagnosticStatus:
        age = float("inf") if state.last_monotonic is None else now - state.last_monotonic
        if age > stale_sec:
            level, message = DiagnosticStatus.ERROR, "topic stale or missing"
        elif min_hz > 0 and hz < min_hz:
            level, message = DiagnosticStatus.WARN, "topic rate below target"
        else:
            level, message = DiagnosticStatus.OK, "healthy"
        return DiagnosticStatus(
            level=level,
            name=f"slam_robot_ros2/{name}",
            hardware_id="slam-inputs",
            message=message,
            values=[
                KeyValue(key="rate_hz", value=f"{hz:.3f}"),
                KeyValue(key="min_rate_hz", value=f"{min_hz:.3f}"),
                KeyValue(key="age_sec", value="inf" if age == float("inf") else f"{age:.3f}"),
                KeyValue(key="stale_after_sec", value=f"{stale_sec:.3f}"),
            ],
        )

    def report(self) -> None:
        now = time.monotonic()
        dt = max(now - self.window_start, 1e-6)
        statuses = [
            self._topic_status("scan", self.scan, self.scan.count / dt,
                               float(self.get_parameter("scan_min_hz").value),
                               float(self.get_parameter("scan_stale_sec").value), now),
            self._topic_status("odom", self.odom, self.odom.count / dt,
                               float(self.get_parameter("odom_min_hz").value),
                               float(self.get_parameter("odom_stale_sec").value), now),
            self._topic_status("map", self.map, self.map.count / dt, 0.0,
                               float(self.get_parameter("map_stale_sec").value), now),
        ]
        msg = DiagnosticArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.status = statuses
        self.pub.publish(msg)
        self.scan.count = self.odom.count = self.map.count = 0
        self.window_start = now

def main(args=None) -> None:
    rclpy.init(args=args)
    node = SlamHealthMonitor()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
