#!/usr/bin/env python3
"""Selective OpenRCA dataset downloader.

Uses gdown --json to list ALL files in the Google Drive folder,
then downloads ONLY files matching the target date paths.
This avoids downloading the entire 68GB dataset.

Usage:
    python3 scripts/download-dataset.py <folder_id> <system> <dates...>

Target path filter:
    Telecom → dataset/Telecom/telemetry/{date}/
    Bank    → dataset/Bank/telemetry/{date}/
    Market  → dataset/Market/{cloudbed}/telemetry/{date}/
"""

import json
import os
import subprocess
import sys
from pathlib import Path

FOLDER_ID = sys.argv[1] if len(sys.argv) > 1 else "1wGiEnu4OkWrjPxfx5ZTROnU37-5UDoPM"
SYSTEM = sys.argv[2] if len(sys.argv) > 2 else "Telecom"
CLOUDBED = sys.argv[3] if len(sys.argv) > 3 else ""  # cloudbed-1 / cloudbed-2
TARGET_DATES = sys.argv[4:] if len(sys.argv) > 4 else []

print("=" * 60)
print("OpenRCA Selective Dataset Downloader")
print("=" * 60)
print(f"  Folder:   {FOLDER_ID}")
print(f"  System:   {SYSTEM}")
print(f"  CloudBed: {CLOUDBED or '(none)'}")
print(f"  Dates:    {TARGET_DATES}")


def build_path_filter():
    """Build the path prefix that files must match to be downloaded."""
    if CLOUDBED:
        return f"dataset/{SYSTEM}/{CLOUDBED}/"
    return f"dataset/{SYSTEM}/"


def list_folder_files(folder_id: str):
    """List all files in a Google Drive folder using gdown --json."""
    print(f"\n📋 Listing folder contents...")
    result = subprocess.run(
        ["gdown", "--folder", "--json", folder_id],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print(f"[ERROR] gdown --json failed (exit {result.returncode})")
        print(f"  stdout: {result.stdout[:500]}")
        print(f"  stderr: {result.stderr[:500]}")
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON: {e}")
        print(f"  Raw output (first 500 chars): {result.stdout[:500]}")
        return []

    print(f"  Total entries in folder: {len(data)}")
    return data


def download_file(file_id: str, output_path: str):
    """Download a single file from Google Drive by ID."""
    out_dir = os.path.dirname(output_path)
    os.makedirs(out_dir, exist_ok=True)

    result = subprocess.run(
        ["gdown", "--no-cookies", file_id, "-O", output_path],
        capture_output=True,
        text=True,
        timeout=300,
    )
    return result.returncode == 0


def main():
    # Step 1: List all files
    entries = list_folder_files(FOLDER_ID)
    if not entries:
        print("\n[FATAL] Cannot list folder contents. Aborting.")
        sys.exit(1)

    # Step 2: Filter files by target path
    path_filter = build_path_filter()
    print(f"\n🔍 Filtering files by prefix: '{path_filter}'")

    matching = []
    skipped = 0
    for entry in entries:
        path = entry.get("path", "")
        file_id = entry.get("id", "")
        name = entry.get("name", "")
        is_dir = entry.get("type") == "folder" or entry.get("type") == "directory"

        # Skip directories (gdown lists them but we only care about files)
        if is_dir:
            # But we still track directory entries for debugging
            if path_filter in path:
                matching.append(entry)
            continue

        # Check if file path matches our target prefix
        if path_filter in path:
            matching.append(entry)
        else:
            skipped += 1

    print(f"  Matching: {len(matching)} files")
    print(f"  Skipped:  {skipped} files (outside target system)")

    if not matching:
        print(f"\n[WARN] No files match prefix '{path_filter}'")
        print("  First 10 available paths:")
        for e in entries[:10]:
            print(f"    {e.get('path', 'N/A')}")
        sys.exit(1)

    # Step 3: Download matching files
    print(f"\n📥 Downloading {len(matching)} matching files...")
    success = 0
    failed = 0
    total_size = 0

    for i, entry in enumerate(matching):
        path = entry.get("path", "")
        file_id = entry.get("id", "")
        size_bytes = int(entry.get("size", 0))
        total_size += size_bytes

        # Determine output path under dataset/
        output_path = os.path.join("dataset", path)

        if os.path.exists(output_path):
            print(f"  [{i+1}/{len(matching)}] SKIP (exists): {path}")
            success += 1
            continue

        size_mb = size_bytes / (1024 * 1024) if size_bytes else 0
        print(f"  [{i+1}/{len(matching)}] {size_mb:.1f}MB  {path}")

        if download_file(file_id, output_path):
            success += 1
        else:
            print(f"    ❌ Download failed!")
            failed += 1

    total_gb = total_size / (1024 * 1024 * 1024)
    print(f"\n📊 Download summary:")
    print(f"  Total size:   {total_gb:.2f} GB")
    print(f"  Downloaded:   {success} files")
    if failed:
        print(f"  Failed:       {failed} files")
        sys.exit(1)

    # Step 4: Run filter script to remove non-target dates
    print(f"\n📂 Running date-level filter...")
    subprocess.run(["python3", "scripts/filter-dates.py"], check=False)

    # Report final size
    print(f"\n📊 Final dataset size:")
    subprocess.run(["du", "-sh", "dataset/"], check=False)

    print(f"\n✅ Selective download complete for {SYSTEM}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
