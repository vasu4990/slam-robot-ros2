from glob import glob
from setuptools import find_packages, setup

package_name = "slam_robot_ros2"

setup(
    name=package_name,
    version="0.4.0",
    packages=find_packages(exclude=["tests"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
        ("share/" + package_name + "/urdf", glob("urdf/*")),
        ("share/" + package_name + "/rviz", glob("rviz/*")),
        ("share/" + package_name + "/simulation/worlds", glob("simulation/worlds/*")),
        ("share/" + package_name + "/simulation/models/slam_robot", glob("simulation/models/slam_robot/*")),
        ("share/" + package_name + "/benchmarks", glob("benchmarks/*")),
        ("share/" + package_name + "/scripts", glob("scripts/*")),
    ],
    install_requires=["setuptools"],
    tests_require=["pytest"],
    zip_safe=True,
    maintainer="Vivek Vala",
    maintainer_email="vivekvala562@gmail.com",
    description="Engineering-grade ROS 2 LiDAR SLAM stack with Gazebo ground-truth benchmarking and hardware-evidence capture",
    license="MIT",
    entry_points={"console_scripts": [
        "diagnostics = slam_robot_ros2.diagnostics:main",
        "tf_monitor = slam_robot_ros2.tf_monitor:main",
        "synthetic_inputs = slam_robot_ros2.synthetic_inputs:main",
        "trajectory_recorder = slam_robot_ros2.trajectory_recorder:main",
        "benchmark_driver = slam_robot_ros2.benchmark_driver:main",
        "hardware_audit = slam_robot_ros2.hardware_audit:main",
    ]},
)
