#!/usr/bin/env bash
# No set -e — we want explicit error handling

echo "=========================================="
echo "OpenRCA Dataset Download — Market/cloudbed-2"
echo "=========================================="

echo "→ Free disk before: $(df -h . | tail -1 | awk '{print $4}')"
echo "→ Python: $(python3 --version)"
echo "→ Installing gdown..."

python3 -m pip install --quiet gdown 2>&1
echo "→ gdown installed: $(gdown --version 2>&1)"

echo ""
echo "→ Starting download from Google Drive folder: 1wGiEnu4OkWrjPxfx5ZTROnU37-5UDoPM"
echo "→ Output: dataset/"

gdown --folder "1wGiEnu4OkWrjPxfx5ZTROnU37-5UDoPM" -O dataset/ --continue 2>&1
GEXIT=$?

echo ""
echo "→ gdown exit code: $GEXIT"
echo "→ Free disk after: $(df -h . | tail -1 | awk '{print $4}')"

if [ $GEXIT -ne 0 ]; then
    echo "→ Checking if dataset/ was created anyway..."
    ls dataset/ 2>/dev/null || echo "  (no dataset/ directory)"
    if [ -d dataset/ ]; then
        echo "→ Dataset directory exists despite gdown error — proceeding"
    else
        echo "→ FATAL: gdown failed and no data was downloaded"
        exit 1
    fi
fi

echo ""
echo "→ Running date filter..."
python3 scripts/filter-dates.py 2>&1
FEXIT=$?
echo "→ filter exit code: $FEXIT"

echo ""
echo "→ Final dataset:"
du -sh dataset/ 2>/dev/null || echo "  (empty)"
echo ""
echo "✅ Done — Market/cloudbed-2"
