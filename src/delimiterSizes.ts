// The fonts a delimiter is drawn in when it is larger than its text size,
// smallest first, with the CSS class that selects each. \left and \right
// take the first one in which the delimiter is tall enough; \big, \Big,
// \bigg and \Bigg always use the Size1 to Size4 fonts.
import type {FontName} from "./types/fonts";

export type DelimiterFont = {font: FontName, className: string};

const delimiterSizes: DelimiterFont[] = [
    {font: "Size1-Regular", className: "size1"},
    {font: "Size2-Regular", className: "size2"},
    {font: "Size3-Regular", className: "size3"},
    {font: "Size4-Regular", className: "size4"},
];

export default delimiterSizes;
