#!/usr/bin/env python3
"""Selective OpenRCA dataset downloader (v4).

Uses gdown.download_folder(skip_download=True) to list files WITHOUT downloading,
filters by target system/date paths, then downloads only matching files.

Usage:
    python3 scripts/download-dataset.py <folder_id> <system> [cloudbed] <dates...>

Target path filters:
    Telecom → dataset/Telecom/telemetry/{date}/
    Bank    → dataset/Bank/telemetry/{date}/
    Market  → dataset/Market/{cloudbed}/telemetry/{date}/
"""

import os
import sys
import subprocess
from pathlib import Path

FOLDER_ID = sys.argv[1] if len(sys.argv) > 1 else "1wGiEnu4OkWrjPxfx5ZTROnU37-5UDoPM"
SYSTEM = sys.argv[2] if len(sys.argv) > 2 else "Telecom"
CLOUDBED = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else ""
TARGET_DATES = set(sys.argv[4:]) if len(sys.argv) > 4 else set()

print("=" * 60)
print("OpenRCA Selective Dataset Downloader (v4)")
print("=" * 60)
print(f"  Folder:   {FOLDER_ID}")
print(f"  System:   {SYSTEM}")
print(f"  CloudBed: {CLOUDBED or '(none)'}")
print(f"  Dates:    {sorted(TARGET_DATES)}")

# Build path prefix filter
if CLOUDBED:
    PATH_PREFIX = f"dataset/{SYSTEM}/{CLOUDBED}/"
else:
    PATH_PREFIX = f"dataset/{SYSTEM}/"


def list_files(folder_id: str):
    """List all files in folder using gdown Python API (no download)."""
    print(f"\n📋 Listing folder contents (skip_download mode)...")

    try:
        import gdown
        entries = gdown.download_folder(
            id=folder_id,
            output="/tmp/gdown_list",
            quiet=True,
            use_cookies=False,
            skip_download=True,
        )

        if not entries:
            print("[ERROR] gdown returned empty list")
            return []

        # entries is a list of GoogleDriveFileToDownload named tuples
        # Each has: id, path, local_path
        result = []
        for e in entries:
            result.append({
                "id": e.id,
                "path": e.path,
            })

        print(f"  Total entries: {len(result)}")
        return result

    except ImportError:
        print("[FATAL] gdown not installed")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Listing failed: {type(e).__name__}: {e}")
        return []


def download_one(file_id: str, output_path: str) -> bool:
    """Download a single file by Google Drive ID."""
    out_dir = os.path.dirname(output_path)
    os.makedirs(out_dir, exist_ok=True)

    if os.path.exists(output_path):
        return True  # Already downloaded

    try:
        import gdown
        gdown.download(id=file_id, output=output_path, quiet=True, use_cookies=False)
        return os.path.exists(output_path)
    except Exception as e:
        print(f"    ❌ Download error: {e}")
        return False


def main():
    # Step 1: List
    entries = list_files(FOLDER_ID)
    if not entries:
        print("\n[FATAL] Cannot list folder contents. Aborting.")
        sys.exit(1)

    # Show some sample paths for debugging
    print(f"\n  Sample paths (first 10):")
    for e in entries[:10]:
        print(f"    {e['path']}")

    # Step 2: Filter
    print(f"\n🔍 Filtering by prefix: '{PATH_PREFIX}'")
    matching = []
    for e in entries:
        p = e["path"]
        if PATH_PREFIX in p:
            matching.append(e)

    print(f"  Matching files: {len(matching)}")

    if not matching:
        # Show what paths are available for this system
        print(f"\n[WARN] No files match prefix '{PATH_PREFIX}'")
        print(f"  Available paths containing '{SYSTEM}':")
        for e in entries:
            if SYSTEM in e["path"]:
                print(f"    {e['path']}")
        sys.exit(1)

    # Step 3: Download matching files
    print(f"\n📥 Downloading {len(matching)} files...")
    success = 0
    failed = 0

    for i, entry in enumerate(matching):
        path = entry["path"]
        file_id = entry["id"]
        output_path = os.path.join("dataset", path)

        print(f"  [{i+1}/{len(matching)}] {path}")
        if download_one(file_id, output_path):
            success += 1
        else:
            failed += 1

    print(f"\n📊 Summary: {success} downloaded, {failed} failed")

    if failed > 0:
        sys.exit(1)

    # Step 4: Run filter-dates.py to remove non-target dates
    print(f"\n📂 Running date-level filter...")
    subprocess.run(["python3", "scripts/filter-dates.py"], check=False)

    # Report
    print(f"\n📊 Final dataset size:")
    subprocess.run(["du", "-sh", "dataset/"], check=False)
    subprocess.run(["find", "dataset/", "-type", "d"], check=False)

    print(f"\n✅ Selective download complete for {SYSTEM}")


if __name__ == "__main__":
    main()
