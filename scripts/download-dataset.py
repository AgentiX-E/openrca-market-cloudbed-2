#!/usr/bin/env python3
"""Selective OpenRCA downloader with fallback to full download."""
import os, sys, subprocess

folder_id = sys.argv[1]
system = sys.argv[2]
cloudbed = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else ""
target_dates = set(sys.argv[4:]) if len(sys.argv) > 4 else set()

print(f"Selective download: system={system}, cloudbed={cloudbed}, dates={sorted(target_dates)}")

# Build path prefix
if cloudbed:
    prefix = f"dataset/{system}/{cloudbed}/"
else:
    prefix = f"dataset/{system}/"

try:
    import gdown
except ImportError:
    print("FATAL: gdown not installed")
    sys.exit(1)

# Try selective listing first
print("\nTrying selective listing via gdown API...")
try:
    entries = gdown.download_folder(
        id=folder_id, output="/tmp/gdown_list", quiet=False,
        use_cookies=False, skip_download=True,
    )
    if entries:
        print(f"  Got {len(entries)} entries from gdown API")
        matching = []
        for e in entries:
            try:
                if prefix in e.path:
                    matching.append((e.id, e.path))
            except:
                pass
        print(f"  Matching: {len(matching)} files")
        
        if matching:
            ok = 0
            for i, (fid, path) in enumerate(matching):
                out = os.path.join("dataset", path)
                os.makedirs(os.path.dirname(out), exist_ok=True)
                if os.path.exists(out):
                    ok += 1
                    continue
                print(f"  [{i+1}/{len(matching)}] {path}")
                try:
                    gdown.download(id=fid, output=out, quiet=True, use_cookies=False)
                    if os.path.exists(out):
                        ok += 1
                except Exception as e:
                    print(f"    ERROR: {e}")
            print(f"\nDownloaded {ok}/{len(matching)} files")
            if ok > 0:
                subprocess.run(["python3", "scripts/filter-dates.py"], check=False)
                subprocess.run(["du", "-sh", "dataset/"], check=False)
                print("Selective download SUCCESS")
                sys.exit(0)
except Exception as e:
    print(f"Selective listing failed: {type(e).__name__}: {e}")

# Fallback: full download
print("\nFalling back to full dataset download...")
print("(This downloads the entire 68GB OpenRCA dataset)")
result = subprocess.run(
    ["gdown", "--folder", folder_id, "-O", "dataset/", "--no-cookies", "--continue"],
    timeout=7200,
)
if result.returncode != 0:
    print(f"Full download failed (exit {result.returncode})")
    sys.exit(1)

subprocess.run(["python3", "scripts/filter-dates.py"], check=False)
subprocess.run(["du", "-sh", "dataset/"], check=False)
print("Full download SUCCESS")
