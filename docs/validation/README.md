# Validation Evidence

Store reproducible evidence here or link to immutable artifacts/releases.

Suggested structure:

```text
validation/
  <date>-<test-name>/
    README.md
    environment.yaml
    commands.txt
    metrics.json
    screenshots/
```

Do not commit enormous rosbag files directly to Git. Store them in an appropriate artifact/object store and record a stable identifier/checksum here.
