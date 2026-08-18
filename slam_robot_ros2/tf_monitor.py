"""Monitor the core SLAM TF contract and publish standard ROS diagnostics."""
from __future__ import annotations
import rclpy
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener

class TfHealthMonitor(Node):
    def __init__(self) -> None:
        super().__init__("slam_tf_monitor")
        self.declare_parameter("diagnostics_topic", "/diagnostics")
        self.declare_parameter("odom_frame", "odom")
        self.declare_parameter("base_frame", "base_footprint")
        self.declare_parameter("laser_frame", "laser_link")
        self.declare_parameter("tf_stale_sec", 1.0)
        self.declare_parameter("report_period_sec", 1.0)
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.pub = self.create_publisher(
            DiagnosticArray, self.get_parameter("diagnostics_topic").value, 10
        )
        self.create_timer(float(self.get_parameter("report_period_sec").value), self.report)

    def _check(self, parent: str, child: str) -> DiagnosticStatus:
        try:
            tf = self.buffer.lookup_transform(
                parent, child, Time(), timeout=Duration(seconds=0.15)
            )
            stamp = rclpy.time.Time.from_msg(tf.header.stamp)
            age = max(0.0, (self.get_clock().now() - stamp).nanoseconds / 1e9)
            limit = float(self.get_parameter("tf_stale_sec").value)
            level = DiagnosticStatus.OK if age <= limit else DiagnosticStatus.WARN
            message = "transform available" if level == DiagnosticStatus.OK else "transform stale"
            values = [KeyValue(key="age_sec", value=f"{age:.3f}")]
        except TransformException as exc:
            level, message = DiagnosticStatus.ERROR, "transform unavailable"
            values = [KeyValue(key="error", value=str(exc))]
        return DiagnosticStatus(
            level=level, name=f"slam_robot_ros2/tf/{parent}->{child}",
            hardware_id="tf-tree", message=message, values=values
        )

    def report(self) -> None:
        odom = str(self.get_parameter("odom_frame").value)
        base = str(self.get_parameter("base_frame").value)
        laser = str(self.get_parameter("laser_frame").value)
        msg = DiagnosticArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.status = [self._check(odom, base), self._check(base, laser)]
        self.pub.publish(msg)

def main(args=None) -> None:
    rclpy.init(args=args)
    node = TfHealthMonitor()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
