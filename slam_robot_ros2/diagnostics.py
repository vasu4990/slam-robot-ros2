import time

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class InputRateDiagnostics(Node):
    def __init__(self):
        super().__init__("slam_input_diagnostics")
        self.scan_count = 0
        self.odom_count = 0
        self.window_start = time.monotonic()
        self.create_subscription(LaserScan, "/scan", self.on_scan, 10)
        self.create_subscription(Odometry, "/odom", self.on_odom, 20)
        self.create_timer(5.0, self.report)

    def on_scan(self, _msg):
        self.scan_count += 1

    def on_odom(self, _msg):
        self.odom_count += 1

    def report(self):
        now = time.monotonic()
        dt = max(now - self.window_start, 1e-6)
        scan_hz = self.scan_count / dt
        odom_hz = self.odom_count / dt
        self.get_logger().info(f"input rates: /scan={scan_hz:.1f} Hz, /odom={odom_hz:.1f} Hz")
        if self.scan_count == 0:
            self.get_logger().warning("no /scan messages received in the last window")
        if self.odom_count == 0:
            self.get_logger().warning("no /odom messages received in the last window")
        self.scan_count = 0
        self.odom_count = 0
        self.window_start = now


def main(args=None):
    rclpy.init(args=args)
    node = InputRateDiagnostics()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
