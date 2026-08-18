from glob import glob
from setuptools import find_packages, setup

package_name = "slam_robot_ros2"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
        ("share/" + package_name + "/urdf", glob("urdf/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Vivek Vala",
    maintainer_email="vivekvala562@gmail.com",
    description="Reference ROS 2 package for differential-drive LiDAR SLAM",
    license="MIT",
    entry_points={"console_scripts": ["diagnostics = slam_robot_ros2.diagnostics:main"]},
)
