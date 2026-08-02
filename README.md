# openrca-market-cloudbed-2

> OpenRCA data shard repository — Market (cloudbed-2)

## Overview

This repository hosts the **Market** dataset slice for the OpenRCA multi-project benchmark.
It provides cached telemetry data and prediction workflows for three RCA projects.

| Property | Value |
|----------|-------|
| System | Market |
| Slice | cloudbed-2 |
| Cache Key | `market-cb2-v1` |
| Raw Size | ~9 GB |
| Compressed | ~4.5 GB |

## Date Coverage

- `2022_03_20`
- `2022_03_21`

## Architecture

```
openrca-market-cloudbed-2/
├── .github/workflows/
│   ├── prediction-causality-analyzer.yml   # CA-LLM agent prediction
│   ├── prediction-micro-kinetic-py.yml     # MicroKinetic Python prediction
│   └── prediction-micro-kinetic-ts.yml     # MicroKinetic TypeScript prediction
├── scripts/
│   ├── download-dataset.sh                 # gdown download + date filter
│   └── filter-dates.py                     # Keep only target dates
└── README.md
```

## Workflows

All three prediction workflows follow the same pattern:

1. **Restore cache** — `actions/cache@v4` with key `market-cb2-v1`
2. **Cache miss → download** — `gdown` from Google Drive, filter to target dates
3. **Clone + build** the target project repo
4. **Run prediction** with `DEEPSEEK_API_KEY`
5. **Upload predictions** as artifact (90-day retention)

## Secrets Required

| Secret | Purpose |
|--------|---------|
| `DEEPSEEK_API_KEY` | LLM API key for RCA agent inference |

## Cache Strategy

- **Key**: `market-cb2-v1`
- **Path**: `dataset/`
- **Invalidation**: Bump version suffix (`v1 → v2`) if dataset changes
- **First run**: ~15 min download + ~30-60 min prediction
- **Cached runs**: ~30-60 min prediction only

## Downstream Consumers

Predictions uploaded as artifacts are consumed by evaluation workflows in:
- `AgentiX-E/causality-analyzer`
- `AgentiX-E/micro-kinetic-py`
- `AgentiX-E/micro-kinetic-ts`

Artifact name format: `predictions-{project}-market-cb2`
