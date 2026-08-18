# Gazebo Jetty Simulation

The reference simulator targets ROS 2 Lyrical with the default Gazebo Jetty pairing. `slam_lab.sdf` is a physics world with asymmetric walls and a loop-rich layout. The robot uses Gazebo's DiffDrive system for wheel odometry, a GPU lidar for `/scan`, and a separate OdometryPublisher with zero configured noise for `/ground_truth/odom`.

Run:
```bash
ros2 launch slam_robot_ros2 simulation.launch.py headless:=false
```

Full SLAM benchmark:
```bash
ros2 launch slam_robot_ros2 simulation_mapping.launch.py run_benchmark_driver:=true
```

The simulator is an engineering test environment, not proof of hardware performance.
