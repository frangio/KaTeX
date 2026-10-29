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

## Versioning

For each KaTeX release V, this fork releases a version W that satisfies
the npm range `^V`, so it can stand in for that release wherever a
package depends on `katex` with a caret range. While KaTeX is at 0.x,
`^0.Y.Z` allows only 0.Y.Z and later patches of 0.Y, so W keeps V's
major and minor version, and its patch number is the larger of V's and
one more than this fork's previous release in that minor version. The
fork's own fixes are patch releases. For example:

| Release | Version |
|---|---|
| KaTeX 0.19.0 | 0.19.0 |
| A fix in this fork | 0.19.1 |
| KaTeX 0.19.1 | 0.19.2 |
| KaTeX 0.20.0 | 0.20.0 |

The patch numbers of the fork and of KaTeX therefore drift apart, and a
version does not say which KaTeX release it is based on: each release
records that in its notes and in the message of its git tag. Tags are
named `libertinus-vW` so they never collide with KaTeX's own `vV` tags,
which this fork's history contains.
Prereleases can never satisfy `^V`, so versions have no suffixes.

## Releasing

The package is published as `@frangio/katex-libertinus`. For a release
based on a new KaTeX version, first rebase this branch onto that
version's tag, rerun `build.py` and commit its output. Then, with the
version chosen as above:

```sh
pnpm clean-install && pnpm test
npm version 0.19.N --no-git-tag-version   # builds dist/ and the release archives,
                                          # and updates README.md's CDN links and hashes
npm pack --dry-run                        # dist/ with only Libertinus fonts, fonts/OFL.txt, LICENSE
git commit -am "release: libertinus-v0.19.N"
git tag -a libertinus-v0.19.N -m "Based on KaTeX 0.19.Z"
git push origin libertinus libertinus-v0.19.N
npm publish
```

`npm version` runs the `postversion` script, which builds the package
and stamps the version and the integrity hashes of the files just built
into the jsDelivr links in `README.md`. To rebuild those links without
changing the version, run `pnpm dist && node update-sri.js package
README.md`. Upstream's continuous integration publishes with
semantic-release on pushes to `main`; this branch is not `main` and the
repository holds no npm token, so it never runs.

## Licenses

KaTeX's code, and this fork's changes to it, are under the MIT license
(`LICENSE`). The `Libertinus_*` fonts in `fonts/` are modified Libertinus
fonts and, like Libertinus, under the SIL Open Font License 1.1:
`fonts/OFL.txt`, the license file of the Libertinus 7.051 release they
are built from, which `pnpm build` copies to `dist/fonts/OFL.txt` beside
them. The SVG paths that `build.py` draws from Libertinus's outlines, in
`src/svgGeometry.ts`, are under the same license, as a comment there
says; the paths KaTeX adapted from its own fonts remain under theirs, as
`src/stretchy.ts` says. `package.json` declares both licenses,
`MIT AND OFL-1.1`.

The OFL lets modified fonts keep the name Libertinus; its reserved names
are "Linux Libertine", "Biolinum" and "STIX Fonts". Each font keeps its
Libertinus name and copyright, and its version string, such as "Version
7.051;RELEASE", gets "; modified for KaTeX" appended. When rebuilding
from another Libertinus release, replace `fonts/OFL.txt` with that
release's `OFL.txt`.

The stylesheet declares the Libertinus fonts under KaTeX's CSS family
names, such as `KaTeX_Main`, which KaTeX's stylesheet selects. A page
that also loads stock KaTeX's stylesheet gets both sets of fonts under
the same names, and both sets of rules for the same classes, so this
fork replaces KaTeX on a page and cannot be used alongside it.

## What it writes

| File | Contents |
|---|---|
| `fonts/Libertinus_*.woff2` | Subsets of Libertinus Math, Serif, Sans and Mono with glyphs remapped to the codepoints KaTeX emits, for example math italic *x* (U+1D465) at `x` and each delimiter size at its plain codepoint in the Size fonts. Big operators have their advance reduced by their italic correction, converting OpenType's convention to TeX's. Where KaTeX keeps a symbol at a codepoint Libertinus leaves empty, the Libertinus glyph for the same symbol is placed there: the AMS corners `\ulcorner` … `\lrcorner` (KaTeX's box-drawing codepoints) from ⌜ ⌝ ⌞ ⌟, `\triangleright` and `\triangleleft` from ▷ and ◁, `\Finv` from Libertinus Serif, and the slash of `\not` from the combining long solidus U+0338, moved right to sit over the relation that follows it rather than the character before it. The Main fonts also get © and ®, which KaTeX's fonts lack (the regular weight from Libertinus Math, the others from Libertinus Serif), so `\textcopyright` and `\textregistered` use them instead of building them with `\textcircled`. The AMS font gets all 26 lowercase double-struck letters, where KaTeX's has only `k` for `\Bbbk`, so `\mathbb` draws lowercase letters too. |
| `src/unavailableSymbols.ts` | The commands whose glyph is in no Libertinus font and that KaTeX keeps at codepoints no other font draws them at, the characters that stand for them in input, and the macros built on them. KaTeX reports each as a parse error (see below). |
| `src/styles/libertinus.scss` | `@font-face` rules for those subsets under KaTeX's family names, with `unicode-range`. Each subset also covers the zero-width space KaTeX puts in its vertical layouts. |
| `src/styles/fonts.scss` | KaTeX's own `@font-face` rules removed, so the build ships only the Libertinus subsets. |
| `src/fontMetricsData.js` | Height, depth, italic correction, skew and width of every glyph, from the outlines and the MATH table. |
| `src/fontMetrics.ts` | Font-wide parameters (`sigmasAndXis`) from the MATH constants, including the overbar and underbar rules and gaps, the gap between a subscript and a superscript, the gaps of `\atop` and `\binom`, and the root index's raise, which KaTeX otherwise derives from the fraction rule thickness. |
| `src/Options.ts` | Script and scriptscript sizes from `ScriptPercentScaleDown` and `ScriptScriptPercentScaleDown`. |
| `src/delimiterSizes.ts` | The sizes `\left` and `\right` delimiters come in: twelve fonts `KaTeX_Delim1` to `KaTeX_Delim12`, the Nth holding Libertinus's Nth larger size of each delimiter (parentheses, brackets, braces, floors, ceilings, angle brackets and slashes), with their metrics in `fontMetricsData.js` and their classes in `libertinus.scss`. KaTeX's own four sizes stay for `\big` to `\Bigg`. |
| `src/opticalMargins.ts` | Extra space on the content side of large braces. Libertinus's brace curls inward and keeps its stem close to the content, so it leaves 0.06–0.07em less white space than the parenthesis of the same size; this is that difference, measured from the outlines. |
| `src/radicalMetrics.ts` | Height, advance and minimum width of each radical size. |
| `src/svgGeometry.ts` | Radical paths from Libertinus's radical glyphs and its radical assembly; tall parentheses, brackets, floors, ceilings and bars from the pieces of their MATH assemblies, with their widths in `tallDelimWidths`; the extender bars of assembled delimiters at Libertinus's stem positions; and the stretchy paths: arrows, harpoons, two-headed arrows, `\xlongequal`, over and under accent arrows, over and under braces, over and under brackets (`\overbracket`, `\underbracket`), wide accents and `\vec` (see below for the braces). Each stretchy path is the Libertinus glyph or assembly piece at its anchored end, with its straight shaft extended across the box. |
| `src/stretchy.ts` | Box heights of the converted stretchy elements in `katexImagesData`, and over and under arrows switched to Libertinus's accent arrows (U+20D6, U+20D7, U+20E1, U+20EE, U+20EF and the over harpoons). |
| `src/wideAccentImages.ts` | The five Libertinus sizes of `\widehat`, `\widecheck` and `\widetilde`/`\utilde`, chosen by the number of characters under the accent, each in a box whose bottom is the font's `AccentBaseHeight`, all six sizes for single characters, and the flag that draws them at natural size there (see below). |
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
- `\bigcirc` (◯) and `\diamond` (⋄) are not in Libertinus. They are
  its white circle ○ and white diamond ◇ resized and centred on the math
  axis: the circle until its stroke is that of the operators −, ∘ and ⊖
  (1.92 times, 0.90em across, against Computer Modern's 0.93em), the
  diamond to Computer Modern's 0.48em, which leaves its stroke lighter
  than the operators'. `\textcircled` draws its circle with the same ○.
- Tall vertical arrows are built, as in KaTeX, from the arrowhead, a
  shaft taken from ⏐ (single arrows) or ‖ (double arrows), and that glyph
  at the plain end. Libertinus has no ⏐, and its ‖ has its stems 120
  units apart where ⇑ has them 150 apart. In the Size1 font both are
  copies of Libertinus's `|`, which has the arrows' 50-unit stroke, moved
  under the stems of ↑ and ⇑, in glyphs as wide as the arrows.
- `\eqslantless` (⪕) and `\eqslantgtr` (⪖) are not in Libertinus. They are
  drawn as its `\leqslant` (⩽) and `\geqslant` (⩾) turned upside down,
  which is the shape these characters have: the slanted bar above the
  `<` or `>` instead of below it.

## Departures from KaTeX

- KaTeX stretches the image of `\widehat`, `\widecheck`, `\widetilde` and
  `\utilde` to the width of its base, also when that squeezes it over a
  single character: over *x* it draws Computer Modern's smallest image at
  half its width, over *f* at a quarter. Computer Modern's image is flat
  enough that this goes unnoticed; Libertinus's accents keep their shape
  only at their own size. With this build, the accent over or under a
  single character is never stretched: as in TeX, it is the widest of
  Libertinus's six sizes that fits the character, or the narrowest, which
  is the ordinary accent, drawn at its natural size and centred on the
  character. Over *x* that is the same hat as `\hat`. Bases of several
  characters, whose width KaTeX doesn't know, are stretched as in KaTeX.
  The code is in `src/functions/accent.ts`, `src/functions/accentunder.ts`
  and `src/stretchy.ts`, enabled by `naturalSizeOverCharacter` in
  `src/wideAccentImages.ts`.

## Not available

- 36 AMS symbols are in no Libertinus font: `\lessapprox` `\gtrapprox`
  `\lnapprox` `\gnapprox` `\lesseqqgtr` `\gtreqqless` `\precapprox`
  `\succapprox` `\precnapprox` `\succnapprox` `\subseteqq` `\supseteqq`
  `\subsetneqq` `\supsetneqq` `\Subset` `\Supset` `\bumpeq` `\Bumpeq`
  `\pitchfork` `\multimap` `\Cap` `\doublecap` `\Cup` `\doublecup`
  `\intercal` `\veebar` `\barwedge` `\doublebarwedge` `\divideontimes`
  `\leftthreetimes` `\rightthreetimes` `\Game` `\checkmark` `\maltese`
  `\blacklozenge`. KaTeX keeps them at their Unicode codepoints, and the
  stylesheet lists the generic family `math` after the AMS font, so they
  are drawn in the reader's math font (Cambria Math, STIX Two Math and
  the like) with Computer Modern's metrics.
- 16 commands are a parse error ("`\nleqq` is not available: the fonts
  have no glyph for it"), as is typing their character: the 14 negated
  relations KaTeX draws from its private-use glyphs, `\nleqq` `\ngeqq`
  `\nleqslant` `\ngeqslant` `\lvertneqq` `\gvertneqq` `\nsubseteqq`
  `\nsupseteqq` `\varsubsetneq` `\varsupsetneq` `\varsubsetneqq`
  `\varsupsetneqq` `\nshortmid` `\nshortparallel`, and `\diagup` and
  `\diagdown`, which KaTeX keeps at the box-drawing diagonals U+2571 and
  U+2572. No other font has these glyphs at those codepoints. A page that
  defines one with `\renewcommand` gets its own definition.

## Still from Computer Modern

- Stretchy elements Libertinus has no pieces for keep KaTeX's paths:
  `\overgroup`, `\undergroup`, `\overlinesegment`, `\underlinesegment`,
  and the compound arrows `\xrightleftharpoons`, `\xleftrightharpoons`,
  `\xtofrom` and mhchem's `\xrightleftarrows`, `\xrightequilibrium` and
  `\xleftequilibrium`. `\Overrightarrow` uses the full-size Libertinus ⇒,
  since Libertinus has no double accent arrow.
