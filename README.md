# KaTeX in Libertinus

[KaTeX](https://katex.org), the fast math typesetting library for the
web, set in the [Libertinus](https://github.com/alerque/libertinus) fonts
instead of Computer Modern. Its glyphs, per-glyph metrics and font-wide
parameters all come from Libertinus Math and its companion text fonts,
including the font's own sizes of delimiters, radicals and wide accents.
Otherwise it is KaTeX: the same API, options, supported functions and
extensions.

What differs from Libertinus and from KaTeX, which symbols Libertinus
lacks, and how the fonts are rebuilt is described in
[`libertinus/README.md`](libertinus/README.md).

## Install

Install it under KaTeX's name, so that code and extensions that import
`katex` use it:

```sh
npm install katex@npm:@frangio/katex-libertinus
```

Each release can stand in for the KaTeX release it is based on: see
[Versioning](libertinus/README.md#versioning). It replaces KaTeX on a
page and cannot be used alongside it.

## Starter template

```html
<!DOCTYPE html>
<!-- KaTeX requires the use of the HTML5 doctype. Without it, KaTeX may not render properly -->
<html>
  <head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@frangio/katex-libertinus@0.19.0/dist/katex.min.css" integrity="sha384-4ylBr26Cb4OalJmPaRvHYRGNOtPRU/GuU+CbuT86lhMIvXti2FoNTKi5RpZ5KOaj" crossorigin="anonymous">

    <!-- The loading of KaTeX is deferred to speed up page rendering -->
    <script defer src="https://cdn.jsdelivr.net/npm/@frangio/katex-libertinus@0.19.0/dist/katex.min.js" integrity="sha384-yo65JxJ0W4Rw8IA1FTZw4T6ByrgcPa7V5LFpC2LIQ40utgFdDKACOLb1bH1xk5HJ" crossorigin="anonymous"></script>

    <!-- To automatically render math in text elements, include the auto-render extension: -->
    <script defer src="https://cdn.jsdelivr.net/npm/@frangio/katex-libertinus@0.19.0/dist/contrib/auto-render.min.js" integrity="sha384-bjyGPfbij8/NDKJhSGZNP/khQVgtHUE5exjm4Ydllo42FwIgYsdLO2lXGmRBf5Mz" crossorigin="anonymous"
        onload="renderMathInElement(document.body);"></script>
  </head>
  ...
</html>
```

## Documentation

KaTeX's documentation applies: the [API](https://katex.org/docs/api.html),
[options](https://katex.org/docs/options.html),
[error handling](https://katex.org/docs/error.html),
[auto-render](https://katex.org/docs/autorender.html) and the
[supported functions](https://katex.org/docs/supported.html), except for
the symbols Libertinus has no glyph for, listed in
[`libertinus/README.md`](libertinus/README.md#not-available).

## License

KaTeX is by Khan Academy and [its contributors](https://github.com/KaTeX/KaTeX/graphs/contributors),
under the MIT License, which also covers this fork's changes
([`LICENSE`](LICENSE)). The fonts are modified Libertinus fonts, by the
Libertinus Project Authors, under the SIL Open Font License 1.1
([`fonts/OFL.txt`](fonts/OFL.txt)), as are the SVG paths drawn from them.
