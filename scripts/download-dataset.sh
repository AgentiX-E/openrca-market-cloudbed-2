#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo "OpenRCA Dataset Download"
echo "  System:   Market"
echo "  CloudBed: cloudbed-2"
echo "  Dates:    2022_03_20 2022_03_21"
echo "  Free disk: $(df -h . | tail -1 | awk '{print $4}')"
echo "=========================================="

pip3 install --quiet gdown
python3 scripts/download-dataset.py     "1wGiEnu4OkWrjPxfx5ZTROnU37-5UDoPM"     "Market"     "cloudbed-2"     2022_03_20 2022_03_21

echo ""
echo "Final dataset size:"
du -sh dataset/ 2>/dev/null || true
echo "Done."
