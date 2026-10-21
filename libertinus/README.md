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
| `fonts/Libertinus_*.woff2` | Subsets of Libertinus Math, Serif, Sans and Mono with glyphs remapped to the codepoints KaTeX emits, for example math italic *x* (U+1D465) at `x` and each delimiter size at its plain codepoint in the Size fonts. Big operators have their advance reduced by their italic correction, converting OpenType's convention to TeX's. |
| `src/styles/libertinus.scss` | `@font-face` rules for those subsets under KaTeX's family names, with `unicode-range`. Imported after `fonts.scss`, so KaTeX's own fonts only supply characters Libertinus lacks. |
| `src/fontMetricsData.js` | Height, depth, italic correction, skew and width of every glyph, from the outlines and the MATH table. |
| `src/fontMetrics.ts` | Font-wide parameters (`sigmasAndXis`) from the MATH constants. |
| `src/Options.ts` | Script and scriptscript sizes from `ScriptPercentScaleDown` and `ScriptScriptPercentScaleDown`. |
| `src/opticalMargins.ts` | Extra space on the content side of large braces. Libertinus's brace curls inward and keeps its stem close to the content, so it leaves 0.06–0.07em less white space than the parenthesis of the same size; this is that difference, measured from the outlines. |
| `src/radicalMetrics.ts` | Height, advance and minimum width of each radical size. |
| `src/svgGeometry.ts` | Radical paths from Libertinus's radical glyphs and its radical assembly, and the extender bars of assembled delimiters at Libertinus's stem positions. |
| `src/styles/katex.scss` | Root index spacing from `RadicalKernBeforeDegree` and `RadicalKernAfterDegree`. |

## Still from Computer Modern

- Characters no Libertinus font has, such as `\lessapprox`, `\multimap` and
  KaTeX's private-use negated relations, fall back to KaTeX's own fonts.
- Parentheses, brackets and bars taller than the largest pre-drawn size
  (about 3.1em) are KaTeX's single SVG paths. Libertinus's curved, tapering
  shapes don't split into stretchable pieces.
- Stretchy accents and arrows (`\widehat`, `\widetilde`, `\overrightarrow`,
  `\xrightarrow`, `\overbrace`, `\vec`) are KaTeX's SVG paths.
