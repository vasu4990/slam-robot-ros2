from glob import glob
from setuptools import find_packages, setup

package_name = "slam_robot_ros2"

setup(
    name=package_name,
    version="0.2.0",
    packages=find_packages(exclude=["tests"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
        ("share/" + package_name + "/urdf", glob("urdf/*")),
        ("share/" + package_name + "/rviz", glob("rviz/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Vivek Vala",
    maintainer_email="vivekvala562@gmail.com",
    description="Engineering-grade ROS 2 LiDAR SLAM reference stack",
    license="MIT",
    entry_points={"console_scripts": [
        "diagnostics = slam_robot_ros2.diagnostics:main",
        "tf_monitor = slam_robot_ros2.tf_monitor:main",
        "synthetic_inputs = slam_robot_ros2.synthetic_inputs:main",
    ]},
)
