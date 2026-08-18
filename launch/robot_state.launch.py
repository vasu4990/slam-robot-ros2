from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg = Path(get_package_share_directory("slam_robot_ros2"))
    model = str(pkg / "urdf" / "robot.urdf.xacro")
    use_sim_time = LaunchConfiguration("use_sim_time")
    robot_description = ParameterValue(Command(["xacro", " ", model]), value_type=str)
    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description, "use_sim_time": use_sim_time}],
        ),
    ])
