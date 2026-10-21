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
from fontTools.ttLib import TTFont

LIB = Path(sys.argv[1])
REPORT = Path(sys.argv[2]) if len(sys.argv) > 2 else None
KATEX = Path(__file__).resolve().parent.parent

SOURCES = {
    "math": "LibertinusMath-Regular.otf",
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


def glyph_path(glyph, top, top_expr=None):
    pen = FlippedPath(math.glyphs, top, top_expr=top_expr)
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
    "AMS-Regular": [alphabet("doublestruck", extra={ord("k"): 0x1D55C}), identity("math")],
    "Caligraphic-Regular": [alphabet("script"), identity("math")],
    "Fraktur-Regular": [alphabet("fraktur"), identity("serif")],
    "Main-Regular": [accents("math", {0x2032: "minute.ssty1"}), identity("math"), identity("serif")],
    "Main-Bold": [accents("serif-bold"), alphabet("bold"), identity("serif-bold"), identity("math")],
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


def write_subset(source, mapping, reference, path, advances):
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
    radicals = {}
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
        if file in RADICAL_SLOTS and chosen.get(0x221A, (None,))[0] == "math":
            radicals[RADICAL_SLOTS[file]] = chosen[0x221A][1]
        by_source = {}
        for cp, (key, glyph) in chosen.items():
            by_source.setdefault(key, {})[cp] = glyph
            if file == metric_font:
                metrics[metric_font][str(cp)] = sources[key].metrics(
                    glyph, metric_font in ITALIC_FONTS, operators, metric_font in SKEWED_FONTS)
        for key, mapping in by_source.items():
            name = f"Libertinus_{file}_{key}.woff2"
            source = sources[key]
            advances = {g: source.operator_advance(g) for g in mapping.values() if operators and g in source.italic}
            write_subset(source, mapping, reference, KATEX / "fonts" / name, advances)
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
    write_radicals(radicals)
    if REPORT:
        REPORT.write_text(json.dumps(
            {"fonts": report, "sigmas": sigmas, "sizeStyleMap": size_style_map(), "optical": optical},
            indent=1, ensure_ascii=False))


def face(family, weight, style, file, urange):
    return "\n".join([
        "@font-face {",
        f"    font-family: KaTeX_{family};",
        f'    src: url("#{{$font-folder}}/{file}") format("woff2");',
        f"    font-weight: {weight};",
        f"    font-style: {style};",
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
        + "\n\n".join(faces) + "\n")
    katex_scss = KATEX / "src/styles/katex.scss"
    text = katex_scss.read_text()
    if '@import "./libertinus.scss";' not in text:
        text = text.replace('@import "./fonts.scss";\n', '@import "./fonts.scss";\n@import "./libertinus.scss";\n', 1)
        katex_scss.write_text(text)


EXTENDERS = {0x239C, 0x239F, 0x23A2, 0x23A5, 0x23AA, 0x23D0, 0x2016, 0x2223, 0x2225}


def write_optical_margins(optical):
    lines = ["// This file is GENERATED by libertinus/build.py. DO NOT MODIFY.",
             "// Extra space on the content side of large braces, in em, so their",
             "// mean distance to the content matches a parenthesis of the same",
             "// size.",
             "export default {"]
    for cp, (side, names) in OPTICAL.items():
        sizes = optical[chr(cp)]
        sizes["stack"] = sizes["size4"]
        values = [f'side: "{side}"'] + [f"{k}: {js_number(v)}" for k, v in sorted(sizes.items())]
        for name in names:
            lines.append(f"    {json.dumps(name)}: {{")
            lines += wrap([v + "," for v in values], " ", 8, 8)
            lines.append("    },")
    lines.append("};")
    (KATEX / "src/opticalMargins.js").write_text("\n".join(lines) + "\n")


def write_inner_paths(extenders):
    path = KATEX / "src/svgGeometry.js"
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


RADICAL_SLOTS = {"Main-Regular": "main", "Size1-Regular": "size1", "Size2-Regular": "size2",
                 "Size3-Regular": "size3", "Size4-Regular": "size4"}
RADICAL_FUNCTIONS = {"main": "sqrtMain", "size1": "sqrtSize1", "size2": "sqrtSize2",
                     "size3": "sqrtSize3", "size4": "sqrtSize4"}


def radical_assembly():
    variants = math.font["MATH"].table.MathVariants
    index = variants.VertGlyphCoverage.glyphs.index(math.cmap[0x221A])
    parts = variants.VertGlyphConstruction[index].GlyphAssembly.PartRecords
    bottom, extender, top = (p.glyph for p in parts)
    if [p.PartFlags for p in parts] != [0, 1, 0]:
        raise ValueError("unexpected radical assembly")
    return bottom, extender, top, variants.MinConnectorOverlap


def write_radicals(radicals):
    geometry = KATEX / "src/svgGeometry.js"
    text = geometry.read_text()
    pad = int(re.search(r"^const hLinePad = (\d+);", text, re.M).group(1))
    rule = math.constants["RadicalRuleThickness"]
    u = math.upm
    table = {}

    def replace_function(text, name, body):
        start = text.index(f"const {name} = function(")
        end = text.index("\n};\n", start) + 4
        return text[:start] + body + text[end:]

    for slot, glyph in radicals.items():
        xmin, ymin, xmax, ymax = math.bounds(glyph)
        advance = math.glyphs[glyph].width
        name = RADICAL_FUNCTIONS[slot]
        path = (glyph_path(glyph, pad + ymax) +
                f"M{advance} ${{hLinePad}}v${{{rule} + extraVinculum}}h400000v-${{{rule} + extraVinculum}}z")
        body = "\n".join(
            [f"const {name} = function(extraVinculum: number, hLinePad: number): string {{"]
            + comment(f"{name} path geometry is from glyph {glyph} in Libertinus Math.")
            + path_lines(path, "    return `") + ["};", ""])
        text = replace_function(text, name, body)
        table[slot] = {"height": (ymax - ymin) / u, "advance": advance / u, "minWidth": (xmax + 20) / u}

    bottom, extender, top, overlap = radical_assembly()
    _, bottom_min, _, bottom_max = math.bounds(bottom)
    ext_min, _, ext_max, _ = math.bounds(extender)
    _, top_min, top_xmax, top_max = math.bounds(top)
    advance = math.glyphs[top].width
    top_part = glyph_path(top, pad + top_max)
    bottom_part = glyph_path(bottom, 0, top_expr=f"viewBoxHeight - {fmt(-bottom_min)}" if bottom_min < 0 else f"viewBoxHeight + {fmt(bottom_min)}")
    stem_top = pad + top_max - top_min - overlap
    stem_bottom = bottom_max - bottom_min - overlap
    path = (top_part + bottom_part +
            f"M{fmt(ext_min)} {fmt(stem_top)}V${{viewBoxHeight - {fmt(stem_bottom)}}}"
            f"H{fmt(ext_max)}V{fmt(stem_top)}z"
            f"M{advance} ${{hLinePad}}v${{{rule} + extraVinculum}}h400000v-${{{rule} + extraVinculum}}z")
    body = "\n".join(
        ["const sqrtTall = function(", "    extraVinculum: number,", "    hLinePad: number,",
         "    viewBoxHeight: number", "): string {"]
        + comment(f"sqrtTall is assembled from {bottom}, {extender} and {top} in Libertinus Math:"
                  " the bottom piece at the bottom of the box, the top piece at the top and a straight"
                  " stem between them.")
        + path_lines(path, "    return `") + ["};", ""])
    text = replace_function(text, "sqrtTall", body)
    table["tall"] = {"advance": advance / u, "minWidth": (top_xmax + 20) / u}
    geometry.write_text(text)

    lines = ["// This file is GENERATED by libertinus/build.py. DO NOT MODIFY.",
             "// Radical sizes, in em: the surd's height from vinculum top to bottom,",
             "// its advance width (where the radicand starts) and the minimum width",
             "// that keeps the whole surd visible.",
             "export default {"]
    for slot, values in table.items():
        items = [f"{k}: {js_number(v)}" for k, v in values.items()]
        lines.append(f"    {slot}: {{" + ", ".join(items) + "},")
        if len(lines[-1]) > MAX_LINE:
            raise ValueError("radicalMetrics.js line too long")
    lines.append("};")
    (KATEX / "src/radicalMetrics.js").write_text("\n".join(lines) + "\n")

    scss = KATEX / "src/styles/katex.scss"
    text = scss.read_text()
    before = js_number(math.constants["RadicalKernBeforeDegree"] / u)
    after = js_number(math.constants["RadicalKernAfterDegree"] / u)
    block = ("> .root {\n"
             "            /* RadicalKernBeforeDegree and RadicalKernAfterDegree,\n"
             "             written by libertinus/build.py. */\n"
             f"            margin-left: {before}em;\n"
             f"            margin-right: {after}em;\n"
             "        }")
    text, n = re.subn(r"> \.root \{[^}]*\}", lambda m: block, text)
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


def path_lines(path, lead):
    segments = re.findall(r"[MmLlCcHhVvZz](?:\$\{[^}]*\}|[^MmLlCcHhVvZz$])*", path)
    if "".join(segments) != path:
        raise ValueError("could not split path")
    lines = wrap(segments, "", 0, len(lead))
    lines[0] = lead + lines[0][len(lead):]
    if len(lines[-1]) + 2 > MAX_LINE:
        last = segments[-1]
        lines[-1] = lines[-1][:-len(last)]
        lines.append(last)
    lines[-1] += "`;"
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
    path = KATEX / "src/fontMetrics.js"
    text = path.read_text()
    for key, value in sigmas.items():
        v = js_number(value)
        text, n = re.subn(rf"^(\s+{key}: )\[[^\]]*\]", rf"\g<1>[{v}, {v}, {v}]", text, flags=re.M)
        if n != 1:
            raise ValueError(f"sigma {key} not found in fontMetrics.js")
    path.write_text(text)


def write_size_style_map(rows):
    path = KATEX / "src/Options.js"
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
            raise ValueError(f"sizeStyleMap row {i + 1} not found in Options.js")
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
