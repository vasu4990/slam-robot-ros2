from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression

def generate_launch_description():
    pkg = Path(get_package_share_directory("slam_robot_ros2"))
    mode = LaunchConfiguration("mode")
    use_sim_time = LaunchConfiguration("use_sim_time")
    map_file_name = LaunchConfiguration("map_file_name")
    mapping = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(pkg / "launch" / "mapping.launch.py")),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
        condition=IfCondition(PythonExpression(["'", mode, "' == 'mapping'"])),
    )
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(pkg / "launch" / "localization.launch.py")),
        launch_arguments={"use_sim_time": use_sim_time, "map_file_name": map_file_name}.items(),
        condition=IfCondition(PythonExpression(["'", mode, "' == 'localization'"])),
    )
    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="mapping",
                              description="mapping or localization"),
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        DeclareLaunchArgument("map_file_name", default_value=""),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(pkg / "launch" / "robot_state.launch.py")),
            launch_arguments={"use_sim_time": use_sim_time}.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(pkg / "launch" / "diagnostics.launch.py"))
        ),
        mapping,
        localization,
    ])
