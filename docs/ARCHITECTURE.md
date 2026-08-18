# System Architecture

The repository owns the **SLAM integration layer**. It does not pretend to own hardware-specific LiDAR firmware or wheel-encoder/base drivers.

```mermaid
flowchart LR
    L[LiDAR driver] -->|sensor_msgs/LaserScan| S[slam_toolbox]
    B[Base driver / EKF] -->|nav_msgs/Odometry| S
    B -->|odom -> base_footprint TF| TF[TF tree]
    R[robot_state_publisher] -->|base_footprint -> base_link -> laser_link| TF
    S -->|map -> odom TF| TF
    S -->|nav_msgs/OccupancyGrid| M[/map]
    L --> H[health monitor]
    B --> H
    M --> H
    TF --> T[TF monitor]
    H --> D[/diagnostics]
    T --> D
```

## Ownership boundaries

| Responsibility | Owner |
|---|---|
| `map -> odom` | `slam_toolbox` |
| `odom -> base_footprint` | base odometry / state estimator |
| `base_footprint -> base_link` | robot description |
| `base_link -> laser_link` | robot description |
| `/scan` timestamps/frame/range validity | LiDAR driver |
| `/odom` continuity/covariance | base driver / state estimator |
| mapping/localization lifecycle | this package |
| input/TF diagnostics | this package |

Two different nodes must never publish the same TF edge. In particular, this package does **not** publish `odom -> base_footprint`.
