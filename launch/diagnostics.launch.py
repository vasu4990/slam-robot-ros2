from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg = Path(get_package_share_directory("slam_robot_ros2"))
    params = str(pkg / "config" / "diagnostics.yaml")
    return LaunchDescription([
        Node(package="slam_robot_ros2", executable="diagnostics",
             name="slam_health_monitor", output="screen", parameters=[params]),
        Node(package="slam_robot_ros2", executable="tf_monitor",
             name="slam_tf_monitor", output="screen", parameters=[params]),
    ])
