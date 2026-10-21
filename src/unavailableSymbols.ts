// Commands and characters that KaTeX's fonts have no glyph for. Using one is
// a parse error rather than text drawn in whatever font the browser falls
// back to. KaTeX's own fonts have every glyph; a build with other fonts can
// list what they lack.
const unavailableSymbols: string[] = [];
export default unavailableSymbols;
