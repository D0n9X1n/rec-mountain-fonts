#!/usr/bin/env bash
# build-all.sh — Build every family in configs/ in parallel
#
# Usage:
#   ./scripts/build-all.sh [cjk_scale]

set -euo pipefail
cd "$(dirname "$0")/.."

CJK_SCALE="${1:-1.15}"
CONFIGS=(configs/*.yaml)

# Fetch once up front so the parallel builds don't download at the same time
./scripts/fetch-sources.sh

PIDS=()
LOGS=()
for cfg in "${CONFIGS[@]}"; do
    log=$(mktemp)
    LOGS+=("$log")
    echo "Starting ${cfg}..."
    ./scripts/build.sh "$cfg" "$CJK_SCALE" > "$log" 2>&1 &
    PIDS+=($!)
done

FAILED=0
for i in "${!PIDS[@]}"; do
    if wait "${PIDS[$i]}"; then
        echo "✓ ${CONFIGS[$i]}"
    else
        echo "✗ ${CONFIGS[$i]} FAILED (log below)"
        FAILED=1
    fi
done

for i in "${!CONFIGS[@]}"; do
    echo ""
    echo "──────── ${CONFIGS[$i]} ────────"
    cat "${LOGS[$i]}"
    rm -f "${LOGS[$i]}"
done

if [ "$FAILED" -ne 0 ]; then
    echo "=== Some builds failed ==="
    exit 1
fi

echo ""
echo "=== All fonts built ==="
ls -lh fonts/*/*.ttf
