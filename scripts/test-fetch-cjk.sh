#!/usr/bin/env bash
# test-fetch-cjk.sh — Exercise the Resource Han Rounded part of fetch-sources.sh
# in a throwaway copy of the repository, with curl, 7z, and Python stubbed out
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail() {
  printf 'fetch-cjk test: %s\n' "$1" >&2
  exit 1
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
repo="$tmp/repo"
bin="$tmp/bin"
log="$tmp/calls.log"
mkdir -p "$repo/scripts" "$repo/venv/bin" "$bin"
cp "$root/versions.env" "$repo/"
cp "$root/scripts/fetch-sources.sh" "$repo/scripts/"
source "$root/versions.env"

# The other sources are already current, so only Resource Han Rounded is fetched
for pair in "recursive $RECURSIVE_VERSION" "anthropic-serif $ANTHROPIC_SERIF_VERSION" \
  "nerd-fonts-patcher $NERD_FONTS_VERSION"; do
  mkdir -p "$repo/sources/${pair% *}"
  echo "${pair#* }" > "$repo/sources/${pair% *}/.version"
done

# Stub instancer at the real path; the stub Python runs it and passes the fontTools check
printf '# stub instancer\n' > "$repo/scripts/instance-cjk.py"
cat > "$repo/venv/bin/python3" <<EOF
#!/usr/bin/env bash
[ "\$1" = -c ] && exit 0
echo "instance \$3" >> "$log"
touch "\$4"
EOF
cat > "$bin/curl" <<EOF
#!/usr/bin/env bash
while [ \$# -gt 1 ]; do [ "\$1" = -o ] && out=\$2; shift; done
echo "curl" >> "$log"
cp "$tmp/archive" "\$out"
EOF
for name in 7z 7zz; do
  cat > "$bin/$name" <<EOF
#!/usr/bin/env bash
echo "7z" >> "$log"
dest=\${2#-o}
mkdir -p "\$dest" && touch "\$dest/ResourceHanRoundedCN-VF.otf"
EOF
done
chmod +x "$repo/venv/bin/python3" "$bin"/*

# Pin the fixture archive's hash in place of the real one
printf 'fixture archive\n' > "$tmp/archive"
fixture_hash=$( (sha256sum "$tmp/archive" 2>/dev/null || shasum -a 256 "$tmp/archive") | cut -d' ' -f1)
sed -i.bak "s/^RHR_SHA256=.*/RHR_SHA256=${fixture_hash}/" "$repo/scripts/fetch-sources.sh"

fetch() { : > "$log"; PATH="$bin:$PATH" "$repo/scripts/fetch-sources.sh" > "$tmp/out" 2>&1; }
rhr="$repo/sources/resource-han-rounded"

# 1. A corrupt archive fails on its checksum before extraction or instancing
mv "$tmp/archive" "$tmp/archive.real"
printf 'tampered\n' > "$tmp/archive"
fetch && fail "corrupt archive did not fail"
grep -q "does not match its pinned SHA-256" "$tmp/out" || fail "corrupt archive did not report a checksum mismatch"
[ "$(cat "$log")" = curl ] || fail "corrupt archive ran: $(tr '\n' ' ' < "$log")"
[ -e "$rhr" ] && fail "corrupt archive left $rhr behind"
mv "$tmp/archive.real" "$tmp/archive"

# 2. A good archive makes both weights and stamps the recipe
fetch || fail "fetch failed: $(cat "$tmp/out")"
[ -f "$rhr/ResourceHanRoundedCN-Medium.ttf" ] && [ -f "$rhr/ResourceHanRoundedCN-SemiBold.ttf" ] \
  || fail "weights were not made"
grep -q "instance 500" "$log" && grep -q "instance 600" "$log" || fail "did not instance 500 and 600"
grep -q "^${RESOURCE_HAN_ROUNDED_VERSION}+" "$rhr/.version" || fail "stamp is $(cat "$rhr/.version")"

# 3. A complete, current cache does nothing
fetch || fail "cached fetch failed"
[ -s "$log" ] && fail "cached fetch ran: $(tr '\n' ' ' < "$log")"

# 4. A missing weight file makes both again
rm "$rhr/ResourceHanRoundedCN-SemiBold.ttf"
fetch || fail "refetch failed"
grep -c "^instance" "$log" | grep -qx 2 || fail "missing weight did not re-instance both"

# 5. A changed instancing recipe makes both again
printf '# changed recipe\n' >> "$repo/scripts/instance-cjk.py"
fetch || fail "recipe refetch failed"
grep -c "^instance" "$log" | grep -qx 2 || fail "recipe change did not re-instance"

echo "fetch-cjk test: ok"
