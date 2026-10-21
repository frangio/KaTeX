// Radical sizes, in em: the surd's height from vinculum top to bottom, its
// advance width (where the radicand starts) and the minimum width that keeps
// the whole surd visible. These match the paths in svgGeometry.ts.
import type {DelimiterSize} from "./types";

export type RadicalSize = {height: number, advance: number, minWidth: number};

const radicalMetrics: {
    main: RadicalSize,
    sizes: Record<DelimiterSize, RadicalSize>,
    tall: {advance: number, minWidth: number},
} = {
    main: {height: 1, advance: 0.833, minWidth: 0.853},
    sizes: {
        1: {height: 1.2, advance: 1, minWidth: 1.02},
        2: {height: 1.8, advance: 1, minWidth: 1.02},
        3: {height: 2.4, advance: 1, minWidth: 1.02},
        4: {height: 3, advance: 1, minWidth: 1.02},
    },
    tall: {advance: 1.056, minWidth: 0.742},
};

export default radicalMetrics;
