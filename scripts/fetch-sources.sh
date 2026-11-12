#!/usr/bin/env bash
# fetch-sources.sh — Download the pinned upstream sources into sources/
#
# Usage:
#   ./scripts/fetch-sources.sh
#
# Versions come from versions.env. A source is downloaded again only when its
# pinned version changes, or, for Resource Han Rounded, when a weight file or
# its instancing recipe changes.

set -euo pipefail
cd "$(dirname "$0")/.."
source versions.env

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# current <dir> <version> — succeeds if <dir> already holds <version>
current() { [ "$(cat "$1/.version" 2>/dev/null)" = "$2" ]; }
sha256() { if command -v sha256sum > /dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }
# wait_all — wait for every background job; fail if any failed
wait_all() {
    local pid failed=0
    for pid in $(jobs -p); do wait "$pid" || failed=1; done
    return "$failed"
}

# ── Recursive variable font + code ligature feature file ──
dir="sources/recursive"
if ! current "$dir" "$RECURSIVE_VERSION"; then
    echo "Fetching Recursive v${RECURSIVE_VERSION}..."
    rm -rf "$dir" && mkdir -p "$dir"
    curl -fsSL -o "$TMP/recursive.zip" \
        "https://github.com/arrowtype/recursive/releases/download/v${RECURSIVE_VERSION}/ArrowType-Recursive-${RECURSIVE_VERSION}.zip"
    unzip -q -j "$TMP/recursive.zip" "*/Recursive_Desktop/Recursive_VF_${RECURSIVE_VERSION}.ttf" -d "$dir"
    curl -fsSL -o "$dir/calt-generated--code_fonts_only.fea" \
        "https://raw.githubusercontent.com/arrowtype/recursive/v${RECURSIVE_VERSION}/src/features/features/calt-generated--code_fonts_only.fea"
    echo "$RECURSIVE_VERSION" > "$dir/.version"
fi

# ── Resource Han Rounded CN (wght 500 + 600) ──
# The CN variable font is a pre-release with no stable feed, so the archive is
# pinned by SHA-256; update it with RESOURCE_HAN_ROUNDED_VERSION. The static
# Medium (500) and SemiBold (600) sources are made from it by instance-cjk.py.
# They are made again when the version or instance-cjk.py changes, or when
# either file is missing.
dir="sources/resource-han-rounded"
RHR_SHA256=4ad7b141535a1f11831287b0a6f71ddcec8daa92dc1d82c59892068f8ae5df09
RHR_WEIGHTS=("Medium 500" "SemiBold 600")
rhr_stamp="${RESOURCE_HAN_ROUNDED_VERSION}+$(sha256 scripts/instance-cjk.py | cut -c1-12)"
rhr_complete() {
    current "$dir" "$rhr_stamp" || return 1
    for entry in "${RHR_WEIGHTS[@]}"; do
        [ -f "$dir/ResourceHanRoundedCN-${entry% *}.ttf" ] || return 1
    done
}
if ! rhr_complete; then
    echo "Fetching Resource Han Rounded v${RESOURCE_HAN_ROUNDED_VERSION}..."
    SEVENZIP=$(command -v 7z || command -v 7zz || true)
    if [ -z "$SEVENZIP" ]; then
        echo "ERROR: 7z not found (brew install sevenzip / apt-get install p7zip-full)" >&2
        exit 1
    fi
    PYTHON=$([ -x venv/bin/python3 ] && echo venv/bin/python3 || echo python3)
    if ! "$PYTHON" -c "import fontTools" 2> /dev/null; then
        echo "ERROR: ${PYTHON} cannot import fontTools (pip install -r requirements.txt)" >&2
        exit 1
    fi
    curl -fsSL -o "$TMP/rhr.7z" \
        "https://github.com/CyanoHao/Resource-Han-Rounded/releases/download/v${RESOURCE_HAN_ROUNDED_VERSION}/RHR-CFF2-CN-${RESOURCE_HAN_ROUNDED_VERSION}.7z"
    if [ "$(sha256 "$TMP/rhr.7z")" != "$RHR_SHA256" ]; then
        echo "ERROR: RHR-CFF2-CN-${RESOURCE_HAN_ROUNDED_VERSION}.7z does not match its pinned SHA-256" >&2
        exit 1
    fi
    "$SEVENZIP" x -o"$TMP/rhr" "$TMP/rhr.7z" > /dev/null
    vf=$(find "$TMP/rhr" -name "ResourceHanRoundedCN-VF.otf" | head -1)
    if [ -z "$vf" ]; then
        echo "ERROR: ResourceHanRoundedCN-VF.otf not found in archive" >&2
        exit 1
    fi
    rm -rf "$dir" && mkdir -p "$dir"
    for entry in "${RHR_WEIGHTS[@]}"; do
        "$PYTHON" scripts/instance-cjk.py "$vf" "${entry#* }" "$dir/ResourceHanRoundedCN-${entry% *}.ttf" &
    done
    wait_all
    echo "$rhr_stamp" > "$dir/.version"
fi

# ── Nerd Fonts patcher ──
dir="sources/nerd-fonts-patcher"
if ! current "$dir" "$NERD_FONTS_VERSION"; then
    echo "Fetching Nerd Fonts patcher v${NERD_FONTS_VERSION}..."
    rm -rf "$dir" && mkdir -p "$dir"
    curl -fsSL -o "$TMP/patcher.zip" \
        "https://github.com/ryanoasis/nerd-fonts/releases/download/v${NERD_FONTS_VERSION}/FontPatcher.zip"
    unzip -q "$TMP/patcher.zip" -d "$dir"
    echo "$NERD_FONTS_VERSION" > "$dir/.version"
fi

# ── Anthropic Serif Text (Regular, Semibold, and their italics) ──
# There is no versioned release feed, so each file is pinned by SHA-256.
# Update these hashes together with ANTHROPIC_SERIF_VERSION.
dir="sources/anthropic-serif"
if ! current "$dir" "$ANTHROPIC_SERIF_VERSION"; then
    echo "Fetching Anthropic Serif ${ANTHROPIC_SERIF_VERSION}..."
    rm -rf "$dir" && mkdir -p "$dir"
    while read -r weight hash; do
        file="AnthropicSerif-Text-${weight}-Static.otf"
        curl -fsSL -o "$TMP/$file" "https://fontiko.com/system/uploads/font-files/445/${file}"
        if [ "$(sha256 "$TMP/$file")" != "$hash" ]; then
            echo "ERROR: ${file} does not match its pinned SHA-256" >&2
            exit 1
        fi
        cp "$TMP/$file" "$dir/"
    done <<'EOF'
Regular 255ca18a938adc37aa8fb47e9fbfb82562820ee1237a7b6c5bdf2fe6a54b729e
RegularItalic 37ff475d587c0adc5875b1426c2a2afc20ece664516c227bc48a4f62689579e1
Semibold 2b5d01e6281cf6186b27c7857ac0392aed36a991d05aba1a26dd95a77182beb1
SemiboldItalic 5261d2490937f6c3419b2c7b6e87959ff11db8aeae61aa317cc76b99036f9ff2
EOF
    echo "$ANTHROPIC_SERIF_VERSION" > "$dir/.version"
fi

echo "Sources: Recursive ${RECURSIVE_VERSION}, Anthropic Serif ${ANTHROPIC_SERIF_VERSION}, Resource Han Rounded ${RESOURCE_HAN_ROUNDED_VERSION}, Nerd Fonts ${NERD_FONTS_VERSION}"
