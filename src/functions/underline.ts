import defineFunction from "../defineFunction";
import {makeLineSpan, makeSpan, makeVList} from "../buildCommon";
import {MathNode, TextNode} from "../mathMLTree";

import * as html from "../buildHTML";
import * as mml from "../buildMathML";

defineFunction({
    type: "underline",
    names: ["\\underline"],
    numArgs: 1,
    allowedInText: true,

    handler({parser}, args) {
        return {
            type: "underline",
            mode: parser.mode,
            body: args[0],
        };
    },

    htmlBuilder(group, options) {
        // Underlines are handled in the TeXbook pg 443, Rule 10.
        // Build the inner group.
        const innerGroup = html.buildGroup(group.body, options);

        // Create the line to go below the body
        const metrics = options.fontMetrics();
        const line = makeLineSpan("underline-line", options, metrics.underbarRuleThickness);

        // Generate the vlist, with the appropriate kerns
        const vlist = makeVList({
            positionType: "top",
            positionData: innerGroup.height,
            children: [
                {type: "kern", size: metrics.underbarExtraDescender},
                {type: "elem", elem: line},
                {type: "kern", size: metrics.underbarVerticalGap},
                {type: "elem", elem: innerGroup},
            ],
        }, options);

        return makeSpan(["mord", "katex-underline"], [vlist], options);
    },
    mathmlBuilder(group, options) {
        const operator = new MathNode(
            "mo", [new TextNode("\u203e")]);
        operator.setAttribute("stretchy", "true");

        const node = new MathNode(
            "munder",
            [mml.buildGroup(group.body, options), operator]);
        node.setAttribute("accentunder", "true");

        return node;
    },
});
