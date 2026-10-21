#!/usr/bin/env python3
"""Rebuild KaTeX's fonts and metrics from Libertinus.

usage: libertinus/build.py LIBERTINUS_OTF_DIR [REPORT_JSON]

LIBERTINUS_OTF_DIR holds the static OTF files of a Libertinus release.
See libertinus/README.md for what this writes and how to rebuild.
"""

import copy
import json
import re
import sys
from pathlib import Path

from fontTools import subset
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

LIB = Path(sys.argv[1])
REPORT = Path(sys.argv[2]) if len(sys.argv) > 2 else None
KATEX = Path(__file__).resolve().parent.parent

SOURCES = {
    "math": "LibertinusMath-Regular.otf",
    "math-turned": "LibertinusMath-Regular.otf",
    "serif": "LibertinusSerif-Regular.otf",
    "serif-italic": "LibertinusSerif-Italic.otf",
    "serif-bold": "LibertinusSerif-Bold.otf",
    "serif-bolditalic": "LibertinusSerif-BoldItalic.otf",
    "sans": "LibertinusSans-Regular.otf",
    "sans-italic": "LibertinusSans-Italic.otf",
    "sans-bold": "LibertinusSans-Bold.otf",
    "mono": "LibertinusMono-Regular.otf",
}


class Source:
    def __init__(self, key):
        self.key = key
        self.path = LIB / SOURCES[key]
        self.font = TTFont(self.path)
        self.cmap = self.font.getBestCmap()
        self.glyphs = self.font.getGlyphSet()
        self.upm = self.font["head"].unitsPerEm
        self.italic = {}
        self.accent = {}
        self.vvariants = {}
        self.hvariants = {}
        if "MATH" in self.font:
            math = self.font["MATH"].table
            info = math.MathGlyphInfo
            ic = info.MathItalicsCorrectionInfo
            self.italic = dict(zip(ic.Coverage.glyphs, (v.Value for v in ic.ItalicsCorrection)))
            ta = info.MathTopAccentAttachment
            self.accent = dict(zip(ta.TopAccentCoverage.glyphs, (v.Value for v in ta.TopAccentAttachment)))
            mv = math.MathVariants
            for coverage, constructions, into in (
                (mv.VertGlyphCoverage, mv.VertGlyphConstruction, self.vvariants),
                (mv.HorizGlyphCoverage, mv.HorizGlyphConstruction, self.hvariants),
            ):
                for glyph, c in zip(coverage.glyphs, constructions):
                    into[glyph] = [r.VariantGlyph for r in c.MathGlyphVariantRecord]
            self.constants = {
                k: getattr(v, "Value", v) for k, v in vars(math.MathConstants).items()
            }

    def bounds(self, glyph):
        pen = BoundsPen(self.glyphs)
        self.glyphs[glyph].draw(pen)
        return pen.bounds

    def operator_advance(self, glyph):
        return self.glyphs[glyph].width - self.italic.get(glyph, 0)

    def metrics(self, glyph, italic_font, operator=False, skewed=False):
        u = self.upm
        width = (self.operator_advance(glyph) if operator else self.glyphs[glyph].width) / u
        b = self.bounds(glyph)
        if b is None:
            return [0, 0, 0, 0, round(width, 5)]
        xmin, ymin, xmax, ymax = b
        if glyph in self.italic:
            italic = self.italic[glyph] / u
        elif italic_font:
            italic = max(0, xmax / u - width)
        else:
            italic = 0
        skew = self.accent[glyph] / u - width / 2 if skewed and glyph in self.accent else 0
        return [round(x, 5) for x in (max(0, -ymin / u), max(0, ymax / u), italic, skew, width)]


sources = {k: Source(k) for k in SOURCES}
math = sources["math"]

MATH_ALPHABETS = {
    "bold": (0x1D400, 0x1D41A),
    "italic": (0x1D434, 0x1D44E),
    "bolditalic": (0x1D468, 0x1D482),
    "script": (0x1D49C, 0x1D4B6),
    "boldscript": (0x1D4D0, 0x1D4EA),
    "fraktur": (0x1D504, 0x1D51E),
    "doublestruck": (0x1D538, 0x1D552),
    "boldfraktur": (0x1D56C, 0x1D586),
    "sans": (0x1D5A0, 0x1D5BA),
    "sansbold": (0x1D5D4, 0x1D5EE),
    "sansitalic": (0x1D608, 0x1D622),
    "mono": (0x1D670, 0x1D68A),
}
LETTERLIKE = {
    "italic": {"h": 0x210E},
    "script": {"B": 0x212C, "E": 0x2130, "F": 0x2131, "H": 0x210B, "I": 0x2110,
               "L": 0x2112, "M": 0x2133, "R": 0x211B, "e": 0x212F, "g": 0x210A, "o": 0x2134},
    "fraktur": {"C": 0x212D, "H": 0x210C, "I": 0x2111, "R": 0x211C, "Z": 0x2128},
    "doublestruck": {"C": 0x2102, "H": 0x210D, "N": 0x2115, "P": 0x2119, "Q": 0x211A,
                     "R": 0x211D, "Z": 0x2124},
}
MATH_DIGITS = {"bold": 0x1D7CE, "doublestruck": 0x1D7D8, "sans": 0x1D7E2,
               "sansbold": 0x1D7EC, "mono": 0x1D7F6}
MATH_GREEK = {"bold": (0x1D6A8, 0x1D6C2), "italic": (0x1D6E2, 0x1D6FC),
              "bolditalic": (0x1D71C, 0x1D736), "sansbold": (0x1D756, 0x1D770)}
GREEK_SYMBOLS = {0x2202: 25, 0x03F5: 26, 0x03D1: 27, 0x03F0: 28, 0x03D5: 29, 0x03F1: 30, 0x03D6: 31}
DOTLESS = {0x0131: 0x1D6A4, 0x0237: 0x1D6A5, 0xE131: 0x1D6A4, 0xE237: 0x1D6A5}


def alphabet(name, digits=True, greek=True, dotless=False, extra=None):
    def resolve(cp):
        c = chr(cp)
        target = None
        if "A" <= c <= "Z" or "a" <= c <= "z":
            target = LETTERLIKE.get(name, {}).get(c)
            if target is None and name in MATH_ALPHABETS:
                upper, lower = MATH_ALPHABETS[name]
                target = upper + ord(c) - 65 if c <= "Z" else lower + ord(c) - 97
        elif "0" <= c <= "9" and digits and name in MATH_DIGITS:
            target = MATH_DIGITS[name] + cp - 0x30
        elif greek and name in MATH_GREEK:
            upper, lower = MATH_GREEK[name]
            if 0x391 <= cp <= 0x3A9:
                target = upper + cp - 0x391
            elif 0x3B1 <= cp <= 0x3C9:
                target = lower + cp - 0x3B1
            elif cp in GREEK_SYMBOLS:
                target = lower + GREEK_SYMBOLS[cp]
        if dotless and cp in DOTLESS:
            target = DOTLESS[cp]
        if extra and cp in extra:
            target = extra[cp]
        glyph = math.cmap.get(target) if target else None
        return ("math", glyph) if glyph else None
    return resolve


def identity(key):
    def resolve(cp):
        glyph = sources[key].cmap.get(cp)
        return (key, glyph) if glyph else None
    return resolve


def substitute(key, table):
    def resolve(cp):
        glyph = sources[key].cmap.get(table.get(cp))
        return (key, glyph) if glyph else None
    return resolve


# KaTeX's fonts keep these at codepoints Libertinus leaves empty: the AMS
# corners at box-drawing codepoints, \triangleright and \triangleleft at the
# small triangles, and the \not slash in the private use area.
SUBSTITUTES = {
    0x250C: 0x231C, 0x2510: 0x231D, 0x2514: 0x231E, 0x2518: 0x231F,
    0x25B9: 0x25B7, 0x25C3: 0x25C1, 0xE020: 0x0338,
}


# Glyphs Libertinus lacks that are another of its glyphs turned over:
# \eqslantless and \eqslantgtr are \leqslant and \geqslant upside down.
TURNED = {0x2A95: 0x2A7D, 0x2A96: 0x2A7E}


def not_slash(source, glyph):
    # The combining solidus overlays the glyph before it; \not overlays the
    # relation after it, so its slash is centred on a relation's width.
    xmin, _, xmax, _ = source.bounds(glyph)
    return (1, 0, 0, 1, source.glyphs[source.cmap[ord("=")]].width / 2 - (xmin + xmax) / 2, 0)


def upside_down(source, glyph):
    _, ymin, _, ymax = source.bounds(glyph)
    return (1, 0, 0, -1, 0, ymin + ymax)


TRANSFORMS = {0xE020: not_slash, 0x2A95: upside_down, 0x2A96: upside_down}

TEXT_ACCENTS = {0x7E: 0x2DC, 0x5E: 0x2C6}


def accents(key, extra=None):
    def resolve(cp):
        src = sources[key]
        if extra and cp in extra:
            return (key, extra[cp])
        if cp in TEXT_ACCENTS and TEXT_ACCENTS[cp] in src.cmap:
            return (key, src.cmap[TEXT_ACCENTS[cp]])
        return None
    return resolve


class Polygons(BasePen):
    def __init__(self, glyphs):
        super().__init__(glyphs)
        self.contours = []
        self.current = []

    def _moveTo(self, p):
        self.current = [p]

    def _lineTo(self, p):
        self.current.append(p)

    def _curveToOne(self, a, b, c):
        p0 = self.current[-1]
        for i in range(1, 17):
            t = i / 16
            u = 1 - t
            self.current.append((
                u ** 3 * p0[0] + 3 * u * u * t * a[0] + 3 * u * t * t * b[0] + t ** 3 * c[0],
                u ** 3 * p0[1] + 3 * u * u * t * a[1] + 3 * u * t * t * b[1] + t ** 3 * c[1]))

    def _qCurveToOne(self, a, b):
        p0 = self.current[-1]
        for i in range(1, 17):
            t = i / 16
            u = 1 - t
            self.current.append((u * u * p0[0] + 2 * u * t * a[0] + t * t * b[0],
                                 u * u * p0[1] + 2 * u * t * a[1] + t * t * b[1]))

    def _closePath(self):
        self.contours.append(self.current)
        self.current = []

    _endPath = _closePath


def mean_gap(source, glyph, side, lines=200):
    pen = Polygons(source.glyphs)
    source.glyphs[glyph].draw(pen)
    edges = [(c[i], c[(i + 1) % len(c)]) for c in pen.contours for i in range(len(c))]
    ys = [p[1] for c in pen.contours for p in c]
    bottom, top = min(ys), max(ys)
    advance = source.glyphs[glyph].width
    gaps = []
    for k in range(lines):
        y = bottom + (top - bottom) * (k + 0.5) / lines
        xs = [a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
              for a, b in edges if (a[1] <= y < b[1]) or (b[1] <= y < a[1])]
        if xs:
            gaps.append(advance - max(xs) if side == "right" else min(xs))
    return sum(gaps) / len(gaps)


OPTICAL = {ord("{"): ("right", ("\\{", "\\lbrace")), ord("}"): ("left", ("\\}", "\\rbrace"))}


def optical_margin(cp, glyph):
    side = OPTICAL[cp][0]
    reference = glyph.replace("brace", "paren")
    return round(max(0, mean_gap(math, reference, side) - mean_gap(math, glyph, side)) / math.upm, 3)


def bar_ranges(source, glyph):
    pen = Polygons(source.glyphs)
    source.glyphs[glyph].draw(pen)
    ranges = sorted((min(p[0] for p in c), max(p[0] for p in c)) for c in pen.contours)
    return [(round(a), round(b)) for a, b in ranges]


def fmt(v):
    text = f"{round(v, 1):.1f}".removesuffix(".0")
    return "0" if text == "-0" else text


class FlippedPath(BasePen):
    def __init__(self, glyphs, top, dx=0, top_expr=None):
        super().__init__(glyphs)
        self.top = top
        self.dx = dx
        self.top_expr = top_expr
        self.parts = []
        self.current = None
        self.start = None

    def flip(self, pt):
        return (pt[0] + self.dx, self.top - pt[1])

    def _moveTo(self, pt):
        x, y = self.flip(pt)
        if self.top_expr and self.current is None:
            offset = -(y - self.top)
            self.parts.append(f"M{fmt(x)} ${{{self.top_expr} - {fmt(offset)}}}")
        elif self.top_expr:
            self.parts.append(f"m{fmt(x - self.current[0])} {fmt(y - self.current[1])}")
        else:
            self.parts.append(f"M{fmt(x)} {fmt(y)}")
        self.current = self.start = (x, y)

    def _lineTo(self, pt):
        x, y = self.flip(pt)
        if self.top_expr:
            self.parts.append(f"l{fmt(x - self.current[0])} {fmt(y - self.current[1])}")
        else:
            self.parts.append(f"L{fmt(x)} {fmt(y)}")
        self.current = (x, y)

    def _curveToOne(self, a, b, c):
        pts = [self.flip(q) for q in (a, b, c)]
        if self.top_expr:
            cx, cy = self.current
            self.parts.append("c" + " ".join(f"{fmt(x - cx)} {fmt(y - cy)}" for x, y in pts))
        else:
            self.parts.append("C" + " ".join(f"{fmt(x)} {fmt(y)}" for x, y in pts))
        self.current = pts[-1]

    def _closePath(self):
        self.parts.append("z")
        self.current = self.start

    _endPath = _closePath

    def path(self):
        return "".join(self.parts)


def glyph_path(glyph, top, top_expr=None, dx=0):
    pen = FlippedPath(math.glyphs, top, dx=dx, top_expr=top_expr)
    math.glyphs[glyph].draw(pen)
    return pen.path()


def sized(cp, target_total):
    glyph = math.cmap.get(cp)
    if glyph is None:
        return None
    if glyph in math.vvariants:
        def total(g):
            b = math.bounds(g)
            return (b[3] - b[1]) / math.upm if b else 0
        candidates = math.vvariants[glyph]
        return ("math", min(candidates, key=lambda g: abs(total(g) - target_total)))
    return ("math", glyph)


KATEX_FONTS = {
    "AMS-Regular": [alphabet("doublestruck", extra={ord("k"): 0x1D55C}), identity("math"),
                    substitute("math", SUBSTITUTES), substitute("math-turned", TURNED),
                    identity("serif")],
    "Caligraphic-Regular": [alphabet("script"), identity("math")],
    "Fraktur-Regular": [alphabet("fraktur"), identity("serif")],
    "Main-Regular": [accents("math", {0x2032: "minute.ssty1"}), identity("math"), identity("serif"),
                     substitute("math", SUBSTITUTES)],
    "Main-Bold": [accents("serif-bold"), alphabet("bold"), identity("serif-bold"), identity("math"),
                  substitute("serif-bold", SUBSTITUTES)],
    "Main-Italic": [accents("serif-italic"), identity("serif-italic")],
    "Main-BoldItalic": [accents("serif-bolditalic"), identity("serif-bolditalic")],
    "Math-Italic": [alphabet("italic", dotless=True), identity("math")],
    "Math-BoldItalic": [alphabet("bolditalic", dotless=True), alphabet("bold"), identity("math")],
    "SansSerif-Regular": [accents("sans"), alphabet("sans"), identity("sans")],
    "SansSerif-Bold": [accents("sans-bold"), alphabet("sansbold"), identity("sans-bold")],
    "SansSerif-Italic": [accents("sans-italic"), alphabet("sansitalic", digits=False), identity("sans-italic")],
    "Script-Regular": [alphabet("script"), identity("math")],
    "Typewriter-Regular": [alphabet("mono"), identity("mono"), identity("math")],
    "Size1-Regular": "sized",
    "Size2-Regular": "sized",
    "Size3-Regular": "sized",
    "Size4-Regular": "sized",
}
EXTRA_FONT_FILES = {
    "Caligraphic-Bold": ("Caligraphic-Regular", [alphabet("boldscript"), identity("math")]),
    "Fraktur-Bold": ("Fraktur-Regular", [alphabet("boldfraktur"), identity("serif-bold")]),
}
ZERO_WIDTH_SPACE = 0x200B
SKEWED_FONTS = {"Math-Italic", "Math-BoldItalic", "Caligraphic-Regular", "Script-Regular"}
ITALIC_FONTS = {"Main-Italic", "Main-BoldItalic", "Math-Italic", "Math-BoldItalic", "SansSerif-Italic"}


def load_katex_metrics():
    return json.loads((KATEX / "libertinus/katex-metrics.json").read_text())


FACES = {
    "AMS-Regular": ("AMS", "normal", "normal"),
    "Caligraphic-Bold": ("Caligraphic", "bold", "normal"),
    "Caligraphic-Regular": ("Caligraphic", "normal", "normal"),
    "Fraktur-Bold": ("Fraktur", "bold", "normal"),
    "Fraktur-Regular": ("Fraktur", "normal", "normal"),
    "Main-Bold": ("Main", "bold", "normal"),
    "Main-BoldItalic": ("Main", "bold", "italic"),
    "Main-Italic": ("Main", "normal", "italic"),
    "Main-Regular": ("Main", "normal", "normal"),
    "Math-BoldItalic": ("Math", "bold", "italic"),
    "Math-Italic": ("Math", "normal", "italic"),
    "SansSerif-Bold": ("SansSerif", "bold", "normal"),
    "SansSerif-Italic": ("SansSerif", "normal", "italic"),
    "SansSerif-Regular": ("SansSerif", "normal", "normal"),
    "Script-Regular": ("Script", "normal", "normal"),
    "Size1-Regular": ("Size1", "normal", "normal"),
    "Size2-Regular": ("Size2", "normal", "normal"),
    "Size3-Regular": ("Size3", "normal", "normal"),
    "Size4-Regular": ("Size4", "normal", "normal"),
    "Typewriter-Regular": ("Typewriter", "normal", "normal"),
}


def copy_vertical_metrics(font, reference):
    for table, fields in (
        ("hhea", ("ascent", "descent", "lineGap")),
        ("OS/2", ("sTypoAscender", "sTypoDescender", "sTypoLineGap", "usWinAscent", "usWinDescent")),
    ):
        for field in fields:
            setattr(font[table], field, getattr(reference[table], field))
    use_typo = 1 << 7
    font["OS/2"].fsSelection = (font["OS/2"].fsSelection & ~use_typo) | (reference["OS/2"].fsSelection & use_typo)


def transform_glyph(font, glyph, matrix):
    glyphs = font.getGlyphSet()
    pen = T2CharStringPen(None, glyphs)
    glyphs[glyph].draw(TransformPen(pen, matrix))
    charstrings = font["CFF "].cff.topDictIndex[0].CharStrings
    old = charstrings[glyph]
    charstrings[glyph] = pen.getCharString(private=old.private, globalSubrs=old.globalSubrs)


def write_subset(source, mapping, reference, path, advances, transforms):
    font = TTFont(source.path, recalcTimestamp=False)
    hmtx = font["hmtx"]
    for glyph, advance in advances.items():
        hmtx[glyph] = (advance, hmtx[glyph][1])
    for table in font["cmap"].tables:
        table.cmap = dict(mapping)
    options = subset.Options()
    options.layout_features = []
    options.drop_tables += ["GSUB", "GPOS", "GDEF", "MATH", "BASE", "JSTF"]
    options.notdef_outline = True
    options.hinting = False
    options.name_IDs = ["*"]
    options.flavor = "woff2"
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=list(mapping))
    subsetter.subset(font)
    for glyph, matrix in transforms.items():
        transform_glyph(font, glyph, matrix)
    copy_vertical_metrics(font, reference)
    font.flavor = "woff2"
    font.save(path)


def resolve_font(name, resolvers, cps, original):
    chosen = {}
    for cp in cps:
        if resolvers == "sized":
            target = original[str(cp)][0] + original[str(cp)][1]
            hit = sized(cp, target)
        else:
            hit = next((h for r in resolvers if (h := r(cp))), None)
        if hit:
            chosen[cp] = hit
    return chosen


def main():
    original = load_katex_metrics()
    metrics = copy.deepcopy(original)
    report = {}
    optical = {}
    extenders = {}
    faces = []

    jobs = [(name, name, resolvers) for name, resolvers in KATEX_FONTS.items()]
    jobs += [(file, metric_font, resolvers) for file, (metric_font, resolvers) in EXTRA_FONT_FILES.items()]

    for file, metric_font, resolvers in jobs:
        family, weight, style = FACES[file]
        cps = sorted(map(int, original[metric_font]))
        chosen = resolve_font(file, resolvers, cps, original[metric_font])
        reference = TTFont(KATEX / f"fonts/KaTeX_{file}.ttf")

        operators = resolvers == "sized"
        if operators:
            for cp, (key, glyph) in chosen.items():
                if cp in OPTICAL and key == "math":
                    optical.setdefault(chr(cp), {})[file.split("-")[0].lower()] = optical_margin(cp, glyph)
                if cp in EXTENDERS and key == "math" and file in ("Size1-Regular", "Size4-Regular"):
                    extenders.setdefault(cp, {})[file] = bar_ranges(math, glyph)
        by_source = {}
        for cp, (key, glyph) in chosen.items():
            by_source.setdefault(key, {})[cp] = glyph
            if file == metric_font:
                metrics[metric_font][str(cp)] = sources[key].metrics(
                    glyph, metric_font in ITALIC_FONTS, operators, metric_font in SKEWED_FONTS)
        # KaTeX puts a zero-width space in every multi-row vlist. It has no
        # metrics, but without a Libertinus glyph for it the browser loads
        # the whole KaTeX font of the surrounding family to draw nothing.
        key = max((k for k in by_source if ZERO_WIDTH_SPACE in sources[k].cmap), key=lambda k: len(by_source[k]))
        by_source[key][ZERO_WIDTH_SPACE] = sources[key].cmap[ZERO_WIDTH_SPACE]
        for key, mapping in by_source.items():
            name = f"Libertinus_{file}_{key}.woff2"
            source = sources[key]
            advances = {g: source.operator_advance(g) for g in mapping.values() if operators and g in source.italic}
            transforms = {g: TRANSFORMS[cp](source, g) for cp, g in mapping.items() if cp in TRANSFORMS}
            write_subset(source, mapping, reference, KATEX / "fonts" / name, advances, transforms)
            faces.append(face(family, weight, style, name, unicode_range(mapping)))

        report[file] = {
            "from": {key: len(m) for key, m in by_source.items()},
            "katex_fallback": "".join(chr(cp) for cp in cps if cp not in chosen and cp > 32),
        }

    sigmas = global_metrics()
    write_scss(faces)
    write_metrics_data(metrics)
    write_sigmas(sigmas)
    write_size_style_map(size_style_map())
    write_optical_margins(optical)
    write_inner_paths(extenders)
    write_radicals()
    write_stretchy()
    if REPORT:
        REPORT.write_text(json.dumps(
            {"fonts": report, "sigmas": sigmas, "sizeStyleMap": size_style_map(), "optical": optical},
            indent=1, ensure_ascii=False))


def face(family, weight, style, file, urange):
    return "\n".join([
        "@font-face {",
        f"    font-family: KaTeX_{family};",
        f'    src: url("#{{fonts.$font-folder}}/{file}") format("woff2");',
        f"    font-weight: {weight};",
        f"    font-style: {style};",
        "    font-display: fonts.$font-display;",
        *unicode_range_lines(urange),
        "}",
    ])


def unicode_range_lines(urange):
    items = (urange + ";").split(" ")
    return ["    unicode-range:"] + ["        " + item for item in items]


def write_scss(faces):
    (KATEX / "src/styles/libertinus.scss").write_text(
        "// This file is GENERATED by libertinus/build.py. DO NOT MODIFY.\n"
        "// Declared after fonts.scss, so these faces win for the characters\n"
        "// they cover and the KaTeX faces fill in the rest.\n\n"
        "@use \"fonts.scss\";\n\n"
        + "\n\n".join(faces) + "\n")
    # KaTeX's own fonts are not shipped: Libertinus's faces are the only
    # ones, and characters Libertinus lacks fall back to the reader's fonts.
    fonts_scss = KATEX / "src/styles/fonts.scss"
    fonts_scss.write_text(re.sub(r"^@include font-face\(.*\);\n", "", fonts_scss.read_text(), flags=re.M).rstrip() + "\n")
    katex_scss = KATEX / "src/styles/katex.scss"
    text = katex_scss.read_text()
    if '@use "libertinus.scss";' not in text:
        text, n = re.subn(r'^@use "fonts\.scss";\n', '@use "fonts.scss";\n@use "libertinus.scss";\n', text,
                          count=1, flags=re.M)
        if n != 1:
            raise ValueError('@use "fonts.scss" not found in katex.scss')
        katex_scss.write_text(text)


EXTENDERS = {0x239C, 0x239F, 0x23A2, 0x23A5, 0x23AA, 0x23D0, 0x2016, 0x2223, 0x2225}


def write_optical_margins(optical):
    lines = ["// This file is GENERATED by libertinus/build.py. DO NOT MODIFY.",
             "// Extra space on the content side of large braces, in em, so their",
             "// mean distance to the content matches a parenthesis of the same",
             "// size.",
             'import type {DelimiterSize} from "./types";',
             "",
             "export type OpticalMargin = {",
             '    side: "left" | "right",',
             "    sizes: Partial<Record<DelimiterSize, number>>,",
             "    stack?: number,",
             "};",
             "",
             "const opticalMargins: Partial<Record<string, OpticalMargin>> = {"]
    for cp, (side, names) in OPTICAL.items():
        sizes = optical[chr(cp)]
        by_size = ", ".join(f"{k[-1]}: {js_number(v)}" for k, v in sorted(sizes.items()))
        for name in names:
            lines += [f"    {json.dumps(name)}: {{",
                      f'        side: "{side}",',
                      f"        sizes: {{{by_size}}},",
                      f"        stack: {js_number(sizes['size4'])},",
                      "    },"]
    lines += ["};", "", "export default opticalMargins;"]
    (KATEX / "src/opticalMargins.ts").write_text("\n".join(lines) + "\n")


def write_inner_paths(extenders):
    path = KATEX / "src/svgGeometry.ts"
    text = path.read_text()
    start = text.index("export const innerPath")
    end = text.index("};", start)
    body = text[start:end]
    for cp, by_font in extenders.items():
        bars = by_font.get("Size4-Regular") or by_font["Size1-Regular"]
        case = f'case "\\u{cp:04x}":'
        at = body.index(case)
        stop = body.find("case ", at + len(case))
        stop = body.index("default:", at) if stop == -1 else stop
        block = body[at:stop]
        old = re.findall(r"M(\d+) 0 H(\d+)", block)
        if len(set(old)) != len(bars):
            raise ValueError(f"U+{cp:04X}: {len(set(old))} bars in KaTeX, {len(bars)} in Libertinus")
        mapping = dict(zip(sorted(set(old), key=lambda r: int(r[0])), bars))
        block = re.sub(r"M(\d+) 0 H(\d+) V\$\{height\} H(\d+)z",
                       lambda m: "M{0} 0 H{1} V${{height}} H{0}z".format(*mapping[(m.group(1), m.group(2))]), block)
        body = body[:at] + block + body[stop:]
    path.write_text(text[:start] + body + text[end:])




def radical_assembly():
    variants = math.font["MATH"].table.MathVariants
    index = variants.VertGlyphCoverage.glyphs.index(math.cmap[0x221A])
    parts = variants.VertGlyphConstruction[index].GlyphAssembly.PartRecords
    bottom, extender, top = (p.glyph for p in parts)
    if [p.PartFlags for p in parts] != [0, 1, 0]:
        raise ValueError("unexpected radical assembly")
    return bottom, extender, top, variants.MinConnectorOverlap


BOX = 400000
OVERLAP = 20


def rect(x0, y0, x1, y1):
    return f"M{fmt(x0)} {fmt(y0)}V{fmt(y1)}H{fmt(x1)}V{fmt(y0)}z"


def crossings(glyph, x=None, y=None):
    pen = Polygons(math.glyphs)
    math.glyphs[glyph].draw(pen)
    hits = []
    for c in pen.contours:
        for a, b in zip(c, c[1:] + c[:1]):
            if x is not None and (a[0] <= x < b[0] or b[0] <= x < a[0]):
                hits.append(a[1] + (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0]))
            if y is not None and (a[1] <= y < b[1] or b[1] <= y < a[1]):
                hits.append(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
    hits.sort()
    return list(zip(hits[::2], hits[1::2]))


def stretched(glyph, anchor, top, bars=None):
    xmin, _, xmax, _ = math.bounds(glyph)
    if anchor == "right":
        dx = BOX - xmax
        tail = xmin
    elif anchor == "left":
        dx = -xmin
        tail = xmax
    else:
        dx = BOX / 2 - (xmin + xmax) / 2
    if bars is None:
        inside = (xmax - xmin) / 4
        bars = crossings(glyph, x=tail + inside if anchor == "right" else tail - inside)
    path = glyph_path(glyph, top, dx=dx)
    for y0, y1 in bars:
        a, b = top - y1, top - y0
        if anchor in ("right", "mid"):
            path += rect(0, a, xmin + dx + OVERLAP, b)
        if anchor in ("left", "mid"):
            path += rect(xmax + dx - OVERLAP, a, BOX, b)
    return path


ARROWS = {
    "rightarrow": ("arrowright.right", "right", "extender"),
    "leftarrow": ("arrowleft.left", "left", "extender"),
    "doublerightarrow": (0x21D2, "right", "measured"),
    "doubleleftarrow": (0x21D0, "left", "measured"),
    "rightharpoon": (0x21C0, "right", "measured"),
    "leftharpoon": (0x21BC, "left", "measured"),
    "rightharpoondown": (0x21C1, "right", "measured"),
    "leftharpoondown": (0x21BD, "left", "measured"),
    "twoheadrightarrow": (0x21A0, "right", "measured"),
    "twoheadleftarrow": (0x219E, "left", "measured"),
    "leftmapsto": ("uni21A6.left", "left", "extender"),
    "lefthook": ("uni21AA.left", "left", "extender"),
    "righthook": ("uni21A9.right", "right", "extender"),
}
ACCENT_ARROWS = {
    "accentrightarrow": (0x20D7, "right", "over"),
    "accentleftarrow": (0x20D6, "left", "over"),
    "accentrightharpoon": (0x20D1, "right", "over"),
    "accentleftharpoon": (0x20D0, "left", "over"),
    "underaccentrightarrow": (0x20EF, "right", "under"),
    "underaccentleftarrow": (0x20EE, "left", "under"),
}
ROW_PATHS = {
    "overrightarrow": ["accentrightarrow"],
    "overleftarrow": ["accentleftarrow"],
    "overleftrightarrow": ["accentleftarrow", "accentrightarrow"],
    "overrightharpoon": ["accentrightharpoon"],
    "overleftharpoon": ["accentleftharpoon"],
    "underrightarrow": ["underaccentrightarrow"],
    "underleftarrow": ["underaccentleftarrow"],
    "underleftrightarrow": ["underaccentleftarrow", "underaccentrightarrow"],
}
BRACES = {0x23DE: ("leftbrace", "midbrace", "rightbrace"),
          0x23DF: ("leftbraceunder", "midbraceunder", "rightbraceunder")}
WIDE_ACCENTS = {"widehat": 0x302, "widecheck": 0x30C, "tilde": 0x303}
WIDE_ACCENT_SIZES = [1, 1, 2, 3, 4, 4, 5]


def horizontal_assembly(cp):
    variants = math.font["MATH"].table.MathVariants
    index = variants.HorizGlyphCoverage.glyphs.index(math.cmap[cp])
    return [p.glyph for p in variants.HorizGlyphConstruction[index].GlyphAssembly.PartRecords]


HORIZONTAL_BRACE_DESIGN = "vertical"
ROTATED_BRACES = {
    "over": ((0, -1, 1, 0, 0, 0), ("leftbrace", "midbrace", "rightbrace")),
    "under": ((0, 1, -1, 0, 0, 0), ("leftbraceunder", "midbraceunder", "rightbraceunder")),
}


def turned_bounds(glyph, matrix):
    pen = BoundsPen(math.glyphs)
    math.glyphs[glyph].draw(TransformPen(pen, matrix))
    return pen.bounds


def turned_stretched(glyph, matrix, anchor, top, bars):
    xmin, _, xmax, _ = turned_bounds(glyph, matrix)
    if anchor == "right":
        dx = BOX - xmax
    elif anchor == "left":
        dx = -xmin
    else:
        dx = BOX / 2 - (xmin + xmax) / 2
    pen = FlippedPath(math.glyphs, top, dx=dx)
    math.glyphs[glyph].draw(TransformPen(pen, matrix))
    path = pen.path()
    for y0, y1 in bars:
        a, b = top - y1, top - y0
        if anchor in ("right", "mid"):
            path += rect(0, a, xmin + dx + OVERLAP, b)
        if anchor in ("left", "mid"):
            path += rect(xmax + dx - OVERLAP, a, BOX, b)
    return path


def rotated_braces(paths, heights):
    bottom_hook, extender, middle, _, top_hook = (p.glyph for p in vertical_assembly(ord("{")))
    for side, (matrix, names) in ROTATED_BRACES.items():
        pieces = (bottom_hook, middle, top_hook)
        left, right = (bottom_hook, top_hook) if side == "over" else (top_hook, bottom_hook)
        bounds = [turned_bounds(g, matrix) for g in pieces]
        top = max(b[3] for b in bounds)
        bottom = min(b[1] for b in bounds)
        _, ey0, _, ey1 = turned_bounds(extender, matrix)
        bars = [(ey0, ey1)]
        left_name, mid_name, right_name = names
        paths[left_name] = turned_stretched(left, matrix, "left", top, bars)
        paths[mid_name] = turned_stretched(middle, matrix, "mid", top, bars)
        paths[right_name] = turned_stretched(right, matrix, "right", top, bars)
        for name in names:
            heights[name] = round(top - bottom)


def vertical_assembly(cp):
    variants = math.font["MATH"].table.MathVariants
    index = variants.VertGlyphCoverage.glyphs.index(math.cmap[cp])
    return variants.VertGlyphConstruction[index].GlyphAssembly.PartRecords


def write_stretchy():
    axis = math.constants["AxisHeight"]
    paths = {}
    heights = {}

    glyphs = {name: math.cmap[g] if isinstance(g, int) else g for name, (g, _, _) in ARROWS.items()}
    reach = max(max(math.bounds(g)[3] - axis, axis - math.bounds(g)[1]) for g in glyphs.values())
    arrow_height = 2 * round(reach)
    extender = horizontal_assembly(0x2192)[1]
    _, shaft_bottom, _, shaft_top = math.bounds(extender)
    for name, (_, anchor, shaft) in ARROWS.items():
        bars = [(shaft_bottom, shaft_top)] if shaft == "extender" else None
        paths[name] = stretched(glyphs[name], anchor, arrow_height / 2 + axis, bars)
        heights[name] = arrow_height

    base = math.constants["AccentBaseHeight"]
    for name, (cp, anchor, side) in ACCENT_ARROWS.items():
        glyph = math.cmap[cp]
        _, ymin, _, ymax = math.bounds(glyph)
        shaft = horizontal_assembly(cp)[0 if anchor == "right" else 1]
        _, y0, _, y1 = math.bounds(shaft)
        top = ymax if side == "over" else 0
        paths[name] = stretched(glyph, anchor, top, [(y0, y1)])
        heights[name] = round(ymax - base) if side == "over" else round(-ymin)

    equal = math.cmap[ord("=")]
    _, ymin, _, ymax = math.bounds(equal)
    equal_height = 2 * round(max(ymax - axis, axis - ymin))
    top = equal_height / 2 + axis
    paths["longequal"] = "".join(rect(0, top - y1, BOX, top - y0)
                                 for y0, y1 in crossings(equal, x=(math.bounds(equal)[0] + math.bounds(equal)[2]) / 2))
    heights["longequal"] = equal_height

    if HORIZONTAL_BRACE_DESIGN == "vertical":
        rotated_braces(paths, heights)
    for cp, (left, mid, right) in (BRACES if HORIZONTAL_BRACE_DESIGN == "horizontal" else {}).items():
        lt, ex, md, ex2, rt = horizontal_assembly(cp)
        parts = (lt, ex, md, rt)
        top = max(math.bounds(g)[3] for g in parts)
        bottom = min(math.bounds(g)[1] for g in parts)
        _, ey0, _, ey1 = math.bounds(ex)
        bars = [(ey0, ey1)]
        paths[left] = stretched(lt, "left", top, bars)
        paths[mid] = stretched(md, "mid", top, bars)
        paths[right] = stretched(rt, "right", top, bars)
        for name in (left, mid, right):
            heights[name] = round(top - bottom)

    images = {}
    for name, cp in WIDE_ACCENTS.items():
        variants = math.font["MATH"].table.MathVariants
        index = variants.HorizGlyphCoverage.glyphs.index(math.cmap[cp])
        ladder = [r.VariantGlyph for r in variants.HorizGlyphConstruction[index].MathGlyphVariantRecord]
        rows = {}
        for size in sorted(set(WIDE_ACCENT_SIZES)):
            glyph = ladder[size]
            xmin, _, xmax, ymax = math.bounds(glyph)
            paths[f"{name}{size}"] = glyph_path(glyph, ymax, dx=-xmin)
            rows[size] = [f"{name}{size}", round(xmax - xmin), round(ymax - base), round(ymax - base) / 1000]
        images[name] = [rows[size] for size in WIDE_ACCENT_SIZES]

    vec = math.cmap[0x20D7]
    _, _, _, vec_top = math.bounds(vec)
    paths["vec"] = glyph_path(vec, vec_top)
    vec_data = (math.glyphs[vec].width / 1000, vec_top / 1000)

    write_svg_paths(paths)
    write_image_heights(heights)
    write_wide_accent_images(images)
    write_vec_data(vec_data)


def write_svg_paths(paths):
    geometry = KATEX / "src/svgGeometry.ts"
    text = geometry.read_text()
    start = text.index("export const path")
    end = text.index("\n};", start)
    block = text[start:end]
    for name, path in paths.items():
        entry = "\n".join(path_lines(path, f"    {name}: `", "`,"))
        block, n = re.subn(rf"^    {name}: (?:doubleBrushStroke\()?`[^`]*`\)?,", lambda m: entry, block,
                           flags=re.M)
        if n == 0:
            block += "\n" + entry
        elif n > 1:
            raise ValueError(f"path {name} defined twice")
    geometry.write_text(text[:start] + block + text[end:])


def write_image_heights(heights):
    stretchy = KATEX / "src/stretchy.ts"
    text = stretchy.read_text()
    start = text.index("const katexImagesData")
    end = text.index("\n};", start)
    block = text[start:end]
    row = re.compile(r'(\n\s+(?:"[^"]+"|\w+): \[\[)([^\]]*)(\],\s*[\d.]+,\s*)(\d+)')
    used = {}

    def replace(m):
        label = m.group(1).strip().split(":")[0].strip('"')
        names = re.findall(r'"(\w+)"', m.group(2))
        if label in ROW_PATHS:
            names = ROW_PATHS[label]
            m = re.match(row, m.group(1) + ", ".join(f'"{n}"' for n in names) + m.group(3) + m.group(4))
        for n in names:
            used.setdefault(n, set()).add(all(x in heights for x in names))
        if not all(n in heights for n in names):
            return m.group(0)
        sizes = {heights[n] for n in names}
        if len(sizes) != 1:
            raise ValueError(f"paths {names} need different heights")
        return m.group(1) + m.group(2) + m.group(3) + str(sizes.pop())

    block = row.sub(replace, block)
    block = "\n".join(line.replace("], ", "],\n        ", 1) if len(line) > MAX_LINE else line
                      for line in block.split("\n"))
    mixed = [n for n, kinds in used.items() if n in heights and False in kinds]
    if mixed:
        raise ValueError(f"paths {mixed} are also used with Computer Modern paths")
    stretchy.write_text(text[:start] + block + text[end:])


def write_wide_accent_images(images):
    lines = ["// This file is GENERATED by libertinus/build.py. DO NOT MODIFY.",
             "export type WideAccentImage = [string, number, number, number];",
             "",
             "// Images for \\widehat, \\widecheck, \\widetilde and \\utilde, indexed by",
             "// the number of characters under the accent (the last entry covers",
             "// anything longer): [path name, viewBox width, viewBox height, height",
             "// in em]. The image is stretched to the width of its base.",
             ""]
    for name, rows in images.items():
        lines.append(f"const {name}: WideAccentImage[] = [")
        lines += [f'    ["{r[0]}", {r[1]}, {r[2]}, {js_number(r[3])}],' for r in rows]
        lines += ["];", ""]
    lines += ["const wideAccentImages: Record<string, WideAccentImage[]> =",
              "    {widehat, widecheck, widetilde: tilde, utilde: tilde};",
              "",
              "// The smallest images are Libertinus's ordinary accents, which keep",
              "// their shape only at their own size.",
              "export const naturalSizeOverNarrowBase = true;",
              "",
              "export default wideAccentImages;"]
    (KATEX / "src/wideAccentImages.ts").write_text("\n".join(lines) + "\n")


def write_vec_data(vec_data):
    common = KATEX / "src/buildCommon.ts"
    text = common.read_text()
    width, height = (js_number(v) for v in vec_data)
    text, n = re.subn(r'vec: \["vec", [\d.]+, [\d.]+\],', f'vec: ["vec", {width}, {height}],', text)
    if n != 1:
        raise ValueError("vec svgData not found in buildCommon.ts")
    common.write_text(text)


def write_radicals():
    geometry = KATEX / "src/svgGeometry.ts"
    text = geometry.read_text()
    pad = int(re.search(r"^const hLinePad = (\d+);", text, re.M).group(1))
    rule = math.constants["RadicalRuleThickness"]
    u = math.upm
    table = {}

    def replace_function(text, name, body):
        start = text.index(f"const {name} = function(")
        end = text.index("\n};\n", start) + 4
        return text[:start] + body + text[end:]

    # Every pre-drawn radical in Libertinus Math: the first is the text-size
    # surd, the rest are the sizes used before a tall surd is assembled.
    variants = math.vvariants[math.cmap[0x221A]]
    sizes = []
    for i, glyph in enumerate(variants):
        xmin, ymin, xmax, ymax = math.bounds(glyph)
        advance = math.glyphs[glyph].width
        name = "sqrtMain" if i == 0 else f"sqrtSize{i}"
        path = (glyph_path(glyph, pad + ymax) +
                f"M{advance} ${{hLinePad}}v${{{rule} + extraVinculum}}h400000v-${{{rule} + extraVinculum}}z")
        body = "\n".join(
            [f"const {name} = function(extraVinculum: number, hLinePad: number): string {{"]
            + comment(f"{name} path geometry is from glyph {glyph} in Libertinus Math.")
            + path_lines(path, "    return `") + ["};", ""])
        metrics = {"height": (ymax - ymin) / u, "advance": advance / u, "minWidth": (xmax + 20) / u}
        if i == 0:
            text = replace_function(text, name, body)
            table["main"] = metrics
        else:
            sizes.append(body)
            table.setdefault("sizes", []).append(metrics)
    while match := re.search(r"^const sqrtSize\d+ = function\(", text, re.M):
        text = text[:match.start()] + text[text.index("\n};\n", match.start()) + 5:]
    anchor = text.index("// The radical sizes, smallest first")
    text = text[:anchor] + "\n".join(sizes) + "\n" + text[anchor:]
    names = ", ".join(f"sqrtSize{i}" for i in range(1, len(sizes) + 1))
    text, n = re.subn(r"^const sqrtSizes = \[[^\]]*\];", f"const sqrtSizes = [{names}];", text, flags=re.M)
    if n != 1:
        raise ValueError("sqrtSizes not found in svgGeometry.ts")

    bottom, extender, top, overlap = radical_assembly()
    _, bottom_min, _, bottom_max = math.bounds(bottom)
    ext_min, _, ext_max, _ = math.bounds(extender)
    _, top_min, top_xmax, top_max = math.bounds(top)
    # The assembly sets its radicand 0.113em from a vertical stem, close
    # beside the pre-drawn radicals, whose leaning stem leaves the radicand
    # more room the lower it goes. The assembled radical gets the gap the
    # largest pre-drawn one has a quarter of the way up.
    largest = variants[-1]
    _, low, _, high = math.bounds(largest)
    stem = max(right for _, right in crossings(largest, y=low + (high - low) / 4))
    advance = ext_max + math.glyphs[largest].width - stem
    top_part = glyph_path(top, pad + top_max)
    bottom_part = glyph_path(bottom, 0, top_expr=f"viewBoxHeight - {fmt(-bottom_min)}" if bottom_min < 0 else f"viewBoxHeight + {fmt(bottom_min)}")
    stem_top = pad + top_max - top_min - overlap
    stem_bottom = bottom_max - bottom_min - overlap
    path = (top_part + bottom_part +
            f"M{fmt(ext_min)} {fmt(stem_top)}V${{viewBoxHeight - {fmt(stem_bottom)}}}"
            f"H{fmt(ext_max)}V{fmt(stem_top)}z"
            f"M{fmt(ext_min)} ${{hLinePad}}v${{{rule} + extraVinculum}}h400000v-${{{rule} + extraVinculum}}z")
    body = "\n".join(
        ["const sqrtTall = function(", "    extraVinculum: number,", "    hLinePad: number,",
         "    viewBoxHeight: number", "): string {"]
        + comment(f"sqrtTall is assembled from {bottom}, {extender} and {top} in Libertinus Math:"
                  " the bottom piece at the bottom of the box, the top piece at the top and a straight"
                  " stem between them.")
        + path_lines(path, "    return `") + ["};", ""])
    text = replace_function(text, "sqrtTall", body)
    table["tall"] = {"advance": advance / u, "minWidth": (max(top_xmax, advance) + 20) / u}
    geometry.write_text(text)

    def entry(values):
        return "{" + ", ".join(f"{k}: {js_number(v)}" for k, v in values.items()) + "}"

    lines = ["// This file is GENERATED by libertinus/build.py. DO NOT MODIFY.",
             "// Radical sizes, in em: the surd's height from vinculum top to bottom,",
             "// its advance width (where the radicand starts) and the minimum width",
             "// that keeps the whole surd visible.",
             "export type RadicalSize = {height: number, advance: number, minWidth: number};",
             "",
             "const radicalMetrics: {",
             "    main: RadicalSize,",
             "    sizes: RadicalSize[],",
             "    tall: {advance: number, minWidth: number},",
             "} = {",
             f"    main: {entry(table['main'])},",
             "    sizes: ["]
    lines += [f"        {entry(size)}," for size in table["sizes"]]
    lines += ["    ],", f"    tall: {entry(table['tall'])},", "};", "", "export default radicalMetrics;"]
    if any(len(line) > MAX_LINE for line in lines):
        raise ValueError("radicalMetrics.ts line too long")
    (KATEX / "src/radicalMetrics.ts").write_text("\n".join(lines) + "\n")

    scss = KATEX / "src/styles/katex.scss"
    text = scss.read_text()
    before = js_number(math.constants["RadicalKernBeforeDegree"] / u)
    after = js_number(math.constants["RadicalKernAfterDegree"] / u)
    def block(m):
        return (f"> .{m.group(1)} {{\n"
                "            /* RadicalKernBeforeDegree and RadicalKernAfterDegree,\n"
                "             written by libertinus/build.py. */\n"
                f"            margin-left: {before}em;\n"
                f"            margin-right: {after}em;\n"
                "        }")
    text, n = re.subn(r"> \.((?:katex-)?root) \{[^}]*\}", block, text)
    if n != 1:
        raise ValueError("root index margins not found in katex.scss")
    scss.write_text(text)


MAX_LINE = 84


def wrap(items, sep, indent, first_indent, width=MAX_LINE):
    lines = []
    current = ""
    prefix = " " * first_indent
    for item in items:
        candidate = current + sep + item if current else item
        if current and len(prefix) + len(candidate) > width:
            lines.append(prefix + current)
            prefix = " " * indent
            current = item
        else:
            current = candidate
    lines.append(prefix + current)
    return lines


def comment(text, indent=4):
    return [" " * indent + "// " + line for line in wrap(text.split(), " ", 0, 0, MAX_LINE - indent - 3)]


def path_lines(path, lead, end="`;"):
    segments = re.findall(r"[MmLlCcHhVvZz](?:\$\{[^}]*\}|[^MmLlCcHhVvZz$])*", path)
    if "".join(segments) != path:
        raise ValueError("could not split path")
    lines = wrap(segments, "", 0, len(lead))
    lines[0] = lead + lines[0][len(lead):]
    if len(lines[-1]) + len(end) > MAX_LINE:
        last = segments[-1]
        lines[-1] = lines[-1][:-len(last)]
        lines.append(last)
    lines[-1] += end
    return lines


def js_number(x):
    x = round(x, 5)
    return "0" if x == 0 else repr(int(x)) if x == int(x) else repr(x)


def write_metrics_data(metrics):
    lines = ["// This file is GENERATED by libertinus/build.py. DO NOT MODIFY.", "export default {"]
    for font in sorted(metrics):
        lines.append(f'    "{font}": {{')
        for cp in sorted(metrics[font], key=int):
            values = ", ".join(js_number(v) for v in metrics[font][cp])
            lines.append(f'        "{cp}": [{values}],')
        lines.append("    },")
    lines.append("};")
    (KATEX / "src/fontMetricsData.js").write_text("\n".join(lines) + "\n")


def write_sigmas(sigmas):
    path = KATEX / "src/fontMetrics.ts"
    text = path.read_text()
    for key, value in sigmas.items():
        v = js_number(value)
        text, n = re.subn(rf"^(\s+{key}: )\[[^\]]*\]", rf"\g<1>[{v}, {v}, {v}]", text, flags=re.M)
        if n != 1:
            raise ValueError(f"sigma {key} not found in fontMetrics.ts")
    path.write_text(text)


def write_size_style_map(rows):
    path = KATEX / "src/Options.ts"
    text = path.read_text()
    start = text.index("const sizeStyleMap = [")
    end = text.index("];", start)
    body = text[start:end]
    for i, row in enumerate(rows):
        pts = ", ".join(f"{10 * SIZE_MULTIPLIERS[s - 1]:g}" for s in row)
        body, n = re.subn(rf"^    \[{i + 1}, \d+, \d+\],(\s*)// size{i + 1}: \[[^\]]*\]",
                          lambda m: f"    [{row[0]}, {row[1]}, {row[2]}],{m.group(1)}// size{i + 1}: [{pts}]",
                          body, flags=re.M)
        if n != 1:
            raise ValueError(f"sizeStyleMap row {i + 1} not found in Options.ts")
    path.write_text(text[:start] + body + text[end:])


def unicode_range(mapping):
    cps = sorted(mapping)
    ranges = []
    start = prev = cps[0]
    for cp in cps[1:] + [None]:
        if cp is not None and cp == prev + 1:
            prev = cp
            continue
        ranges.append(f"U+{start:X}" if start == prev else f"U+{start:X}-{prev:X}")
        if cp is not None:
            start = prev = cp
    return ", ".join(ranges)


def global_metrics():
    c = {k: v / math.upm for k, v in math.constants.items() if isinstance(v, (int, float))}
    x_height = math.font["OS/2"].sxHeight / math.upm
    values = {
        "xHeight": x_height,
        "quad": 1.0,
        "num1": c["FractionNumeratorDisplayStyleShiftUp"],
        "num2": c["FractionNumeratorShiftUp"],
        "num3": c["StackTopShiftUp"],
        "denom1": c["FractionDenominatorDisplayStyleShiftDown"],
        "denom2": c["FractionDenominatorShiftDown"],
        "sup1": c["SuperscriptShiftUp"],
        "sup2": c["SuperscriptShiftUp"],
        "sup3": c["SuperscriptShiftUpCramped"],
        "sub1": c["SubscriptShiftDown"],
        "sub2": c["SubscriptShiftDown"],
        "supDrop": c["SuperscriptBaselineDropMax"],
        "subDrop": c["SubscriptBaselineDropMin"],
        "axisHeight": c["AxisHeight"],
        "defaultRuleThickness": c["FractionRuleThickness"],
        "bigOpSpacing1": c["UpperLimitGapMin"],
        "bigOpSpacing2": c["LowerLimitGapMin"],
        "bigOpSpacing3": c["UpperLimitBaselineRiseMin"],
        "bigOpSpacing4": c["LowerLimitBaselineDropMin"],
        "sqrtRuleThickness": c["RadicalRuleThickness"],
    }
    return {k: round(v, 5) for k, v in values.items()}


SIZE_MULTIPLIERS = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.44, 1.728, 2.074, 2.488]


def size_style_map():
    script = math.constants["ScriptPercentScaleDown"] / 100
    scriptscript = math.constants["ScriptScriptPercentScaleDown"] / 100

    def nearest(target, limit):
        return 1 + min(range(limit), key=lambda i: abs(SIZE_MULTIPLIERS[i] - target))

    rows = []
    for i, m in enumerate(SIZE_MULTIPLIERS):
        rows.append([i + 1, nearest(m * script, i + 1), nearest(m * scriptscript, i + 1)])
    return rows


if __name__ == "__main__":
    main()
