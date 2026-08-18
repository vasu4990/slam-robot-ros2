"""Deterministic synthetic scan/odometry publisher for ROS graph smoke tests.

This is not a physics simulator and must never be used as SLAM performance evidence.
"""
from __future__ import annotations
import math
import rclpy
from geometry_msgs.msg import Quaternion, TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from tf2_ros import TransformBroadcaster

def yaw_to_quaternion(yaw: float) -> Quaternion:
    q = Quaternion()
    q.z = math.sin(yaw * 0.5)
    q.w = math.cos(yaw * 0.5)
    return q

class SyntheticInputs(Node):
    def __init__(self) -> None:
        super().__init__("synthetic_slam_inputs")
        self.declare_parameter("scan_hz", 10.0)
        self.declare_parameter("odom_hz", 30.0)
        self.scan_pub = self.create_publisher(LaserScan, "/scan", 10)
        self.odom_pub = self.create_publisher(Odometry, "/odom", 20)
        self.tf = TransformBroadcaster(self)
        self.start_ns = self.get_clock().now().nanoseconds
        self.create_timer(1.0 / float(self.get_parameter("scan_hz").value), self.publish_scan)
        self.create_timer(1.0 / float(self.get_parameter("odom_hz").value), self.publish_odom)

    def elapsed(self) -> float:
        return (self.get_clock().now().nanoseconds - self.start_ns) / 1e9

    def publish_scan(self) -> None:
        now = self.get_clock().now()
        count = 360
        msg = LaserScan()
        msg.header.stamp = now.to_msg()
        msg.header.frame_id = "laser_link"
        msg.angle_min = -math.pi
        msg.angle_max = math.pi
        msg.angle_increment = 2.0 * math.pi / count
        msg.time_increment = 0.0
        msg.scan_time = 1.0 / float(self.get_parameter("scan_hz").value)
        msg.range_min = 0.10
        msg.range_max = 12.0
        phase = self.elapsed() * 0.2
        msg.ranges = [3.0 + 0.35 * math.sin(i * 0.07 + phase) for i in range(count)]
        self.scan_pub.publish(msg)

    def publish_odom(self) -> None:
        now = self.get_clock().now()
        t = self.elapsed()
        x = 0.05 * t
        y = 0.10 * math.sin(t * 0.2)
        yaw = 0.02 * math.sin(t * 0.1)
        odom = Odometry()
        odom.header.stamp = now.to_msg()
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_footprint"
        odom.pose.pose.position.x = x
        odom.pose.pose.position.y = y
        odom.pose.pose.orientation = yaw_to_quaternion(yaw)
        odom.twist.twist.linear.x = 0.05
        self.odom_pub.publish(odom)

        tf = TransformStamped()
        tf.header = odom.header
        tf.child_frame_id = odom.child_frame_id
        tf.transform.translation.x = x
        tf.transform.translation.y = y
        tf.transform.rotation = odom.pose.pose.orientation
        self.tf.sendTransform(tf)

def main(args=None) -> None:
    rclpy.init(args=args)
    node = SyntheticInputs()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
