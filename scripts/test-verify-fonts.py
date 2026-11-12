#!/usr/bin/env python3
"""Exercise the CJK checks in verify-fonts.py against altered copies of a built font.

Usage:
    python3 scripts/test-verify-fonts.py [font.ttf]

Uses fonts/RecSansMt.Baker/RecSansMt.Baker-Regular.ttf by default, so build first.
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).parent))
import fontconfig  # noqa: E402

spec = importlib.util.spec_from_file_location("verify_fonts", Path(__file__).parent / "verify-fonts.py")
verify_fonts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_fonts)

FONT = Path(sys.argv[1] if len(sys.argv) > 1 else "fonts/RecSansMt.Baker/RecSansMt.Baker-Regular.ttf")
CONFIG = fontconfig.load("configs/mt-baker.yaml")


def errors_after(change):
    font = TTFont(FONT)
    change(font)
    with tempfile.NamedTemporaryFile(suffix=".ttf") as tmp:
        font.save(tmp.name)
        return verify_fonts.check_font(tmp.name, CONFIG, "Regular")


def drop(cp):
    def change(font):
        for table in font["cmap"].tables:
            table.cmap.pop(cp, None)
    return change


def widen(cp, units):
    def change(font):
        name = font.getBestCmap()[cp]
        width, lsb = font["hmtx"][name]
        font["hmtx"][name] = (width + units, lsb)
    return change


def halfwidth_off_by(units):
    """Set ｱ to half the ideograph advance plus units, whatever the CJK scale."""
    def change(font):
        cmap = font.getBestCmap()
        half = font["hmtx"][cmap[0x4E00]][0] / 2
        _, lsb = font["hmtx"][cmap[0xFF71]]
        font["hmtx"][cmap[0xFF71]] = (int(half + units), lsb)
    return change


CASES = [
    ("unchanged font", lambda font: None, None),
    ("missing halfwidth ｱ", drop(0xFF71), "halfwidth"),
    ("halfwidth ｱ 1 unit over half", halfwidth_off_by(1), None),
    ("halfwidth ｱ 2 units over half", halfwidth_off_by(2), "halfwidth"),
    ("one ideograph 1 unit wide", widen(0x4E01, 1), "ideograph advances"),
    ("missing stem glyph 丨", drop(0x4E28), "stem glyphs"),
]

failed = False
for label, change, expected in CASES:
    errors = errors_after(change)
    ok = not errors if expected is None else any(expected in e for e in errors)
    failed |= not ok
    print(f"{'✓' if ok else '✗'} {label}: {errors or 'no errors'}")
if failed:
    sys.exit(1)
print("verify-fonts test: ok")
