#!/usr/bin/env python3
"""Static consistency checks for Gazebo model, world, bridge and benchmark contracts."""
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml
ROOT=Path(__file__).resolve().parents[1]
def main():
 ET.parse(ROOT/'simulation/models/slam_robot/model.sdf');ET.parse(ROOT/'simulation/worlds/slam_lab.sdf')
 text=(ROOT/'simulation/models/slam_robot/model.sdf').read_text()
 for token in ['gz-sim-diff-drive-system','gz-sim-odometry-publisher-system','gpu_lidar','/model/slam_robot/ground_truth','/model/slam_robot/odometry','/scan']:assert token in text,f'missing {token}'
 assert 'model://slam_robot' in (ROOT/'simulation/worlds/slam_lab.sdf').read_text()
 bridges=yaml.safe_load((ROOT/'config/gazebo_bridge.yaml').read_text());pairs={(b['ros_topic_name'],b['direction']) for b in bridges}
 for pair in [('/scan','GZ_TO_ROS'),('/odom','GZ_TO_ROS'),('/ground_truth/odom','GZ_TO_ROS'),('/cmd_vel','ROS_TO_GZ'),('/clock','GZ_TO_ROS')]:assert pair in pairs,pair
 path=yaml.safe_load((ROOT/'config/benchmark_path.yaml').read_text());assert path['simulation_only'] is True and len(path['segments'])>=8
 print('simulation contracts: PASS')
if __name__=='__main__':main()
