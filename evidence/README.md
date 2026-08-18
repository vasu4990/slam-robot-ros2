# Hardware evidence index

Commit compact, reviewable evidence here: manifests, calibration summaries, TF audits, map metrics, benchmark summaries and selected screenshots/logs.

Do **not** commit large raw rosbag databases by default. Keep raw bags in external storage or GitHub Actions artifacts and record their location/hash in the run manifest.

A valid hardware run must be explicitly marked `simulation: false` and identify the robot, operator, date, environment, hardware profile, rosbag, preflight result, TF audit and mapping artifacts.
