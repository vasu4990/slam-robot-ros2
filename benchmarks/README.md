# Benchmark Artifacts

Each benchmark run should be immutable and self-describing. Preserve the rosbag, copied parameter files, trajectory CSV, map / pose-graph output, ATE/RPE JSON, loop-closure JSON, resource profile, and a short environment manifest.

`scenarios.yaml` defines the expected artifacts. `thresholds.yaml` contains **simulation regression targets only**; it is not a source of hardware specifications.
