# Contributing

Contributions should improve reproducibility, correctness or integration without inventing hardware evidence.

Before opening a PR:

```bash
python -m pip install -r requirements-dev.txt
pytest -q
python tools/config_lint.py
python tools/urdf_lint.py
python tools/release_gate.py reference
```

For ROS-facing changes, also build and test in the reference ROS distribution.

Requirements:
- preserve TF ownership rules;
- document new topics/frames/parameters;
- keep hardware geometry marked unvalidated until measured;
- add tests for pure-Python logic;
- include a rosbag/simulation reproduction when changing SLAM behavior based on observed performance.
