// Extra space, in em, on the content side of large delimiters, per
// pre-drawn size and for assembled (stacked) delimiters. KaTeX's own fonts
// need none.
import type {DelimiterSize} from "./types";

export type OpticalMargin = {
    side: "left" | "right",
    sizes: Partial<Record<DelimiterSize, number>>,
    stack?: number,
};

const opticalMargins: Partial<Record<string, OpticalMargin>> = {};

export default opticalMargins;
