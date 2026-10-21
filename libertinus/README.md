# KaTeX with Libertinus

This branch sets KaTeX in [Libertinus](https://github.com/alerque/libertinus):
its glyphs, its per-glyph metrics and the font-wide parameters from its
OpenType MATH table. `build.py` generates everything font-specific from a
Libertinus release; the code changes it relies on are ordinary commits on
the branch.

## Rebuilding

Requirements: Python 3 with `fonttools` and `brotli`, and the static OTF
files of a Libertinus release (built and checked with 7.051, from
`Libertinus-7.051.tar.zst`, directory `static/OTF/`).

```sh
pip install fonttools brotli
python3 libertinus/build.py path/to/Libertinus-7.051/static/OTF
pnpm build
```

The script can be rerun: it reads KaTeX's original Computer Modern metrics
from `libertinus/katex-metrics.json` (taken from KaTeX 0.19.0, unchanged since 0.16) and
overwrites its own output.

## What it writes

| File | Contents |
|---|---|
| `fonts/Libertinus_*.woff2` | Subsets of Libertinus Math, Serif, Sans and Mono with glyphs remapped to the codepoints KaTeX emits, for example math italic *x* (U+1D465) at `x` and each delimiter size at its plain codepoint in the Size fonts. Big operators have their advance reduced by their italic correction, converting OpenType's convention to TeX's. Where KaTeX keeps a symbol at a codepoint Libertinus leaves empty, the Libertinus glyph for the same symbol is placed there: the AMS corners `\ulcorner` … `\lrcorner` (KaTeX's box-drawing codepoints) from ⌜ ⌝ ⌞ ⌟, `\triangleright` and `\triangleleft` from ▷ and ◁, `\Finv` from Libertinus Serif, and the slash of `\not` from the combining long solidus U+0338, moved right to sit over the relation that follows it rather than the character before it. |
| `src/styles/libertinus.scss` | `@font-face` rules for those subsets under KaTeX's family names, with `unicode-range`. Each subset also covers the zero-width space KaTeX puts in its vertical layouts. |
| `src/styles/fonts.scss` | KaTeX's own `@font-face` rules removed, so the build ships only the Libertinus subsets. |
| `src/fontMetricsData.js` | Height, depth, italic correction, skew and width of every glyph, from the outlines and the MATH table. |
| `src/fontMetrics.ts` | Font-wide parameters (`sigmasAndXis`) from the MATH constants, including the overbar and underbar rules and gaps, the gap between a subscript and a superscript, the gaps of `\atop` and `\binom`, and the root index's raise, which KaTeX otherwise derives from the fraction rule thickness. |
| `src/Options.ts` | Script and scriptscript sizes from `ScriptPercentScaleDown` and `ScriptScriptPercentScaleDown`. |
| `src/opticalMargins.ts` | Extra space on the content side of large braces. Libertinus's brace curls inward and keeps its stem close to the content, so it leaves 0.06–0.07em less white space than the parenthesis of the same size; this is that difference, measured from the outlines. |
| `src/radicalMetrics.ts` | Height, advance and minimum width of each radical size. |
| `src/svgGeometry.ts` | Radical paths from Libertinus's radical glyphs and its radical assembly; tall parentheses, brackets, floors, ceilings and bars from the pieces of their MATH assemblies, with their widths in `tallDelimWidths`; the extender bars of assembled delimiters at Libertinus's stem positions; and the stretchy paths: arrows, harpoons, two-headed arrows, `\xlongequal`, over and under accent arrows, over and under braces, over and under brackets (`\overbracket`, `\underbracket`), wide accents and `\vec` (see below for the braces). Each stretchy path is the Libertinus glyph or assembly piece at its anchored end, with its straight shaft extended across the box. |
| `src/stretchy.ts` | Box heights of the converted stretchy elements in `katexImagesData`, and over and under arrows switched to Libertinus's accent arrows (U+20D6, U+20D7, U+20E1, U+20EE, U+20EF and the over harpoons). |
| `src/wideAccentImages.ts` | The five Libertinus sizes of `\widehat`, `\widecheck` and `\widetilde`/`\utilde`, chosen by the number of characters under the accent, each in a box whose bottom is the font's `AccentBaseHeight`, and the flag that draws them at natural size over a narrower character (see below). |
| `src/buildCommon.ts` | Size of the `\vec` image. |
| `src/styles/katex.scss` | Root index spacing from `RadicalKernBeforeDegree` and `RadicalKernAfterDegree`. |

## Departures from Libertinus

- `\overbrace` and `\underbrace` are drawn from Libertinus's vertical brace
  pieces (U+23A7 to U+23AA) turned 90°, not from its horizontal brace
  (U+23DE, U+23DF). The pieces Libertinus provides for stretching the
  horizontal brace don't match its own pre-drawn horizontal braces: the
  point is a different, narrower drawing and the arms meet it at a
  different height. The vertical pieces are cut from the same drawing as
  the pre-drawn vertical braces, so they stretch consistently, and they
  match the brace used by `cases`. The result is heavier (0.112em stroke
  against 0.080em) and taller (0.488em against 0.385em) than Libertinus's
  horizontal design. Set `HORIZONTAL_BRACE_DESIGN = "horizontal"` in
  `build.py` to use the font's horizontal pieces instead.
- Radicals taller than the largest pre-drawn one (3.8em) are assembled
  from Libertinus's radical pieces, but with the radicand 0.194em from the
  stem instead of the assembly's 0.113em. The pre-drawn radicals have a
  leaning stem that leaves the radicand more room the lower it goes; next
  to them the assembly's vertical stem crowds the radicand. 0.194em is the
  gap the largest pre-drawn radical has a quarter of the way up.
- `\eqslantless` (⪕) and `\eqslantgtr` (⪖) are not in Libertinus. They are
  drawn as its `\leqslant` (⩽) and `\geqslant` (⩾) turned upside down,
  which is the shape these characters have: the slanted bar above the
  `<` or `>` instead of below it.

## Departures from KaTeX

- KaTeX stretches the image of `\widehat`, `\widecheck`, `\widetilde` and
  `\utilde` to the width of its base, also when that squeezes it over a
  single character: over *x* it draws Computer Modern's smallest image at
  half its width, over *f* at a quarter. Computer Modern's image is flat
  enough that this goes unnoticed. Libertinus's smallest wide accent is its
  ordinary accent, which squeezed turns into a narrow spike or vanishes.
  With this build, an image wider than its single-character base keeps its
  natural size and is centred over or under the character, as in TeX,
  which never squeezes an accent and uses the largest size no wider than
  the base. Wider bases are stretched as in KaTeX. The code is in
  `src/functions/accent.ts` and `src/functions/accentunder.ts`, enabled by
  `naturalSizeOverNarrowBase` in `src/wideAccentImages.ts`.

## Not covered by Libertinus

- About 50 characters that KaTeX's fonts have are in no Libertinus font,
  such as `\lessapprox`, `\subseteqq`, `\multimap` and `\checkmark`.
  KaTeX's own fonts are not shipped, so the browser draws them with a font
  installed on the reader's system, spaced with KaTeX's Computer Modern
  metrics. KaTeX's private-use negated relations, such as `\nleqq`, have
  no glyph in any other font.

## Still from Computer Modern

- Stretchy elements Libertinus has no pieces for keep KaTeX's paths:
  `\overgroup`, `\undergroup`, `\overlinesegment`, `\underlinesegment`,
  and the compound arrows `\xrightleftharpoons`, `\xleftrightharpoons`,
  `\xtofrom` and mhchem's `\xrightleftarrows`, `\xrightequilibrium` and
  `\xleftequilibrium`. `\Overrightarrow` uses the full-size Libertinus ⇒,
  since Libertinus has no double accent arrow.
