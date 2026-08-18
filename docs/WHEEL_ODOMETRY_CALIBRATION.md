# Wheel odometry calibration

Calibration is based on physical truth, not commands.

## Wheel radius

Perform multiple straight-line runs on a measured course. For each run record the physically measured travel distance and the odometry-reported travel distance. Add rows to the CSV template with `kind=straight`. The radius correction is the measured/odom distance ratio.

## Wheel separation

Perform multiple slow in-place rotations. Measure true yaw with an external reference (floor marks, calibrated IMU/reference tracker, or another defensible method) and record odometry yaw. Add rows with `kind=rotation`.

Run:

```bash
python tools/wheel_calibration.py calibration.csv \
  --nominal-radius 0.033 \
  --nominal-separation 0.26 \
  --output artifacts/hardware/wheel-calibration.json
```

Use several runs in both directions. Large spread between runs is evidence of slip/backlash or measurement weakness and should be investigated instead of averaged away.
