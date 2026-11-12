#!/usr/bin/env bash
# local-gate.sh — Run the CI checks locally before opening a pull request
#
# Usage:
#   ./scripts/local-gate.sh           # fast checks (seconds)
#   ./scripts/local-gate.sh --build   # also build and verify every family

set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi

step() { echo "── $*"; }

step "Shell syntax"
for f in scripts/*.sh; do bash -n "$f"; done

step "Python syntax"
python3 -m py_compile scripts/*.py

step "Configs"
for cfg in configs/*.yaml; do python3 scripts/fontconfig.py "$cfg" > /dev/null; done

step "Upstream versions in docs"
source versions.env
for pin in "Recursive-${RECURSIVE_VERSION}" "Anthropic_Serif-${ANTHROPIC_SERIF_VERSION}" "Resource_Han_Rounded-${RESOURCE_HAN_ROUNDED_VERSION}" "Nerd_Fonts-${NERD_FONTS_VERSION}"; do
    grep -q "badge/${pin}-" README.md || { echo "README.md badge does not match versions.env: ${pin}" >&2; exit 1; }
done
for page in wiki/Configuration.md wiki/Configuration-zh-CN.md; do
    for line in "RECURSIVE_VERSION=${RECURSIVE_VERSION}" "ANTHROPIC_SERIF_VERSION=${ANTHROPIC_SERIF_VERSION}" "RESOURCE_HAN_ROUNDED_VERSION=${RESOURCE_HAN_ROUNDED_VERSION}" "NERD_FONTS_VERSION=${NERD_FONTS_VERSION}"; do
        grep -qx "$line" "$page" || { echo "${page} does not match versions.env: ${line}" >&2; exit 1; }
    done
done

step "Preview images in README"
for img in docs/previews/*.png; do
    grep -q "$img" README.md || { echo "README.md does not show ${img}" >&2; exit 1; }
done
for img in $(grep -o 'docs/previews/[a-z-]*\.png' README.md | sort -u); do
    [ -f "$img" ] || { echo "README.md references missing ${img}" >&2; exit 1; }
done

step "Wiki"
python3 scripts/check-wiki.py

step "Wiki publisher"
bash scripts/test-wiki-publish.sh

step "Resource Han Rounded fetch"
bash scripts/test-fetch-cjk.sh

step "Release notes"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
echo "0000  example.ttf" > "$tmp/SHA256SUMS.txt"
notes=$(./scripts/release-notes.sh HEAD "$tmp")
grep -q '^## Checksums' <<< "$notes" || { echo "release notes are incomplete" >&2; exit 1; }

if [ "${1:-}" = "--build" ]; then
    step "Build and verify all families"
    ./scripts/build-all.sh
fi

echo "local gate: ok"
