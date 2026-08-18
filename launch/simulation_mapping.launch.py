from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg=Path(get_package_share_directory('slam_robot_ros2')); headless=LaunchConfiguration('headless'); drive=LaunchConfiguration('run_benchmark_driver'); record=LaunchConfiguration('record_trajectory')
    sim=IncludeLaunchDescription(PythonLaunchDescriptionSource(str(pkg/'launch'/'simulation.launch.py')),launch_arguments={'headless':headless}.items())
    slam=IncludeLaunchDescription(PythonLaunchDescriptionSource(str(pkg/'launch'/'mapping.launch.py')),launch_arguments={'use_sim_time':'true','scan_topic':'/scan'}.items())
    diag=IncludeLaunchDescription(PythonLaunchDescriptionSource(str(pkg/'launch'/'diagnostics.launch.py')),launch_arguments={'use_sim_time':'true'}.items())
    recorder=Node(package='slam_robot_ros2',executable='trajectory_recorder',parameters=[{'use_sim_time':True}],condition=IfCondition(record),output='screen')
    driver=Node(package='slam_robot_ros2',executable='benchmark_driver',parameters=[{'use_sim_time':True}],condition=IfCondition(drive),output='screen')
    return LaunchDescription([DeclareLaunchArgument('headless',default_value='true'),DeclareLaunchArgument('run_benchmark_driver',default_value='false'),DeclareLaunchArgument('record_trajectory',default_value='true'),sim,slam,diag,recorder,driver])
