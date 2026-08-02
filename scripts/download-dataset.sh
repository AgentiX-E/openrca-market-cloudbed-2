#!/usr/bin/env bash
set -euo pipefail

# OpenRCA Dataset Download — openrca-market-cloudbed-2
# System: Market | Slice: cloudbed-2
# Dates: 2022_03_20, 2022_03_21

echo "=========================================="
echo "OpenRCA Dataset Download"
echo "  System: Market"
echo "  Slice:  cloudbed-2"
echo "  Free disk before: $(df -h . | tail -1 | awk '{print $4}')"
echo "=========================================="

pip3 install --quiet gdown

echo ""
echo "📥 Downloading OpenRCA dataset from Google Drive..."
echo "   This downloads the entire dataset (~68GB raw, filtered after)"

gdown --folder "1wGiEnu4OkWrjPxfx5ZTROnU37-5UDoPM" \
      --no-cookies \
      -O dataset/ \
      --continue

echo ""
echo "📂 Free disk after download: $(df -h . | tail -1 | awk '{print $4}')"
echo "📂 Filtering to keep only target dates..."
python3 scripts/filter-dates.py

echo ""
echo "📊 Final dataset size:"
du -sh dataset/ 2>/dev/null || true
echo ""
echo "✅ Download + filter complete for Market-cloudbed-2"
