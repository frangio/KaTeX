import defineFunction from "../defineFunction";
import {makeLineSpan, makeSpan, makeVList} from "../buildCommon";
import {MathNode, TextNode} from "../mathMLTree";

import * as html from "../buildHTML";
import * as mml from "../buildMathML";

defineFunction({
    type: "overline",
    names: ["\\overline"],
    numArgs: 1,

    handler({parser}, args) {
        const body = args[0];
        return {
            type: "overline",
            mode: parser.mode,
            body,
        };
    },

    htmlBuilder(group, options) {
        // Overlines are handled in the TeXbook pg 443, Rule 9.

        // Build the inner group in the cramped style.
        const innerGroup = html.buildGroup(group.body,
            options.havingCrampedStyle());

        // Create the line above the body
        const metrics = options.fontMetrics();
        const line = makeLineSpan("overline-line", options, metrics.overbarRuleThickness);

        // Generate the vlist, with the appropriate kerns
        const vlist = makeVList({
            positionType: "firstBaseline",
            children: [
                {type: "elem", elem: innerGroup},
                {type: "kern", size: metrics.overbarVerticalGap},
                {type: "elem", elem: line},
                {type: "kern", size: metrics.overbarExtraAscender},
            ],
        }, options);

        return makeSpan(["mord", "katex-overline"], [vlist], options);
    },
    mathmlBuilder(group, options) {
        const operator = new MathNode(
            "mo", [new TextNode("\u203e")]);
        operator.setAttribute("stretchy", "true");

        const node = new MathNode(
            "mover",
            [mml.buildGroup(group.body, options), operator]);
        node.setAttribute("accent", "true");

        return node;
    },
});
