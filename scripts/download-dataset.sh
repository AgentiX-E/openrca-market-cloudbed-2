#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────────────
# OpenRCA Dataset Download Script
# Repo: openrca-market-cloudbed-2
# System: Market | Slice: cloudbed-2
# Dates: 2022_03_20, 2022_03_21
# Raw: ~9 GB | Compressed: ~4.5 GB
# ──────────────────────────────────────────────────────

GOOGLE_DRIVE_FOLDER="1wGiEnu4OkWrjPxfx5ZTROnU37-5UDoPM"
DATASET_ROOT="dataset"

echo "📥 Downloading OpenRCA dataset from Google Drive..."
echo "   Folder ID: ${GOOGLE_DRIVE_FOLDER}"
echo "   Target: Market — cloudbed-2 (2022_03_20, 2022_03_21)"

# Install gdown if missing
pip3 install --quiet gdown

# Download entire OpenRCA dataset (68 GB total, filtered after)
gdown --folder "${GOOGLE_DRIVE_FOLDER}" \
      -O "${DATASET_ROOT}/" \
      --remaining-ok

echo ""
echo "📂 Filtering to keep only target dates..."
python3 scripts/filter-dates.py

# Report size
echo ""
echo "📊 Dataset size after filtering:"
du -sh "${DATASET_ROOT}/" 2>/dev/null || true

echo ""
echo "✅ Download + filter complete for market-cb2"
