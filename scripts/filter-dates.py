#!/usr/bin/env python3
"""Filter OpenRCA dataset — keep only target date directories for this shard.

Repo: openrca-market-cloudbed-2
System: Market
Dates: 2022_03_20, 2022_03_21
"""

import shutil
import os

KEEP_DATES = [
        "2022_03_20",
        "2022_03_21",
    ]

DATASET_DIR = "dataset/Market/cloudbed-2/telemetry"


def main():
    if not os.path.isdir(DATASET_DIR):
        print(f"[SKIP] Dataset directory {DATASET_DIR} not found — nothing to filter")
        return

    all_dirs = sorted(os.listdir(DATASET_DIR))
    kept = []
    removed = []

    for d in all_dirs:
        dir_path = os.path.join(DATASET_DIR, d)
        if not os.path.isdir(dir_path):
            continue
        if d in KEEP_DATES:
            kept.append(d)
        else:
            print(f"  Removing: {d}")
            shutil.rmtree(dir_path)
            removed.append(d)

    print(f"\nFilter complete:")
    print(f"  Kept ({len(kept)}): {', '.join(kept)}")
    print(f"  Removed ({len(removed)}): {', '.join(removed) if removed else '(none)'}")

    # Verify all expected dates exist
    for expected in KEEP_DATES:
        if expected not in kept:
            print(f"[WARN] Expected date {expected} not found in dataset!")


if __name__ == "__main__":
    main()
