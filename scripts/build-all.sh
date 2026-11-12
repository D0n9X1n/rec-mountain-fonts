#!/usr/bin/env bash
# build-all.sh — Build every family in configs/, one after another
#
# Families run in turn because each build already merges its four styles in
# parallel, and one CJK merge takes about 2.3 GB; three families at once
# exceed a 16 GB CI runner.
#
# Usage:
#   ./scripts/build-all.sh [cjk_scale]

set -euo pipefail
cd "$(dirname "$0")/.."

CJK_SCALE="${1:-1.15}"
CONFIGS=(configs/*.yaml)

# Fetch once up front
./scripts/fetch-sources.sh

LOGS=()
FAILED=0
for cfg in "${CONFIGS[@]}"; do
    log=$(mktemp)
    LOGS+=("$log")
    echo "Building ${cfg}..."
    if ./scripts/build.sh "$cfg" "$CJK_SCALE" > "$log" 2>&1; then
        echo "✓ ${cfg}"
    else
        echo "✗ ${cfg} FAILED (log below)"
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

# Check that the verifier still catches broken CJK spacing and weight
PYTHON=$([ -x venv/bin/python3 ] && echo venv/bin/python3 || echo python3)
"$PYTHON" scripts/test-verify-fonts.py

echo ""
echo "=== All fonts built ==="
ls -lh fonts/*/*.ttf
