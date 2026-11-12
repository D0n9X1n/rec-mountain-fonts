#!/usr/bin/env bash
# build.sh — Build one font family: Recursive or Anthropic Serif + Resource Han Rounded + Nerd Fonts
#
# Usage:
#   ./scripts/build.sh <config.yaml> [cjk_scale]
#
# Examples:
#   ./scripts/build.sh configs/st-helens.yaml
#   ./scripts/build.sh configs/mt-baker.yaml 1.2

set -euo pipefail
cd "$(dirname "$0")/.."

CONFIG="${1:?Usage: $0 <config.yaml> [cjk_scale]}"
CJK_SCALE="${2:-1.15}"

if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi

./scripts/fetch-sources.sh
source versions.env
eval "$(python3 scripts/fontconfig.py "$CONFIG")"  # FAMILY, COMPACT, MONO, BASE

if [ "$BASE" = recursive ]; then
    LATIN="Recursive ${RECURSIVE_VERSION}"
    LATIN_SOURCES=("sources/recursive/Recursive_VF_${RECURSIVE_VERSION}.ttf" "sources/recursive/calt-generated--code_fonts_only.fea")
else
    LATIN="Anthropic Serif ${ANTHROPIC_SERIF_VERSION}"
    LATIN_SOURCES=("sources/anthropic-serif")
fi
CJK_DIR="sources/resource-han-rounded"
PATCHER="sources/nerd-fonts-patcher/font-patcher"

WORK="build/${COMPACT}"
OUT="fonts/${COMPACT}"
STYLES=(Regular Italic Bold BoldItalic)

# Proportional families keep proportional CJK advances and natural-width icons
if [ "$MONO" = 1 ]; then
    CJK_FLAGS=()
    NF_FLAGS=()
else
    CJK_FLAGS=(--proportional)
    NF_FLAGS=(--variable-width-glyphs)
fi

rm -rf "$WORK" "$OUT"
mkdir -p "$WORK"/{1-instance,2-cjk,3-nerd,logs}

# Background jobs: start with `run_job <log> <cmd...>`, then `wait_jobs`.
# Each job logs to its own file; a failure prints the log tail and fails the build.
JOB_PIDS=()
JOB_LOGS=()
run_job() {
    local log=$1
    shift
    "$@" > "$log" 2>&1 &
    JOB_PIDS+=($!)
    JOB_LOGS+=("$log")
}
wait_jobs() {
    local failed=0 i
    for i in "${!JOB_PIDS[@]}"; do
        if ! wait "${JOB_PIDS[$i]}"; then
            echo "  ✗ failed: ${JOB_LOGS[$i]}" >&2
            tail -20 "${JOB_LOGS[$i]}" | sed 's/^/    /' >&2
            failed=1
        fi
    done
    JOB_PIDS=()
    JOB_LOGS=()
    return "$failed"
}

echo "=== Building ${FAMILY} ($([ "$MONO" = 1 ] && echo mono || echo proportional), CJK scale ${CJK_SCALE}) ==="

echo "── 1/4 Instantiate styles from ${LATIN} ──"
python3 scripts/instantiate-fonts.py "$CONFIG" "${LATIN_SOURCES[@]}" "$WORK/1-instance"

echo "── 2/4 Merge Resource Han Rounded ${RESOURCE_HAN_ROUNDED_VERSION} ──"
for style in "${STYLES[@]}"; do
    case "$style" in
        Bold*) cjk="$CJK_DIR/ResourceHanRoundedCN-SemiBold.ttf" ;;
        *) cjk="$CJK_DIR/ResourceHanRoundedCN-Regular.ttf" ;;
    esac
    echo "${style} ← $(basename "$cjk")"
    run_job "$WORK/logs/cjk-${style}.log" \
        fontforge -script scripts/merge-cjk.py \
        "$WORK/1-instance/${COMPACT}-${style}.ttf" "$cjk" "$WORK/2-cjk/${COMPACT}-${style}.ttf" \
        --scale "$CJK_SCALE" ${CJK_FLAGS[@]+"${CJK_FLAGS[@]}"}
done
wait_jobs

echo "── 3/4 Patch Nerd Fonts ${NERD_FONTS_VERSION} ──"
for style in "${STYLES[@]}"; do
    run_job "$WORK/logs/nerd-${style}.log" \
        fontforge -script "$PATCHER" --complete --quiet ${NF_FLAGS[@]+"${NF_FLAGS[@]}"} \
        --outputdir "$WORK/3-nerd" "$WORK/2-cjk/${COMPACT}-${style}.ttf"
done
wait_jobs

echo "── 4/4 Finalize names and spacing flags ──"
python3 scripts/finalize-fonts.py "$CONFIG" "$WORK/3-nerd" "$OUT"

python3 scripts/verify-fonts.py "$CONFIG"
rm -rf "$WORK"
echo "=== Done: ${OUT}/ ==="
