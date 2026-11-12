#!/usr/bin/env python3
"""Check the built fonts in fonts/ against their configs.

Usage:
    python3 scripts/verify-fonts.py configs/*.yaml

Exits 1 if any check fails.
"""

import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

import fontconfig
from fontnames import STYLES, style_file_name

REQUIRED_CODEPOINTS = {
    0x4E2D: "CJK ideograph 中",
    0x3042: "Hiragana あ",
    0xF015: "Nerd Font icon nf-fa-home",
    0xE0B0: "Powerline arrow",
}

# CJK stroke weight as stem thickness / stroke length of 丨 and 一, which does
# not change with the CJK scale. Resource Han Rounded measures about 0.089 at
# wght 400, 0.111 at 500, 0.126 at 600, and 0.139 at 700.
CJK_STEM_RATIO = {"Regular": 0.111, "Bold": 0.126}
CJK_STEM_TOLERANCE = 0.006
CJK_STEM_GLYPHS = (0x4E28, 0x4E00)


def cjk_stem_ratio(font, cmap):
    glyphs = font.getGlyphSet()
    ratios = []
    for cp in CJK_STEM_GLYPHS:
        pen = BoundsPen(glyphs)
        glyphs[cmap[cp]].draw(pen)
        x_min, y_min, x_max, y_max = pen.bounds
        width, height = x_max - x_min, y_max - y_min
        ratios.append(min(width, height) / max(width, height))
    return sum(ratios) / len(ratios)


def check_font(path, cfg, style):
    errors = []
    font = TTFont(path)
    names = font["name"]
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]

    if names.getDebugName(1) != cfg["family"]:
        errors.append(f"family name is {names.getDebugName(1)!r}")
    if names.getDebugName(2) != style:
        errors.append(f"style name is {names.getDebugName(2)!r}")
    for record in names.names:
        if record.nameID in (1, 2, 3, 4, 6, 16, 17) and "Nerd" in record.toUnicode():
            errors.append(f"name {record.nameID} still says {record.toUnicode()!r}")

    for cp, label in REQUIRED_CODEPOINTS.items():
        if cp not in cmap:
            errors.append(f"missing {label} (U+{cp:04X})")

    if all(cp in cmap for cp in CJK_STEM_GLYPHS):
        expected = CJK_STEM_RATIO["Bold" if style.startswith("Bold") else "Regular"]
        ratio = cjk_stem_ratio(font, cmap)
        if abs(ratio - expected) > CJK_STEM_TOLERANCE:
            errors.append(f"CJK stem ratio is {ratio:.3f}, expected {expected:.3f} ± {CJK_STEM_TOLERANCE}")
    else:
        errors.append("missing CJK stem glyphs 丨 (U+4E28) or 一 (U+4E00)")

    cell = hmtx["space"][0]
    ascii_widths = {hmtx[cmap[cp]][0] for cp in range(0x20, 0x7F) if cp in cmap}
    if cfg["mono"]:
        if font["post"].isFixedPitch != 1:
            errors.append("post.isFixedPitch is not 1")
        if font["head"].flags & (1 << 4):
            errors.append("head.flags bit 4 is set")
        if ascii_widths != {cell}:
            errors.append(f"ASCII advances are {sorted(ascii_widths)}, expected {cell}")
        if 0x4E2D in cmap and hmtx[cmap[0x4E2D]][0] != 2 * cell:
            errors.append(f"CJK advance is {hmtx[cmap[0x4E2D]][0]}, expected {2 * cell}")
    else:
        if font["post"].isFixedPitch != 0:
            errors.append("post.isFixedPitch is not 0")
        if len(ascii_widths) < 2:
            errors.append("ASCII advances are all equal; expected a proportional font")
        # Every ideograph keeps the same scaled advance, and a halfwidth form takes half
        ideograph_widths = {hmtx[cmap[cp]][0] for cp in range(0x4E00, 0xA000) if cp in cmap}
        if len(ideograph_widths) != 1:
            errors.append(f"CJK ideograph advances are {sorted(ideograph_widths)}, expected one width")
        elif 0xFF71 not in cmap:
            errors.append("missing halfwidth ｱ (U+FF71)")
        elif abs(hmtx[cmap[0xFF71]][0] - min(ideograph_widths) / 2) > 1:
            errors.append(f"halfwidth ｱ advance is {hmtx[cmap[0xFF71]][0]}, expected half of {min(ideograph_widths)}")

    return errors


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    failed = False
    for config_path in sys.argv[1:]:
        cfg = fontconfig.load(config_path)
        out_dir = Path("fonts") / cfg["compact"]
        family_ok = True
        for style in STYLES:
            path = out_dir / style_file_name(cfg["compact"], style)
            errors = [f"{path} not found"] if not path.is_file() else check_font(path, cfg, style)
            for error in errors:
                print(f"✗ {path.name}: {error}")
            family_ok &= not errors
        failed |= not family_ok
        if family_ok:
            print(f"✓ {cfg['family']}: 4 styles verified ({'mono' if cfg['mono'] else 'proportional'})")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
