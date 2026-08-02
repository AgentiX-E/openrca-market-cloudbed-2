#!/usr/bin/env bash
set -euo pipefail
# Thin wrapper — delegates to selective Python downloader
pip3 install --quiet gdown
python3 scripts/download-dataset.py \
    "1wGiEnu4OkWrjPxfx5ZTROnU37-5UDoPM" \
    "Market" \
    "cloudbed-2" \
    2022_03_20 2022_03_21
