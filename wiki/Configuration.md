# Configuration

[简体中文](Configuration-zh-CN)

Each family is one YAML file in `configs/`. Upstream versions live in
`versions.env`.

## Family configs

`configs/st-helens.yaml` holds the shared Recursive design:

| Key | Meaning |
|---|---|
| `Family Name` | Full family name, for example `Rec Mono St.Helens`. File and PostScript names drop the spaces. |
| `Base` | Latin source: `recursive` (default) or `anthropic-serif` |
| `Mono` | `true` builds a monospace family (`MONO 1`); `false` builds a proportional one (`MONO 0`). Must be `false` for `anthropic-serif`. |
| `Styles` | For `recursive`: `CASL`, `wght`, `slnt`, and `CRSV` for each of Regular, Italic, Bold, and Bold Italic. For `anthropic-serif`: the source weight for each style. |
| `Code Ligatures` | Turn Recursive's code ligatures on by default. Applied to mono families only. |
| `Features` | Stylistic sets frozen into the fonts |
| `Exclude Features` | Stylistic sets to remove from the inherited `Features` |

`configs/mt-baker.yaml` starts from St.Helens:

```yaml
Extends: st-helens.yaml

Family Name: Rec Sans Mt.Baker
Mono: false

Exclude Features:
  - ss10  # Dotted 0
```

`Extends` loads the named file first; keys in the extending file replace the
parent's. `Exclude Features` then removes sets from the inherited `Features`;
naming a set that is not enabled is an error. Any other change to St.Helens's
styles or features therefore applies to Mt.Baker too.

`configs/mt-adams.yaml` stands alone:

```yaml
Family Name: Rec Serif Mt.Adams

Base: anthropic-serif
Mono: false

Styles:
  Regular:     Regular
  Italic:      RegularItalic
  Bold:        Semibold
  Bold Italic: SemiboldItalic
```

Each `Styles` value names an Anthropic Serif Text file that
`scripts/fetch-sources.sh` downloads: `Regular`, `RegularItalic`, `Semibold`, or
`SemiboldItalic`. Bold uses Semibold to match the Recursive families' wght 600.

## Code ligatures

Recursive draws code ligatures as glyphs wider than one cell. For a mono family
the build gives each one a single-cell advance and shifts its outline left so it
overhangs the cells before it. In a proportional family that would squash every
glyph wider than a space, so the build skips ligatures when `Mono` is `false`,
even if `Code Ligatures` is `true`.

## Stylistic sets

| Feature | Change | Applies to |
|---|---|---|
| ss01 | Single-story a | Roman only |
| ss02 | Single-story g | Roman only |
| ss03 | Simplified f | Roman only |
| ss04 | Simplified i | Roman only |
| ss05 | Simplified l | Roman only |
| ss06 | Simplified r | Roman only |
| ss07 | Simplified italic diagonals (kwxyz) | Roman and cursive |
| ss08 | Serifless L and Z | Roman and cursive |
| ss09 | Simplified 6 and 9 | Roman and cursive |
| ss10 | Dotted 0 | Roman and cursive |
| ss11 | Simplified 1 | Roman and cursive |
| ss12 | Simplified @ | Roman and cursive |

## Upstream versions

`versions.env` pins each upstream release:

```bash
RECURSIVE_VERSION=1.085
ANTHROPIC_SERIF_VERSION=25.324
RESOURCE_HAN_ROUNDED_VERSION=1.910
NERD_FONTS_VERSION=3.5.1
```

`./scripts/check-updates.sh` compares these with the latest GitHub releases,
ignoring pre-releases, and exits 1 if any is behind. Resource Han Rounded is
pinned to a pre-release, the only one with a variable font, so it is compared
with the newest release of any kind, and `scripts/fetch-sources.sh` pins its
archive by SHA-256. Anthropic Serif has no
release feed: `ANTHROPIC_SERIF_VERSION` is its name-table version, and
`scripts/fetch-sources.sh` pins each of its files by SHA-256, so change the
hashes there together with the version. To update one, change the
version, also update the version badges in `README.md` and the block above in
both Configuration pages (the local gate fails until they match), run
`./scripts/local-gate.sh --build`, and check the result in an editor before
merging.

## Adding a family

1. Add `configs/<name>.yaml`, usually with `Extends: st-helens.yaml` for a
   Recursive family or `Base: anthropic-serif` for a serif one.
2. Run `./scripts/build.sh configs/<name>.yaml`.

`build-all.sh`, the verifier, CI, and release packaging pick up every file in
`configs/` automatically.
