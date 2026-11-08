# CLAUDE.md — Rec Mountain Fonts

Rec Mountain Fonts builds three font families with Resource Han Rounded CJK and Nerd
Fonts: **Rec Mono St.Helens** (Recursive, monospace, for code), **Rec Sans
Mt.Baker** (Recursive, proportional, for text), and **Rec Serif Mt.Adams**
(Anthropic Serif Text, proportional, for reading). St.Helens and Mt.Baker share
one design.

## Read first

- [`wiki/Configuration.md`](wiki/Configuration.md) — family configs, `Extends`, pinned upstream versions.
- [`wiki/Build-Pipeline.md`](wiki/Build-Pipeline.md) — the four build stages and the verifier.
- [`wiki/Release-Process.md`](wiki/Release-Process.md) — CI, tag-driven releases, version numbers.
- [`wiki/Wiki-Publication.md`](wiki/Wiki-Publication.md) — documentation rules.

**Canonical documentation rule:** `wiki/` is the only documentation surface.
Each topic has an English `wiki/<Page>.md` and a Chinese `wiki/<Page>-zh-CN.md`
with matching heading structure and equivalent facts; update both in the same
change. Load only the English files for routine context. Verify descriptions
against the current scripts and configs before writing them.

## Rules

- `configs/st-helens.yaml` is the shared design. Mt.Baker extends it and changes
  only its name, `Mono: false`, and `Exclude Features: [ss10]` (plain zero); keep
  it that way unless asked otherwise.
- `configs/mt-adams.yaml` uses `Base: anthropic-serif`; Bold and Bold Italic map
  to the Semibold weights to match the Recursive families' wght 600. Anthropic
  Serif has no release feed, so its files are pinned by SHA-256 in
  `scripts/fetch-sources.sh`; update those hashes with `ANTHROPIC_SERIF_VERSION`.
- All families share one CJK scale (`build-all.sh` default 1.15).
- Upstream versions live only in `versions.env`. Never vendor upstream fonts or
  the Nerd Fonts patcher into the repository; `sources/` is fetched and ignored.
- Python dependencies are pinned exactly in `requirements.txt`.
- Workflow actions are pinned to commit SHAs with a trailing `# vX.Y.Z` comment.
- The preview images in `README.md` and `wiki/Fonts*.md` come from
  `docs/previews/`. After any change to fonts, configs, or
  `scripts/render-previews.py`, rebuild, run `python3 scripts/render-previews.py`,
  look at every changed image, and commit them in the same change. Every
  preview must appear in `README.md`; the local gate checks this.

## Commands

```bash
./scripts/local-gate.sh            # fast checks: scripts, configs, wiki, release notes
./scripts/local-gate.sh --build    # plus a full build and font verification
./scripts/check-updates.sh         # compare versions.env with upstream releases
```

Run `./scripts/local-gate.sh --build` before pushing a change to font output.
