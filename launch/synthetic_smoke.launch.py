from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg = Path(get_package_share_directory("slam_robot_ros2"))
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(pkg / "launch" / "robot_state.launch.py"))
        ),
        Node(package="slam_robot_ros2", executable="synthetic_inputs",
             name="synthetic_slam_inputs", output="screen"),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(pkg / "launch" / "diagnostics.launch.py"))
        ),
    ])
