from glob import glob
from setuptools import setup

package_name = "slam_robot_ros2"

setup(
    name=package_name,
    version="0.1.0",
    packages=[],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Vivek Vala",
    maintainer_email="vivekvala562@gmail.com",
    description="ROS 2 SLAM Toolbox starter package for a differential-drive robot.",
    license="MIT",
)
