#!/usr/bin/env bash
# fetch-sources.sh — Download the pinned upstream sources into sources/
#
# Usage:
#   ./scripts/fetch-sources.sh
#
# Versions come from versions.env. A source is downloaded again only when its
# pinned version changes, or, for Resource Han Rounded, when a weight file is
# missing.

set -euo pipefail
cd "$(dirname "$0")/.."
source versions.env

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# current <dir> <version> — succeeds if <dir> already holds <version>
current() { [ "$(cat "$1/.version" 2>/dev/null)" = "$2" ]; }

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

# ── Resource Han Rounded CN (Medium + Bold) ──
# Downloaded again when the version changes or either weight file is missing.
dir="sources/resource-han-rounded"
RHR_WEIGHTS=(Medium Bold)
rhr_complete() {
    current "$dir" "$RESOURCE_HAN_ROUNDED_VERSION" || return 1
    for weight in "${RHR_WEIGHTS[@]}"; do
        [ -f "$dir/ResourceHanRoundedCN-${weight}.ttf" ] || return 1
    done
}
if ! rhr_complete; then
    echo "Fetching Resource Han Rounded v${RESOURCE_HAN_ROUNDED_VERSION}..."
    SEVENZIP=$(command -v 7z || command -v 7zz || true)
    if [ -z "$SEVENZIP" ]; then
        echo "ERROR: 7z not found (brew install sevenzip / apt-get install p7zip-full)" >&2
        exit 1
    fi
    rm -rf "$dir" && mkdir -p "$dir"
    curl -fsSL -o "$TMP/rhr.7z" \
        "https://github.com/CyanoHao/Resource-Han-Rounded/releases/download/v${RESOURCE_HAN_ROUNDED_VERSION}/RHR-CN-${RESOURCE_HAN_ROUNDED_VERSION}.7z"
    "$SEVENZIP" x -o"$TMP/rhr" "$TMP/rhr.7z" > /dev/null
    for weight in "${RHR_WEIGHTS[@]}"; do
        src=$(find "$TMP/rhr" -name "ResourceHanRoundedCN-${weight}.ttf" | head -1)
        if [ -z "$src" ]; then
            echo "ERROR: ResourceHanRoundedCN-${weight}.ttf not found in archive" >&2
            exit 1
        fi
        cp "$src" "$dir/"
    done
    echo "$RESOURCE_HAN_ROUNDED_VERSION" > "$dir/.version"
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
    sha256() { if command -v sha256sum > /dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }
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
