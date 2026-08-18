#!/usr/bin/env python3
"""Compute basic occupancy-image metrics for P2/P5 PGM maps."""
from __future__ import annotations
from pathlib import Path
import argparse, json

def _next_token(data: bytes, index: int) -> tuple[bytes, int]:
    n = len(data)
    while index < n:
        if data[index:index+1] == b"#":
            while index < n and data[index:index+1] not in (b"\n", b"\r"):
                index += 1
        elif data[index:index+1].isspace():
            index += 1
        else:
            break
    start = index
    while index < n and not data[index:index+1].isspace() and data[index:index+1] != b"#":
        index += 1
    if start == index:
        raise ValueError("unexpected end of PGM header")
    return data[start:index], index

def read_pgm(path: Path):
    data = path.read_bytes()
    idx = 0
    magic, idx = _next_token(data, idx)
    width_b, idx = _next_token(data, idx)
    height_b, idx = _next_token(data, idx)
    max_b, idx = _next_token(data, idx)
    magic = magic.decode("ascii")
    width, height, max_value = int(width_b), int(height_b), int(max_b)
    if max_value > 255:
        raise ValueError("16-bit PGM is not supported")
    if magic == "P2":
        tokens = []
        while True:
            try:
                tok, idx = _next_token(data, idx)
            except ValueError:
                break
            tokens.append(int(tok))
        pixels = tokens
    elif magic == "P5":
        while idx < len(data) and data[idx:idx+1].isspace():
            idx += 1
        pixels = list(data[idx:idx + width * height])
    else:
        raise ValueError("only P2/P5 PGM formats are supported")
    if len(pixels) != width * height:
        raise ValueError("pixel count does not match dimensions")
    return width, height, max_value, pixels

def summarize(path: Path) -> dict:
    width, height, max_value, pixels = read_pgm(path)
    occupied = sum(v < max_value * 0.35 for v in pixels)
    free = sum(v > max_value * 0.65 for v in pixels)
    unknown = len(pixels) - occupied - free
    return {
        "width_px": width, "height_px": height, "cells": len(pixels),
        "occupied_ratio": occupied / len(pixels),
        "free_ratio": free / len(pixels),
        "unknown_ratio": unknown / len(pixels),
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("map", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    metrics = summarize(a.map)
    text = json.dumps(metrics, indent=2)
    print(text)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(text + "\n")

if __name__ == "__main__":
    main()
