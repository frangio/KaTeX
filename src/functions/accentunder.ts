// Horizontal overlap functions
import defineFunction from "../defineFunction";
import {makeSpan, makeVList} from "../buildCommon";
import {MathNode} from "../mathMLTree";
import {stretchyMathML, stretchySvg, wideAccentNaturalWidth} from "../stretchy";
import {isCharacterBox} from "../utils";
import {makeEm} from "../units";
import {getBaseSymbol} from "./accent";

import * as html from "../buildHTML";
import * as mml from "../buildMathML";

import type {ParseNode} from "../types/nodes";

defineFunction({
    type: "accentUnder",
    names: [
        "\\underleftarrow", "\\underrightarrow", "\\underleftrightarrow",
        "\\undergroup", "\\underlinesegment", "\\utilde",
    ],
    numArgs: 1,

    handler: ({parser, funcName}, args) => {
        const base = args[0];
        return {
            type: "accentUnder",
            mode: parser.mode,
            label: funcName,
            base: base,
        };
    },

    htmlBuilder: (group: ParseNode<"accentUnder">, options) => {
        // Treat under accents much like underlines.
        const innerGroup = html.buildGroup(group.base, options);

        const baseSymbol = isCharacterBox(group.base)
            ? getBaseSymbol(innerGroup) : undefined;
        const naturalWidth = wideAccentNaturalWidth(group);
        let accentBody;
        let wrapperClasses: string[] = ["svg-align"];
        if (baseSymbol && naturalWidth > baseSymbol.width) {
            // As in accent.ts, an image wider than the character is drawn at
            // its natural size, centered under the character, instead of
            // being squeezed to its width.
            accentBody = stretchySvg(group, options, naturalWidth);
            accentBody.style.marginLeft =
                makeEm((baseSymbol.width - naturalWidth) / 2);
            wrapperClasses = [];
        } else {
            accentBody = stretchySvg(group, options);
        }
        const kern = group.label === "\\utilde" ? 0.12 : 0;

        // Generate the vlist, with the appropriate kerns
        const vlist = makeVList({
            positionType: "top",
            positionData: innerGroup.height,
            children: [
                {type: "elem", elem: accentBody, wrapperClasses},
                {type: "kern", size: kern},
                {type: "elem", elem: innerGroup},
            ],
        }, options);

        return makeSpan(["mord", "accentunder"], [vlist], options);
    },
    mathmlBuilder: (group, options) => {
        const accentNode = stretchyMathML(group.label);
        const node = new MathNode(
            "munder",
            [mml.buildGroup(group.base, options), accentNode]
        );
        node.setAttribute("accentunder", "true");
        return node;
    },
});
