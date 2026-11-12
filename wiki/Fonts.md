# Fonts

[简体中文](Fonts-zh-CN)

Rec Mountain Fonts ships three families. St.Helens (for code) and Mt.Baker (the same
letterforms with natural widths, for everyday text) share one Recursive design;
Mt.Adams is a serif for long-form reading, built from Anthropic Serif Text.

## Preview

### Styles

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/styles-dark.png">
  <img alt="Regular, Italic, Bold, and Bold Italic of all three families" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/styles-light.png" width="800">
</picture>

### Code

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/code-dark.png">
  <img alt="TypeScript in Rec Mono St.Helens with code ligatures and italic keywords" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/code-light.png" width="800">
</picture>

### Terminal

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/terminal-dark.png">
  <img alt="A shell prompt with Powerline segments, Nerd Font icons, and a CJK table aligned on the cell grid" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/terminal-light.png" width="800">
</picture>

### Ligatures

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/ligatures-dark.png">
  <img alt="Thirty code ligatures in Rec Mono St.Helens" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/ligatures-light.png" width="800">
</picture>

### Text

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/text-dark.png">
  <img alt="English, Chinese, and Japanese paragraphs in Rec Sans Mt.Baker" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/text-light.png" width="800">
</picture>

### Serif

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/serif-dark.png">
  <img alt="English, Chinese, and Japanese paragraphs in Rec Serif Mt.Adams" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/serif-light.png" width="800">
</picture>

### Glyph coverage

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/glyphs-dark.png">
  <img alt="Glyph coverage: Latin, Vietnamese, mathematical Greek, CJK, kana, box drawing, Powerline, and Nerd Font icons" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/glyphs-light.png" width="800">
</picture>

## Families

| Family | Use | Spacing | Code ligatures |
|---|---|---|---|
| **Rec Mono St.Helens** | Editors and terminals | Monospace, 600-unit cell | Yes |
| **Rec Sans Mt.Baker** | Documents and UI | Proportional | No |
| **Rec Serif Mt.Adams** | Articles, notes, and e-books | Proportional | No |

Each family has four styles: Regular, Italic, Bold, and Bold Italic.

## St.Helens and Mt.Baker design

Both families come from one config (`configs/st-helens.yaml`); Mt.Baker changes
its name and spacing and drops the dotted zero. See [Configuration](Configuration).

| Setting | Value |
|---|---|
| Casual (`CASL`) | 1 — the casual, brush-like Recursive design |
| Cursive (`CRSV`) | 1 — cursive letterforms |
| Slant (`slnt`) | -3° for Regular and Bold, -10° for Italic and Bold Italic |
| Weight (`wght`) | 400 for Regular and Italic, 600 for Bold and Bold Italic |
| Stylistic sets | ss01–ss12; Mt.Baker leaves out ss10, so St.Helens has a dotted zero and Mt.Baker a plain one |

Recursive's ss01–ss06 alternates apply only to Roman (`CRSV 0`) glyphs, so they
have no visible effect with `CRSV 1`. They stay in the config so a Roman family
can reuse it.

## Mt.Adams design

Mt.Adams (`configs/mt-adams.yaml`) takes each style from a static Anthropic
Serif Text weight:

| Style | Anthropic Serif Text weight |
|---|---|
| Regular | Regular |
| Italic | Italic (-10°) |
| Bold | Semibold, to match the other families' wght 600 |
| Bold Italic | Semibold Italic |

The build converts its CFF outlines to TrueType at 1000 units per em, so the
CJK merge and the icons line up as they do in the Recursive families.

## Glyph coverage

| Source | Coverage |
|---|---|
| Recursive | Latin (including Vietnamese), 20 mathematical Greek letters, box drawing, blocks, punctuation, and symbols. No Cyrillic. |
| Anthropic Serif Text (Mt.Adams) | Latin-1 and all of Latin Extended-A (Western and Central European), punctuation, and symbols. No Vietnamese, Greek, Cyrillic, or box drawing. |
| Resource Han Rounded CN | CJK ideographs (20,976 in U+4E00–9FFF), kana, CJK punctuation, full-width and halfwidth forms |
| Nerd Fonts | Every icon set the patcher's `--complete` option adds, including Powerline |

CJK glyphs come from Resource Han Rounded at the same weight as the Latin
glyphs: wght 400 for Regular and Italic, and wght 600 for Bold and Bold Italic. In every family they are
scaled to the Latin font's em, shrunk only if they would be taller than its
ascender–descender body, then enlarged 1.15× and centred on that body. Hangul
syllables are not included.

## Spacing differences

| Glyph group | St.Helens | Mt.Baker | Mt.Adams |
|---|---|---|---|
| ASCII | Always 600 | Natural width (for example `i` 350, `m` 850) | Natural width (for example `i` 300, `m` 944) |
| CJK and full-width forms | 1200 (two cells) | Scaled source width (1150) | Scaled source width (1150) |
| Halfwidth forms | 600 (one cell) | Scaled source width (575) | Scaled source width (575) |
| Nerd Font icons | Two cells, centred | Natural width | Natural width |
| Code ligatures (`=>`, `!=`) | On by default | Off | None |

St.Helens also sets the flags Windows Terminal and DirectWrite need to keep
ASCII text on the cell grid; see [Build Pipeline](Build-Pipeline).
