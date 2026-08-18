#!/usr/bin/env python3
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_LINKS = {"base_footprint", "base_link", "laser_link"}
REQUIRED_JOINTS = {"base_footprint_joint", "laser_joint"}

def lint(path: Path = ROOT / "urdf/robot.urdf.xacro") -> list[str]:
    tree = ET.parse(path)
    robot = tree.getroot()
    links = {e.attrib.get("name") for e in robot.findall("link")}
    joints = {e.attrib.get("name"): e.attrib.get("type") for e in robot.findall("joint")}
    errors = []
    for name in REQUIRED_LINKS - links:
        errors.append(f"missing link {name}")
    for name in REQUIRED_JOINTS - set(joints):
        errors.append(f"missing joint {name}")
    if joints.get("base_footprint_joint") != "fixed":
        errors.append("base_footprint_joint must be fixed")
    if joints.get("laser_joint") != "fixed":
        errors.append("laser_joint must be fixed")
    if "map" in links or "odom" in links:
        errors.append("map/odom must not be modeled as URDF links")
    return errors

def main():
    errors = lint()
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        raise SystemExit(1)
    print("URDF static contract: PASS")

if __name__ == "__main__":
    main()
