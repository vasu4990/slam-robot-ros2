from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg=Path(get_package_share_directory('slam_robot_ros2')); gz_pkg=Path(get_package_share_directory('ros_gz_sim'))
    world=str(pkg/'simulation'/'worlds'/'slam_lab.sdf'); models=str(pkg/'simulation'/'models'); bridge=str(pkg/'config'/'gazebo_bridge.yaml'); headless=LaunchConfiguration('headless')
    common=PythonLaunchDescriptionSource(str(gz_pkg/'launch'/'gz_sim.launch.py'))
    gz_headless=IncludeLaunchDescription(common,launch_arguments={'gz_args':f'-r -s --headless-rendering {world}'}.items(),condition=IfCondition(headless))
    gz_gui=IncludeLaunchDescription(common,launch_arguments={'gz_args':f'-r {world}'}.items(),condition=UnlessCondition(headless))
    rsp=IncludeLaunchDescription(PythonLaunchDescriptionSource(str(pkg/'launch'/'robot_state.launch.py')),launch_arguments={'use_sim_time':'true'}.items())
    ros_gz=Node(package='ros_gz_bridge',executable='parameter_bridge',name='gazebo_bridge',output='screen',parameters=[{'config_file':bridge}])
    return LaunchDescription([DeclareLaunchArgument('headless',default_value='true'),SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH',[models,':',EnvironmentVariable('GZ_SIM_RESOURCE_PATH',default_value='')]),gz_headless,gz_gui,ros_gz,rsp])
