# Failure Modes

| Symptom | Likely causes | First checks |
|---|---|---|
| Map rotates/drifts badly | wheel calibration, slip, bad LiDAR extrinsic | odom trajectory, wheel separation, `laser_link` |
| Scan appears offset in RViz | wrong sensor transform | `base_link -> laser_link` |
| Message filter drops scans | missing/late TF, timestamp mismatch | TF at scan timestamp, clock source |
| Map duplicates corridors | odom drift / weak scan matching | bag replay, wheel calibration, speed |
| Catastrophic loop closure | ambiguous environment / aggressive thresholds | pose graph, loop thresholds |
| No map update | SLAM lifecycle inactive, stale scan, TF unavailable | node lifecycle, diagnostics |
| Robot jumps in map | odom reset or conflicting TF publisher | TF authorities, base driver |
| Localization never converges | wrong serialized map/start pose/input geometry | map path, TF, scan alignment |

Treat warnings as evidence to investigate, not as reasons to randomly change many parameters at once.
