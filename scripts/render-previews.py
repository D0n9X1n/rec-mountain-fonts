#!/usr/bin/env python3
"""Render the preview images in docs/previews/ from the built fonts.

Usage:
    python3 scripts/render-previews.py [fonts_dir]

fonts_dir defaults to fonts/ (the output of build-all.sh). Every preview is
written twice, <name>-dark.png and <name>-light.png, in the Apollo dark and
light palettes. Text is shaped with HarfBuzz (Pillow's raqm layout), so code
ligatures, CJK, and Nerd Font icons render as they do in apps.
"""

import functools
import re
import sys
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont, features

import fontconfig
from fontnames import STYLES, style_file_name

SCALE = 2  # render at 2x; the README shows images at half size
WIDTH = 800
PAD = 32
OUT_DIR = Path("docs/previews")

# Apollo palettes (https://github.com/D0n9X1n/apollo-theme, palette/*.json)
THEMES = {
    "dark": {
        "canvas": "#141617", "surface": "#1d2021", "selection": "#3c3836",
        "fg": "#cfbc97", "bright": "#fbf1c7", "muted": "#928374", "faint": "#665c54",
        "accent": "#fabd2f", "red": "#fb4934", "green": "#b8bb26",
        "blue": "#83a598", "magenta": "#d3869b", "cyan": "#8ec07c",
    },
    "light": {
        "canvas": "#f9f5d7", "surface": "#f2e5bc", "selection": "#ebdbb2",
        "fg": "#3c3836", "bright": "#282828", "muted": "#665c54", "faint": "#a89984",
        "accent": "#8a5200", "red": "#9d0006", "green": "#6b6700",
        "blue": "#076678", "magenta": "#8f3f71", "cyan": "#356b4d",
    },
}

ICONS = {
    "folder": "", "branch": "", "check": "", "house": "",
    "apple": "", "linux": "", "windows": "", "github": "",
    "python": "", "rust": "", "docker": "", "vim": "",
    "typescript": "\U000f06e6", "markdown": "", "terminal": "",
    "gear": "", "file": "", "lock": "", "heart": "",
    "star": "", "clock": "", "code": "",
    "pl_right": "", "pl_round_left": "", "pl_round_right": "",
}

LIGATURES = [
    "=>", "->", "<-", "<->", "==>", "<==", "==", "===", "!=", "!==",
    ">=", "<=", "|>", "<|", "::", "&&", "||", "??", "?.", "++",
    "//", "/*", "*/", "<!--", "-->", "=~", "!~", ">>=", "<<=", "|=|",
]


class Families:
    """Font files for the mono, sans, and serif families, read from configs/."""

    KEYS = ("mono", "sans", "serif")

    def __init__(self, fonts_dir):
        self.entries = {}
        for config_path in sorted(Path("configs").glob("*.yaml")):
            cfg = fontconfig.load(config_path)
            files = {s: fonts_dir / cfg["compact"] / style_file_name(cfg["compact"], s) for s in STYLES}
            missing = [str(p) for p in files.values() if not p.is_file()]
            if missing:
                sys.exit(f"ERROR: missing {', '.join(missing)} — run ./scripts/build-all.sh first")
            key = "serif" if cfg["base"] == "anthropic-serif" else "mono" if cfg["mono"] else "sans"
            self.entries[key] = (cfg["family"], files)
        if set(self.entries) != set(self.KEYS):
            sys.exit("ERROR: previews need one mono, one sans, and one serif family in configs/")

        for key in self.KEYS:
            cmap = TTFont(self.entries[key][1]["Regular"]).getBestCmap()
            absent = [name for name, ch in ICONS.items() if ord(ch) not in cmap]
            if absent:
                sys.exit(f"ERROR: icons missing from {self.entries[key][0]}: {', '.join(absent)}")

    def name(self, key):
        return self.entries[key][0]

    def font(self, key, style, size):
        return load_font(str(self.entries[key][1][style]), size)


@functools.lru_cache(maxsize=None)
def load_font(path, size):
    return ImageFont.truetype(path, round(size * SCALE), layout_engine=ImageFont.Layout.RAQM)


def px(value):
    return round(value * SCALE)


class Card:
    """A rounded card in one theme. Coordinates are in 1x points."""

    def __init__(self, theme, max_height=2000):
        self.t = THEMES[theme]
        self.image = Image.new("RGB", (px(WIDTH), px(max_height)), self.t["canvas"])
        self.draw = ImageDraw.Draw(self.image)

    def text(self, x, baseline, s, font, fill, features=None):
        """Draw s with its baseline at y; return the advance in points."""
        self.draw.text((px(x), px(baseline)), s, font=font, fill=self.t.get(fill, fill),
                       anchor="ls", features=features)
        return font.getlength(s, features=features) / SCALE

    def width(self, s, font, features=None):
        return font.getlength(s, features=features) / SCALE

    def rect(self, x0, y0, x1, y1, fill, radius=0):
        self.draw.rounded_rectangle((px(x0), px(y0), px(x1), px(y1)), radius=px(radius),
                                    fill=self.t.get(fill, fill))

    def window_chrome(self, title, mono_font):
        """Editor/terminal title bar; returns the y where content starts."""
        self.rect(0, 0, WIDTH, 40, "surface")
        for i, color in enumerate(("red", "accent", "green")):
            cx, cy, r = 24 + i * 20, 20, 6
            self.draw.ellipse((px(cx - r), px(cy - r), px(cx + r), px(cy + r)), fill=self.t[color])
        tw = self.width(title, mono_font)
        self.text((WIDTH - tw) / 2, 25, title, mono_font, "muted")
        return 40

    def save(self, path, height):
        image = self.image.crop((0, 0, px(WIDTH), px(height)))
        mask = Image.new("L", image.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius=px(14), fill=255)
        out = Image.new("RGBA", image.size, (0, 0, 0, 0))
        out.paste(image, (0, 0), mask)
        out.save(path, optimize=True)


# ── Code ─────────────────────────────────────────────────────────────────────

CODE = """\
// Pick a family for some text: mono for code, sans or serif for prose
type Spacing = "mono" | "proportional";

interface Family {
  name: string;
  spacing: Spacing;
  cjk: boolean;
}

const families: Family[] = [
  { name: "Rec Mono St.Helens", spacing: "mono", cjk: true },
  { name: "Rec Sans Mt.Baker", spacing: "proportional", cjk: true },
  { name: "Rec Serif Mt.Adams", spacing: "proportional", cjk: true },
];

export async function pick(cp: number, code = true): Promise<Family> {
  const want = code ? "mono" : "proportional";
  const hit = families.find((f) => f.spacing === want && f.cjk);
  if (hit == null || cp <= 0x1f || cp !== cp) throw new Error("none");
  return hit; // => Rec Mono St.Helens
}

console.log(`中文 -> ${(await pick(0x4e2d)).name ?? "?"}`);"""

KEYWORDS = {"type", "interface", "const", "export", "async", "function", "return",
            "if", "throw", "new", "await", "true", "false", "null"}
TOKEN = re.compile(r"""
    (?P<comment>//.*$)
  | (?P<string>`[^`]*`|"[^"]*")
  | (?P<number>\b0x[0-9a-fA-F]+\b|\b\d+\b)
  | (?P<word>[A-Za-z_$][\w$]*)
  | (?P<op>[=!<>\-+*/%&|?:.]+)
  | (?P<other>.)
""", re.X)


def code_tokens(line):
    """Yield (text, color, italic). Operator runs stay whole so ligatures form."""
    for m in TOKEN.finditer(line):
        kind, text = m.lastgroup, m.group()
        if kind == "comment":
            yield text, "muted", True
        elif kind == "string":
            yield text, "green", False
        elif kind == "number":
            yield text, "magenta", False
        elif kind == "word":
            rest = line[m.end():]
            if text in KEYWORDS:
                yield text, "red", True
            elif text[0].isupper():
                yield text, "accent", False
            elif rest.startswith("("):
                yield text, "cyan", False
            else:
                yield text, "fg", False
        elif kind == "op":
            yield text, "blue", False
        else:
            yield text, "fg", False


def render_code(fam, card):
    size, lh = 14.5, 23
    regular = fam.font("mono", "Regular", size)
    italic = fam.font("mono", "Italic", size)
    y = card.window_chrome("families.ts — Rec Mono St.Helens", fam.font("mono", "Regular", 12)) + 6
    for n, line in enumerate(CODE.splitlines(), 1):
        y += lh
        num = str(n)
        card.text(PAD + 18 - card.width(num, regular), y, num, regular, "faint")
        x = PAD + 36
        for text, color, is_italic in code_tokens(line):
            x += card.text(x, y, text, italic if is_italic else regular, color)
    return y + 22


# ── Terminal ─────────────────────────────────────────────────────────────────

def east_asian_pad(s, width):
    used = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)
    return s + " " * (width - used)


def render_terminal(fam, card):
    size, lh = 14.5, 24
    font = fam.font("mono", "Regular", size)
    bold = fam.font("mono", "Bold", size)
    ascent, descent = font.getmetrics()
    y = card.window_chrome("zsh — Rec Mono St.Helens", fam.font("mono", "Regular", 12)) + 6
    x0 = PAD

    def prompt(y, command):
        segments = [
            (f" {ICONS['apple']} ", "bright", "selection"),
            (f" {ICONS['folder']} ~/rec-mountain-fonts ", "canvas", "blue"),
            (f" {ICONS['branch']} main {ICONS['check']} ", "canvas", "green"),
        ]
        x = x0
        top, bottom = y - ascent / SCALE, y + descent / SCALE
        for i, (text, fg, bg) in enumerate(segments):
            w = card.width(text, bold)
            card.rect(x, top, x + w, bottom, bg)
            card.text(x, y, text, bold, fg)
            x += w
            sep_bg = segments[i + 1][2] if i + 1 < len(segments) else None
            if sep_bg:
                card.rect(x, top, x + card.width(ICONS["pl_right"], font), bottom, sep_bg)
            x += card.text(x, y, ICONS["pl_right"], font, bg)
        x += card.text(x, y, " ", font, "fg")
        card.text(x, y, command, font, "fg")

    y += lh
    prompt(y, "eza --icons")
    y += lh
    listing = [("folder", "configs", "blue"), ("folder", "scripts", "blue"), ("folder", "wiki", "blue"),
               ("markdown", "README.md", "fg"), ("gear", "versions.env", "accent"),
               ("file", "requirements.txt", "fg")]
    x = x0
    for icon, name, color in listing:
        x += card.text(x, y, ICONS[icon] + " ", font, color)
        x += card.text(x, y, name + "   ", font, color)

    y += lh * 1.6
    prompt(y, "./scripts/build-all.sh")
    for line, color in [("✓ Rec Mono St.Helens: 4 styles verified (mono)", "green"),
                        ("✓ Rec Sans Mt.Baker: 4 styles verified (proportional)", "green"),
                        ("✓ Rec Serif Mt.Adams: 4 styles verified (proportional)", "green"),
                        ("=== All fonts built ===", "muted")]:
        y += lh
        card.text(x0, y, line, font, color)

    y += lh * 1.6
    rows = [("字体", "用途", "字宽"), ("Rec Mono St.Helens", "代码、终端", "等宽"),
            ("Rec Sans Mt.Baker", "文档、界面", "比例"),
            ("Rec Serif Mt.Adams", "长文阅读", "比例")]
    widths = (22, 14, 6)
    border = "─" * (sum(widths) + 2)
    box_lh = (ascent + descent) / SCALE  # box glyphs span exactly one line box
    card.text(x0, y, "╭" + border + "╮", font, "muted")
    for i, row in enumerate(rows):
        y += box_lh
        cells = "".join(east_asian_pad(c, w) for c, w in zip(row, widths))
        x = x0 + card.text(x0, y, "│ ", font, "muted")
        x += card.text(x, y, cells, bold if i == 0 else font, "accent" if i == 0 else "fg")
        card.text(x, y, " │", font, "muted")
    y += box_lh
    card.text(x0, y, "╰" + border + "╯", font, "muted")

    y += lh * 1.4
    icons = "  ".join(ICONS[k] for k in ("house", "github", "apple", "linux", "windows", "terminal",
                                         "code", "python", "rust", "typescript", "docker", "vim",
                                         "lock", "heart", "star", "clock"))
    card.text(x0, y, icons, font, "magenta")
    return y + 24


# ── Ligatures ────────────────────────────────────────────────────────────────

def render_ligatures(fam, card):
    big = fam.font("mono", "Regular", 26)
    small = fam.font("mono", "Regular", 11)
    title = fam.font("sans", "Bold", 18)
    label = fam.font("sans", "Regular", 12.5)
    y = PAD + 18
    card.text(PAD, y, "Code ligatures", title, "bright")
    card.text(PAD + card.width("Code ligatures", title) + 12, y, "on by default in Rec Mono St.Helens; off in the proportional families", label, "muted")
    cols, cell_w, cell_h = 6, (WIDTH - 2 * PAD) / 6, 74
    top = y + 18
    for i, seq in enumerate(LIGATURES):
        cx = PAD + (i % cols) * cell_w
        cy = top + (i // cols) * cell_h
        card.rect(cx + 4, cy + 4, cx + cell_w - 4, cy + cell_h - 4, "surface", radius=8)
        w = card.width(seq, big)
        card.text(cx + (cell_w - w) / 2, cy + 40, seq, big, "accent")
        plain = " ".join(seq)
        pw = card.width(plain, small, features=["-calt"])
        card.text(cx + (cell_w - pw) / 2, cy + 60, plain, small, "muted", features=["-calt"])
    rows = (len(LIGATURES) + cols - 1) // cols
    return top + rows * cell_h + PAD - 8


# ── Styles ───────────────────────────────────────────────────────────────────

def render_styles(fam, card):
    head = fam.font("sans", "Bold", 13)
    label = fam.font("mono", "Regular", 11)
    y = PAD
    samples = {
        "mono": "Quick brown fox -> 0O 1lI {}[] 字形",
        "sans": "The quick brown fox jumps · 中文排版",
        "serif": "The quick brown fox jumps · 中文排版",
    }
    for key in Families.KEYS:
        family = fam.name(key)
        y += 18
        card.text(PAD, y, family.upper(), head, "muted")
        y += 8
        for style in STYLES:
            y += 40
            card.text(PAD, y - 6, style, label, "muted")
            card.text(PAD + 100, y, samples[key], fam.font(key, style, 25), "bright" if "Bold" in style else "fg")
        y += 22
    return y + PAD - 22


# ── Text ─────────────────────────────────────────────────────────────────────

WRAP_TOKEN = re.compile(r"[　-鿿＀-￯]|[^\s　-鿿＀-￯]+\s*|\s+")


def wrap(card, text, font, max_width):
    lines, line = [], ""
    for token in WRAP_TOKEN.findall(text):
        if line and card.width((line + token).rstrip(), font) > max_width:
            lines.append(line.rstrip())
            line = token.lstrip()
        else:
            line += token
    if line.strip():
        lines.append(line.rstrip())
    return lines


def render_paragraphs(fam, card, key, subtitle, paragraphs):
    title = fam.font(key, "Bold", 30)
    sub = fam.font(key, "Italic", 15)
    body_w = WIDTH - 2 * PAD
    y = PAD + 26
    card.text(PAD, y, fam.name(key), title, "bright")
    y += 26
    card.text(PAD, y, subtitle, sub, "muted")
    for style, size, color, text in paragraphs:
        font = fam.font(key, style, size)
        y += 14
        for line in wrap(card, text, font, body_w):
            y += size * 1.6
            card.text(PAD, y, line, font, color)
    return y + PAD


def render_text(fam, card):
    return render_paragraphs(fam, card, "sans", "St.Helens's letterforms at their natural widths, for documents and UI.", [
        ("Regular", 16.5, "fg", "Recursive is a variable typeface inspired by casual script signpainting. "
                                "Mt.Baker keeps every letter at its natural width, so notes, documents, and "
                                "interfaces read like prose rather than code — numbers like 0123456789 included."),
        ("Italic", 16.5, "fg", "Italic and Bold Italic use the same cursive forms as the code font, so a "
                               "highlighted word looks the same in your editor and in your docs."),
        ("Regular", 16.5, "fg", "资源圆体为两套字体提供中文与日文字形。在 Mt.Baker 中，汉字使用比例宽度，"
                                "适合文档、笔记和界面；在 St.Helens 中，每个汉字占两个字符宽，与代码对齐。"),
        ("Regular", 16.5, "fg", "ひらがな・カタカナ・漢字も、同じ丸みのある書体で表示されます。"),
        ("Bold", 16.5, "accent", "Bold — The quick brown fox jumps over the lazy dog. 敏捷的棕色狐狸。"),
    ])


def render_serif(fam, card):
    return render_paragraphs(fam, card, "serif", "Anthropic Serif Text with Resource Han Rounded, for long-form reading.", [
        ("Regular", 17, "fg", "Mt.Adams pairs a book serif with the same CJK glyphs and Nerd Font icons as "
                              "the other two families, so articles, notes, and e-books can switch fonts without "
                              "losing Chinese, Japanese, or icons — figures like 0123456789 included."),
        ("Italic", 17, "fg", "Italic is for emphasis, titles of works, and asides; Bold uses the semibold "
                             "weight so it matches St.Helens and Mt.Baker."),
        ("Regular", 17, "fg", "资源圆体为 Mt.Adams 提供中文与日文字形，以比例宽度与衬线字母并排。"),
        ("Regular", 17, "fg", "ひらがな・カタカナ・漢字も、同じ丸みのある書体で表示されます。"),
        ("Bold", 17, "accent", "Bold — The quick brown fox jumps over the lazy dog. 敏捷的棕色狐狸。"),
    ])


# ── Chinese ──────────────────────────────────────────────────────────────────

def render_cjk(fam, card):
    head = fam.font("sans", "Bold", 13)
    label = fam.font("mono", "Regular", 11)
    y = PAD
    samples = {
        "mono": "print(\"你好，世界\")  # 中文注释对齐",
        "sans": "Rec Sans 与中文排版，自然而清晰。",
        "serif": "Rec Serif 与中文排版，宜于长文阅读。",
    }
    for key in Families.KEYS:
        y += 18
        card.text(PAD, y, fam.name(key).upper(), head, "muted")
        y += 8
        for style in ("Regular", "Bold"):
            y += 42
            card.text(PAD, y - 6, style, label, "muted")
            card.text(PAD + 100, y, samples[key], fam.font(key, style, 26), "bright" if style == "Bold" else "fg")
        y += 22
    return y + PAD - 22


# ── Glyphs ───────────────────────────────────────────────────────────────────

def render_glyphs(fam, card):
    label = fam.font("sans", "Regular", 12)
    glyph = fam.font("mono", "Regular", 24)
    rows = [
        ("Latin", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "bright"),
        ("", "abcdefghijklmnopqrstuvwxyz", "bright"),
        ("Digits and symbols", "0123456789 0O 1lI !?&@#$%^*()[]{}", "fg"),
        ("Vietnamese and accents", "ắằẳẵặ ếềểễệ ốồổỗộ ứừửữự ÀÉÎÕÜ ñ ç ß", "fg"),
        ("Greek (math)", "ΑΒΓΔΘΛΠΦ αβγδθλμπφ", "fg"),
        ("CJK", "永和九年 春夏秋冬 中文字体 漢字", "fg"),
        ("Kana and halfwidth", "あいうえお アイウエオ ｱｲｳｴｵ", "fg"),
        ("Box drawing and blocks", "┌ ┬ ┐ ├ ┼ ┤ └ ┴ ┘ ─ │ ╭ ╮ ╰ ╯ ═ ║ ░ ▒ ▓ █ ▀ ▄", "fg"),
        ("Powerline", f"{ICONS['pl_round_left']}{ICONS['pl_right']} {ICONS['branch']} "
                      f"        ", "accent"),
        ("Nerd Font icons", " ".join(ICONS[k] for k in ("house", "folder", "github", "apple", "linux",
                                                         "windows", "terminal", "code", "python", "rust",
                                                         "typescript", "docker", "vim", "markdown",
                                                         "gear", "lock", "heart", "star")), "magenta"),
    ]
    y = PAD
    for name, text, color in rows:
        if name:
            y += 30
            card.text(PAD, y, name, label, "muted")
        y += 36
        card.text(PAD, y, text, glyph, color)
    return y + PAD


# ── Hero ─────────────────────────────────────────────────────────────────────

def render_hero(fam, card):
    big = fam.font("sans", "Italic", 110)
    w = card.width("Aa永", big)
    card.text(WIDTH - PAD - w, PAD + 112, "Aa永", big, "selection")
    y = PAD + 46
    card.text(PAD, y, "Rec Mono St.Helens", fam.font("mono", "Bold", 40), "bright")
    y += 54
    card.text(PAD, y, "Rec Sans Mt.Baker", fam.font("sans", "Bold Italic", 40), "accent")
    y += 54
    card.text(PAD, y, "Rec Serif Mt.Adams", fam.font("serif", "Bold", 40), "blue")
    y += 34
    sub = fam.font("sans", "Regular", 15.5)
    card.text(PAD, y, "Recursive  ·  Anthropic Serif  ·  资源圆体 Resource Han Rounded  ·  Nerd Fonts", sub, "muted")
    mono = fam.font("mono", "Regular", 17)
    y += 38
    x = PAD
    for text, color in [("const ", "red"), ("ok", "fg"), (" = ", "blue"), ("a", "fg"), (" !== ", "blue"),
                        ("b", "fg"), (" && ", "blue"), ("c", "fg"), (" >= ", "blue"), ("0x1F", "magenta"),
                        ("; ", "fg"), ("// 中文 ", "muted"), (ICONS["github"] + " " + ICONS["apple"] + " "
                                                            + ICONS["python"] + " " + ICONS["rust"], "magenta")]:
        x += card.text(x, y, text, fam.font("mono", "Italic", 17) if text.startswith("//") else mono, color)
    return y + PAD


PREVIEWS = {
    "hero": render_hero,
    "code": render_code,
    "terminal": render_terminal,
    "ligatures": render_ligatures,
    "styles": render_styles,
    "text": render_text,
    "serif": render_serif,
    "cjk": render_cjk,
    "glyphs": render_glyphs,
}


def main():
    if len(sys.argv) > 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    if not features.check("raqm"):
        sys.exit("ERROR: Pillow was built without raqm; ligatures and CJK would not shape correctly")
    fam = Families(Path(sys.argv[1] if len(sys.argv) == 2 else "fonts"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, render in PREVIEWS.items():
        for theme in THEMES:
            card = Card(theme)
            height = render(fam, card)
            path = OUT_DIR / f"{name}-{theme}.png"
            card.save(path, height)
            print(f"  {path}")


if __name__ == "__main__":
    main()
