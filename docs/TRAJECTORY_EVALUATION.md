# Trajectory Evaluation

`trajectory_recorder` samples Gazebo ground truth and the SLAM estimate (`map -> base_footprint`) into one CSV. `tools/trajectory_metrics.py` performs best-fit **SE(2)** alignment with no scale correction, then reports absolute trajectory error (ATE), yaw error, and fixed-delta relative pose error (RPE).

No scale alignment is allowed because a metric LiDAR SLAM stack must preserve physical scale.
