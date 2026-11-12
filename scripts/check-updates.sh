#!/usr/bin/env bash
# check-updates.sh — Compare the pinned upstream versions with the latest releases
#
# Usage:
#   ./scripts/check-updates.sh
#
# Exits 1 if any pinned version is behind. Pre-releases are ignored, except for
# Resource Han Rounded, whose pinned variable font is itself a pre-release.

set -euo pipefail
cd "$(dirname "$0")/.."
source versions.env

outdated=0

# check <name> <owner/repo> <pinned> [--pre-release]
check() {
    local name=$1 repo=$2 pinned=$3 latest
    if [ "${4:-}" = --pre-release ]; then
        latest=$(curl -fsSL "https://api.github.com/repos/${repo}/releases?per_page=1" |
            python3 -c 'import json, sys; print(json.load(sys.stdin)[0]["tag_name"].lstrip("v"))')
    else
        latest=$(curl -fsSL "https://api.github.com/repos/${repo}/releases/latest" |
            python3 -c 'import json, sys; print(json.load(sys.stdin)["tag_name"].lstrip("v"))')
    fi
    if [ "$latest" = "$pinned" ]; then
        echo "✓ ${name} ${pinned} is the latest release"
    else
        echo "↑ ${name} ${pinned} → ${latest} available (update versions.env)"
        outdated=1
    fi
}

check "Recursive" arrowtype/recursive "$RECURSIVE_VERSION"
check "Resource Han Rounded" CyanoHao/Resource-Han-Rounded "$RESOURCE_HAN_ROUNDED_VERSION" --pre-release
check "Nerd Fonts" ryanoasis/nerd-fonts "$NERD_FONTS_VERSION"
echo "· Anthropic Serif ${ANTHROPIC_SERIF_VERSION} is pinned by SHA-256 (no release feed to check)"

exit "$outdated"
