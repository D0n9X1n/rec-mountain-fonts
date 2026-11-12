#!/usr/bin/env python3
"""Make a static CJK source weight from the Resource Han Rounded variable font.

Usage:
    python3 scripts/instance-cjk.py <ResourceHanRoundedCN-VF.otf> <wght> <output.ttf>

The variable font is CFF2, which FontForge cannot open, so the instance is
saved with quadratic TrueType outlines. Only the outlines, advances and cmap are
used by merge-cjk.py; layout and vertical tables are dropped because the
instancer cannot merge this font's GPOS.
"""

import sys

from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable
from fontTools.varLib.instancer import instantiateVariableFont

DROP_TABLES = ("GPOS", "GDEF", "BASE", "VVAR", "vhea", "vmtx", "VORG")
ROUNDNESS = 100  # ROND default: fully rounded, as in the static releases
CU2QU_MAX_ERR = 1.0  # font units


def to_truetype(font):
    order = font.getGlyphOrder()
    glyph_set = font.getGlyphSet()
    glyphs = {}
    for name in order:
        pen = TTGlyphPen(None)
        glyph_set[name].draw(Cu2QuPen(pen, CU2QU_MAX_ERR, reverse_direction=True))
        glyphs[name] = pen.glyph()

    glyf = font["glyf"] = newTable("glyf")
    glyf.glyphOrder = order
    glyf.glyphs = glyphs
    font["loca"] = newTable("loca")
    del font["CFF2"]

    maxp = font["maxp"] = newTable("maxp")
    maxp.tableVersion = 0x00010000
    for attr in ("maxTwilightPoints", "maxStorage", "maxFunctionDefs", "maxInstructionDefs",
                 "maxStackElements", "maxSizeOfInstructions", "maxComponentElements"):
        setattr(maxp, attr, 0)
    maxp.maxZones = 1
    font["post"].formatType = 3.0
    font.sfntVersion = "\x00\x01\x00\x00"


def main():
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    source, weight, output = sys.argv[1], float(sys.argv[2]), sys.argv[3]

    font = TTFont(source)
    for tag in DROP_TABLES:
        if tag in font:
            del font[tag]
    font = instantiateVariableFont(font, {"wght": weight, "ROND": ROUNDNESS})
    to_truetype(font)
    font.save(output)  # recalculates maxp point/contour counts and bounding boxes
    print(f"Resource Han Rounded wght {weight:g} → {output}")


if __name__ == "__main__":
    main()
