/**
 * This file provides support to domTree.js and delimiter.js.
 * It's a storehouse of path geometry for SVG images.
 */

// In all paths below, the viewBox-to-em scale is 1000:1.

// Second Brush Stroke
//    Low resolution monitors struggle to display images in fine detail.
//    So browsers apply anti-aliasing. A long straight arrow shaft therefore
//    will sometimes appear as if it has a blurred edge.

//    To mitigate this, these SVG files contain a second "brush-stroke" on the
//    arrow shafts. That is, a second long thin rectangular SVG path has been
//    written directly on top of each arrow shaft. This reinforcement causes
//    some of the screen pixels to display as black instead of the anti-aliased
//    gray pixel that a  single path would generate. So we get arrow shafts
//    whose edges appear to be sharper.
const doubleBrushStroke = (svgPath: string): string => `${svgPath} ${svgPath}`;

const hLinePad = 80;  // padding above a sqrt vinculum. Prevents image cropping.

// The vinculum of a \sqrt can be made thicker by a KaTeX rendering option.
// Think of variable extraVinculum as two detours in the SVG path.
// The detour begins at the lower left of the area labeled extraVinculum below.
// The detour proceeds one extraVinculum distance up and slightly to the right,
// displacing the radiused corner between surd and vinculum. The radius is
// traversed as usual, then the detour resumes. It goes right, to the end of
// the very long vinculum, then down one extraVinculum distance,
// after which it resumes regular path geometry for the radical.
/*                                                  vinculum
                                                   /
         /▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒←extraVinculum
        / █████████████████████←0.04em (40 unit) std vinculum thickness
       / /
      / /
     / /\
    / / surd
*/

const sqrtMain = function(extraVinculum: number, hLinePad: number): string {
    // sqrtMain path geometry is from glyph radical in Libertinus Math.
    return `M564 120L642 120L642 80L529 80L529 86L330 910L148 595
C113 621 76 645 35 666L48 694L112 668L312 1013L350 993zM607 ${hLinePad}
v${40 + extraVinculum}h400000v-${40 + extraVinculum}z`;
};

const sqrtSize1 = function(extraVinculum: number, hLinePad: number): string {
    // sqrtSize1 path geometry is from glyph radical.size1 in Libertinus Math.
    return `M627 120L700 120L700 80L587 80L587 86L383 1202L148 795
C113 821 76 845 35 866L48 894L112 868L370 1313L413 1293zM665 ${hLinePad}
v${40 + extraVinculum}h400000v-${40 + extraVinculum}z`;
};

const sqrtSize2 = function(extraVinculum: number, hLinePad: number): string {
    // sqrtSize2 path geometry is from glyph radical.size2 in Libertinus Math.
    return `M677 120L745 120L745 80L632 80L632 86L427 1644L148 1095
C113 1121 76 1145 35 1166L48 1194L112 1168L415 1763L463 1738zM710 ${hLinePad}
v${40 + extraVinculum}h400000v-${40 + extraVinculum}z`;
};

const sqrtSize3 = function(extraVinculum: number, hLinePad: number): string {
    // sqrtSize3 path geometry is from glyph radical.size4 in Libertinus Math.
    return `M754 120L822 120L822 80L709 80L709 86L502 2430L148 1585
C113 1611 76 1635 35 1656L48 1684L112 1658L492 2563L540 2538zM787 ${hLinePad}
v${40 + extraVinculum}h400000v-${40 + extraVinculum}z`;
};

const sqrtSize4 = function(extraVinculum: number, hLinePad: number): string {
    // sqrtSize4 path geometry is from glyph radical.size5 in Libertinus Math.
    return `M824 120L892 120L892 80L779 80L779 86L571 2872L148 1805
C113 1831 76 1855 35 1876L48 1904L112 1878L562 3013L610 2988zM857 ${hLinePad}
v${40 + extraVinculum}h400000v-${40 + extraVinculum}z`;
};

export const phasePath = function(y: number): string {
    const x = y / 2;  // x coordinate at top of angle
    return `M400000 ${y} H0 L${x} 0 l65 45 L145 ${y - 80} H400000z`;
};

const sqrtTall = function(
    extraVinculum: number,
    hLinePad: number,
    viewBoxHeight: number
): string {
    // sqrtTall is assembled from radical.bt, radical.md and radical.tp in
    // Libertinus Math: the bottom piece at the bottom of the box, the top piece at
    // the top and a straight stem between them.
    return `M659 239L704 239L704 120L852 120L852 80L659 80z
M704 ${viewBoxHeight - 20 - 7}l0 -1658l-45 0l0 1533l-511 -1426c-35 26 -72 50 -113 71
l13 28l64 -26l540 1505zM659 139V${viewBoxHeight - 1585}H704V139zM817 ${hLinePad}
v${40 + extraVinculum}h400000v-${40 + extraVinculum}z`;
};

export const sqrtPath = function(
    size: string,
    extraVinculum: number,
    viewBoxHeight: number
): string {
    extraVinculum = 1000 * extraVinculum; // Convert from document ems to viewBox.
    let path = "";

    switch (size) {
        case "sqrtMain":
            path = sqrtMain(extraVinculum, hLinePad);
            break;
        case "sqrtSize1":
            path = sqrtSize1(extraVinculum, hLinePad);
            break;
        case "sqrtSize2":
            path = sqrtSize2(extraVinculum, hLinePad);
            break;
        case "sqrtSize3":
            path = sqrtSize3(extraVinculum, hLinePad);
            break;
        case "sqrtSize4":
            path = sqrtSize4(extraVinculum, hLinePad);
            break;
        case "sqrtTall":
            path = sqrtTall(extraVinculum, hLinePad, viewBoxHeight);
    }
    return path;
};

export const innerPath = function(name: string, height: number): string {
    // The inner part of stretchy tall delimiters
    switch (name) {
        case "\u239c":
            return doubleBrushStroke(`M51 0 H163 V${height} H51z`);
        case "\u2223":
            return doubleBrushStroke(`M80 0 H130 V${height} H80z`);
        case "\u2225":
            return doubleBrushStroke(`M80 0 H130 V${height} H80z`) +
                doubleBrushStroke(`M260 0 H310 V${height} H260z`);
        case "\u239f":
            return doubleBrushStroke(`M321 0 H433 V${height} H321z`);
        case "\u23a2":
            return doubleBrushStroke(`M135 0 H247 V${height} H135z`);
        case "\u23a5":
            return doubleBrushStroke(`M338 0 H450 V${height} H338z`);
        case "\u23aa":
            return doubleBrushStroke(`M244 0 H356 V${height} H244z`);
        case "\u23d0":
            return doubleBrushStroke(`M312 0 H355 V${height} H312z`);
        case "\u2016":
            return doubleBrushStroke(`M80 0 H130 V${height} H80z`) +
                doubleBrushStroke(`M200 0 H250 V${height} H200z`);
        default:
            return "";
    }
};

export const path: Record<string, string> = {
    // The doubleleftarrow geometry is from glyph U+21D0 in the font KaTeX Main
    doubleleftarrow: `M257 459C246 433 229 404 210 377L803 377
C815 365 815 339 803 327L171 327C151 303 133 284 124 277C133 270 151 251 171 227
L803 227C815 215 815 189 803 177L210 177C229 150 246 121 257 95C251 89 225 89 219 95
C133 192 52 248 3 265C-1 269 -1 285 3 289C52 306 133 362 219 459
C225 465 251 465 257 459zM792 327V377H400000V327zM792 177V227H400000V177z`,

    // doublerightarrow is from glyph U+21D2 in font KaTeX Main
    doublerightarrow: `M399743 95C399754 121 399771 150 399790 177L399197 177
C399185 189 399185 215 399197 227L399829 227C399849 251 399867 270 399876 277
C399867 284 399849 303 399829 327L399197 327C399185 339 399185 365 399197 377
L399790 377C399771 404 399754 433 399743 459C399749 465 399775 465 399781 459
C399867 362 399948 306 399997 289C400001 285 400001 269 399997 265
C399948 248 399867 192 399781 95C399775 89 399749 89 399743 95zM0 327V377H399208V327
zM0 177V227H399208V177z`,

    // leftarrow is from glyph U+2190 in font KaTeX Main
    leftarrow: `M216 104C130 201 49 257 0 274L0 297C108 341 216 469 216 470L256 470
C217 386 176 340 143 313L643 313L643 261L143 261C175 230 224 176 254 104zM623 261
V313H400000V261z`,

    // overbrace is from glyphs U+23A9/23A8/23A7 in font KaTeX_Size4-Regular
    leftbrace: `M431 101.4L293 101.4C108 101.4 7 195.4 0 380.4
C6 386.4 18 386.4 24 380.4C44 296.4 129 181.4 285 181.4L431 181.4zM411 101.4V181.4
H400000V101.4z`,

    leftbraceunder: `M431 283.5L431 203.5L285 203.5C129 203.5 44 88.5 24 4.5
C18 -1.5 6 -1.5 0 4.5C7 189.5 108 283.5 293 283.5zM411 203.5V283.5H400000V203.5z`,

    // overgroup is from the MnSymbol package (public domain)
    leftgroup: `M400000 80
H435C64 80 168.3 229.4 21 260c-5.9 1.2-18 0-18 0-2 0-3-1-3-3v-38C76 61 257 0
 435 0h399565z`,

    leftgroupunder: `M400000 262
H435C64 262 168.3 112.6 21 82c-5.9-1.2-18 0-18 0-2 0-3 1-3 3v38c76 158 257 219
 435 219h399565z`,

    // Harpoons are from glyph U+21BD in font KaTeX Main
    leftharpoon: `M4.5 302L804.5 302C816.5 290 816.5 264 804.5 252L147.5 252
C179.5 221 228.5 167 258.5 95C252.5 89 226.5 89 220.5 95C134.5 192 53.5 248 4.5 265
C-1.5 271 -1.5 296 4.5 302zM793.5 252V302H400000V252z`,

    leftharpoonplus: `M0 267c.7 5.3 3 10 7 14h399993v-40H93c3.3-3.3 10.2-9.5
 20.5-18.5s17.8-15.8 22.5-20.5c50.7-52 88-110.3 112-175 4-11.3 5-18.3 3-21-1.3
-4-7.3-6-18-6-8 0-13 .7-15 2s-4.7 6.7-8 16c-42 98.7-107.3 174.7-196 228-6.7 4.7
-10.7 8-12 10-1.3 2-2 5.7-2 11zm100-26v40h399900v-40zM0 435v40h400000v-40z
m0 0v40h400000v-40z`,

    leftharpoondown: `M4.5 252C-1.5 258 -1.5 283 4.5 289
C53.5 306 134.5 362 220.5 459C226.5 465 252.5 465 258.5 459
C228.5 387 179.5 333 147.5 302L804.5 302C816.5 290 816.5 264 804.5 252zM793.5 252
V302H400000V252z`,

    leftharpoondownplus: `M7 435c-4 4-6.3 8.7-7 14 0 5.3.7 9 2 11s5.3 5.3 12
 10c90.7 54 156 130 196 228 3.3 10.7 6.3 16.3 9 17 2 .7 5 1 9 1h5c10.7 0 16.7
-2 18-6 2-2.7 1-9.7-3-21-32-87.3-82.7-157.7-152-211l-3-3h399907v-40H7zm93 0
v40h399900v-40zM0 241v40h399900v-40zm0 0v40h399900v-40z`,

    // hook is from glyph U+21A9 in font KaTeX Main
    lefthook: `M260 261L158 261C99 262 52 215 52 157C52 99 99 52 157 52L260 52L260 0
L157 0C70 0 0 70 0 157C0 244 70 314 158 313L260 313zM240 261V313H400000V261z`,

    leftlinesegment: doubleBrushStroke(`M40 281 V428 H0 V94 H40 V241 H400000 v40z`),

    leftbracketunder: doubleBrushStroke(`M0 0 h120 V290 H399995 v120 H0z`),

    leftbracketover: doubleBrushStroke(`M0 440 h120 V150 H399995 v-120 H0z`),

    leftmapsto: `M500 313L500 261L50 261L50 104L0 104L0 470L50 470L50 313zM480 261
V313H400000V261z`,

    // tofrom is from glyph U+21C4 in font KaTeX AMS Regular
    leftToFrom: `M0 147h400000v40H0zm0 214c68 40 115.7 95.7 143 167h22c15.3 0 23
-.3 23-1 0-1.3-5.3-13.7-16-37-18-35.3-41.3-69-70-101l-7-8h399905v-40H95l7-8
c28.7-32 52-65.7 70-101 10.7-23.3 16-35.7 16-37 0-.7-7.7-1-23-1h-22C115.7 265.3
 68 321 0 361zm0-174v-40h399900v40zm100 154v40h399900v-40z`,

    longequal: `M0 200V250H400000V200zM0 0V50H400000V0z`,

    midbrace: `M199553.5 181.4L199860.5 181.4
C199949.5 181.4 199978.5 140.4 199997.5 73.4L200001.5 73.4
C200029.5 141.4 200069.5 181.4 200151.5 181.4L200446.5 181.4L200446.5 101.4
L200125.5 101.4C200064.5 101.4 200020.5 80.4 200011.5 6.4
C200003.5 -1.6 199996.5 -2.6 199987.5 6.4
C199980.5 80.4 199926.5 101.4 199876.5 101.4L199553.5 101.4zM0 101.4V181.4H199573.5
V101.4zM200426.5 101.4V181.4H400000V101.4z`,

    midbraceunder: `M199553.5 203.5L199553.5 283.5L199876.5 283.5
C199926.5 283.5 199980.5 304.5 199987.5 378.5
C199996.5 387.5 200003.5 386.5 200011.5 378.5
C200020.5 304.5 200064.5 283.5 200125.5 283.5L200446.5 283.5L200446.5 203.5
L200151.5 203.5C200069.5 203.5 200029.5 243.5 200001.5 311.5L199997.5 311.5
C199978.5 244.5 199949.5 203.5 199860.5 203.5zM0 203.5V283.5H199573.5V203.5z
M200426.5 203.5V283.5H400000V203.5z`,

    oiintSize1: `M512.6 71.6c272.6 0 320.3 106.8 320.3 178.2 0 70.8-47.7 177.6
-320.3 177.6S193.1 320.6 193.1 249.8c0-71.4 46.9-178.2 319.5-178.2z
m368.1 178.2c0-86.4-60.9-215.4-368.1-215.4-306.4 0-367.3 129-367.3 215.4 0 85.8
60.9 214.8 367.3 214.8 307.2 0 368.1-129 368.1-214.8z`,

    oiintSize2: `M757.8 100.1c384.7 0 451.1 137.6 451.1 230 0 91.3-66.4 228.8
-451.1 228.8-386.3 0-452.7-137.5-452.7-228.8 0-92.4 66.4-230 452.7-230z
m502.4 230c0-111.2-82.4-277.2-502.4-277.2s-504 166-504 277.2
c0 110 84 276 504 276s502.4-166 502.4-276z`,

    oiiintSize1: `M681.4 71.6c408.9 0 480.5 106.8 480.5 178.2 0 70.8-71.6 177.6
-480.5 177.6S202.1 320.6 202.1 249.8c0-71.4 70.5-178.2 479.3-178.2z
m525.8 178.2c0-86.4-86.8-215.4-525.7-215.4-437.9 0-524.7 129-524.7 215.4 0
85.8 86.8 214.8 524.7 214.8 438.9 0 525.7-129 525.7-214.8z`,

    oiiintSize2: `M1021.2 53c603.6 0 707.8 165.8 707.8 277.2 0 110-104.2 275.8
-707.8 275.8-606 0-710.2-165.8-710.2-275.8C311 218.8 415.2 53 1021.2 53z
m770.4 277.1c0-131.2-126.4-327.6-770.5-327.6S248.4 198.9 248.4 330.1
c0 130 128.8 326.4 772.7 326.4s770.5-196.4 770.5-326.4z`,

    rightarrow: `M399784 104L399746 104C399776 176 399825 230 399857 261L399357 261
L399357 313L399857 313C399824 340 399783 386 399744 470L399784 470
C399784 469 399892 341 400000 297L400000 274C399951 257 399870 201 399784 104zM0 261
V313H399377V261z`,

    rightbrace: `M399569 101.4L399569 181.4L399715 181.4
C399871 181.4 399956 296.4 399976 380.4C399982 386.4 399994 386.4 400000 380.4
C399993 195.4 399892 101.4 399707 101.4zM0 101.4V181.4H399589V101.4z`,

    rightbraceunder: `M399569 283.5L399707 283.5
C399892 283.5 399993 189.5 400000 4.5C399994 -1.5 399982 -1.5 399976 4.5
C399956 88.5 399871 203.5 399715 203.5L399569 203.5zM0 203.5V283.5H399589V203.5z`,

    rightgroup: `M0 80h399565c371 0 266.7 149.4 414 180 5.9 1.2 18 0 18 0 2 0
 3-1 3-3v-38c-76-158-257-219-435-219H0z`,

    rightgroupunder: `M0 262h399565c371 0 266.7-149.4 414-180 5.9-1.2 18 0 18
 0 2 0 3 1 3 3v38c-76 158-257 219-435 219H0z`,

    rightharpoon: `M399995.5 302C400001.5 296 400001.5 271 399995.5 265
C399946.5 248 399865.5 192 399779.5 95C399773.5 89 399747.5 89 399741.5 95
C399771.5 167 399820.5 221 399852.5 252L399195.5 252
C399183.5 264 399183.5 290 399195.5 302zM0 252V302H399206.5V252z`,

    rightharpoonplus: `M0 241v40h399993c4.7-4.7 7-9.3 7-14 0-9.3-3.7-15.3-11
-18-92.7-56.7-159-133.7-199-231-3.3-9.3-6-14.7-8-16-2-1.3-7-2-15-2-10.7 0-16.7
 2-18 6-2 2.7-1 9.7 3 21 15.3 42 36.7 81.8 64 119.5 27.3 37.7 58 69.2 92 94.5z
m0 0v40h399900v-40z m100 194v40h399900v-40zm0 0v40h399900v-40z`,

    rightharpoondown: `M399995.5 252L399195.5 252
C399183.5 264 399183.5 290 399195.5 302L399852.5 302
C399820.5 333 399771.5 387 399741.5 459C399747.5 465 399773.5 465 399779.5 459
C399865.5 362 399946.5 306 399995.5 289C400001.5 283 400001.5 258 399995.5 252z
M0 252V302H399206.5V252z`,

    rightharpoondownplus: `M399747 705c0 7.3 6.7 11 20 11 8 0 13-.8
 15-2.5s4.7-6.8 8-15.5c40-94 99.3-166.3 178-217 13.3-8 20.3-12.3 21-13 5.3-3.3
 8.5-5.8 9.5-7.5 1-1.7 1.5-5.2 1.5-10.5s-2.3-10.3-7-15H0v40h399908c-34 25.3
-64.7 57-92 95-27.3 38-48.7 77.7-64 119-3.3 8.7-5 14-5 16zM0 435v40h399900v-40z
m0-194v40h400000v-40zm0 0v40h400000v-40z`,

    righthook: `M399740 261L399740 313L399842 313C399930 314 400000 244 400000 157
C400000 70 399930 0 399843 0L399740 0L399740 52L399843 52
C399901 52 399948 99 399948 157C399948 215 399901 262 399842 261zM0 261V313H399760
V261z`,

    rightlinesegment: doubleBrushStroke(`M399960 241 V94 h40 V428 h-40 V281 H0 v-40z`),

    rightbracketunder: doubleBrushStroke(`M399995 0 h-120 V290 H0 v120 H400000z`),

    rightbracketover: doubleBrushStroke(`M399995 440 h-120 V150 H0 v-120 H399995z`),

    rightToFrom: `M400000 167c-70.7-42-118-97.7-142-167h-23c-15.3 0-23 .3-23
 1 0 1.3 5.3 13.7 16 37 18 35.3 41.3 69 70 101l7 8H0v40h399905l-7 8c-28.7 32
-52 65.7-70 101-10.7 23.3-16 35.7-16 37 0 .7 7.7 1 23 1h23c24-69.3 71.3-125 142
-167z M100 147v40h399900v-40zM0 341v40h399900v-40z`,

    // twoheadleftarrow is from glyph U+219E in font KaTeX AMS Regular
    twoheadleftarrow: `M395 459C365 387 347 341 324 302L803 302
C815 290 815 264 803 252L324 252C347 213 365 167 395 95C389 89 363 89 357 95
C329 149 278 221 246 252L146 252C178 221 227 167 257 95C251 89 225 89 219 95
C133 192 52 248 3 265C-1 269 -1 285 3 289C52 306 133 362 219 459
C225 465 251 465 257 459C227 387 178 333 146 302L246 302C278 333 329 405 357 459
C363 465 389 465 395 459zM792 252V302H400000V252z`,

    twoheadrightarrow: `M399605 95C399635 167 399654 213 399676 252L399197 252
C399185 264 399185 290 399197 302L399676 302C399654 341 399635 387 399605 459
C399611 465 399637 465 399643 459C399671 405 399722 333 399754 302L399854 302
C399822 333 399773 387 399743 459C399749 465 399775 465 399781 459
C399867 362 399948 306 399997 289C400001 285 400001 269 399997 265
C399948 248 399867 192 399781 95C399775 89 399749 89 399743 95
C399773 167 399822 221 399854 252L399754 252C399722 221 399671 149 399643 95
C399637 89 399611 89 399605 95zM0 252V302H399208V252z`,

    // tilde1 is a modified version of a glyph from the MnSymbol package
    tilde1: `M548 0C539 63 498 95 444 95C422 95 384 85 333 63C237 22 172 0 138 0
C75 0 0 49 0 156L26 156C37 94 79 63 130 63C151 63 188 73 239 94
C350 140 360 156 431 156C503 156 573 99 573 0z`,

    // ditto tilde2, tilde3, & tilde4
    tilde2: `M976 0C960 62 897 95 795 95C752 95 681 85 584 62C406 22 283 0 220 0
C101 0 20 41 0 156L26 156C46 94 108 62 205 62C244 62 314 74 410 94
C618 139 638 156 770 156C904 156 983 109 1002 0z`,

    tilde3: `M1468 0C1447 68 1360 104 1214 104C1153 104 1007 92 870 68
C613 24 426 0 334 0C163 0 33 46 0 170L26 170C55 102 173 68 311 68
C368 68 480 80 617 102C916 151 988 170 1177 170C1370 170 1468 119 1495 0z`,

    tilde4: `M1901 0C1874 67 1706 99 1549 99C1484 99 1253 88 1107 65
C832 23 546 0 446 0C263 0 36 45 0 167L29 167C63 100 284 67 432 67
C493 67 667 80 815 102C1133 150 1317 167 1520 167C1725 167 1901 118 1931 0z`,

    // vec is from glyph U+20D7 in font KaTeX Main
    vec: `M420 126L420 94C391 84 335 58 283 0L252 0C272 39 316 77 335 90L0 90L0 130
L335 130C316 143 272 181 252 220L283 220C335 162 391 136 420 126z`,

    // widehat1 is a modified version of a glyph from the MnSymbol package
    widehat1: `M573 191L311 0L262 0L0 192L21 218L285 63L552 218z`,

    // ditto widehat2, widehat3, & widehat4
    widehat2: `M1002 191L527 0L478 0L0 192L13 218L501 63L990 218z`,

    widehat3: `M1495 193L773 0L724 0L0 194L8 220L747 63L1489 220z`,

    widehat4: `M1931 193L991 0L942 0L0 194L8 220L965 63L1925 220z`,

    // widecheck paths are all inverted versions of widehat
    widecheck1: `M552 0L285 155L21 0L0 26L262 218L311 218L573 27z`,

    widecheck2: `M990 0L501 155L13 0L0 26L478 218L527 218L1002 27z`,

    widecheck3: `M1489 0L747 157L8 0L0 26L724 220L773 220L1495 27z`,

    widecheck4: `M1925 0L965 157L8 0L0 26L942 220L991 220L1931 27z`,

    // The next ten paths support reaction arrows from the mhchem package.

    // Arrows for \ce{<-->} are offset from xAxis by 0.22ex, per mhchem in LaTeX
    // baraboveleftarrow is mostly from glyph U+2190 in font KaTeX Main
    baraboveleftarrow: `M400000 620h-399890l3 -3c68.7 -52.7 113.7 -120 135 -202
c4 -14.7 6 -23 6 -25c0 -7.3 -7 -11 -21 -11c-8 0 -13.2 0.8 -15.5 2.5
c-2.3 1.7 -4.2 5.8 -5.5 12.5c-1.3 4.7 -2.7 10.3 -4 17c-12 48.7 -34.8 92 -68.5 130
s-74.2 66.3 -121.5 85c-10 4 -16 7.7 -18 11c0 8.7 6 14.3 18 17c47.3 18.7 87.8 47
121.5 85s56.5 81.3 68.5 130c0.7 2 1.3 5 2 9s1.2 6.7 1.5 8c0.3 1.3 1 3.3 2 6
s2.2 4.5 3.5 5.5c1.3 1 3.3 1.8 6 2.5s6 1 10 1c14 0 21 -3.7 21 -11
c0 -2 -2 -10.3 -6 -25c-20 -79.3 -65 -146.7 -135 -202l-3 -3h399890z
M100 620v40h399900v-40z M0 241v40h399900v-40zM0 241v40h399900v-40z`,

    // rightarrowabovebar is mostly from glyph U+2192, KaTeX Main
    rightarrowabovebar: `M0 241v40h399891c-47.3 35.3-84 78-110 128-16.7 32
-27.7 63.7-33 95 0 1.3-.2 2.7-.5 4-.3 1.3-.5 2.3-.5 3 0 7.3 6.7 11 20 11 8 0
13.2-.8 15.5-2.5 2.3-1.7 4.2-5.5 5.5-11.5 2-13.3 5.7-27 11-41 14.7-44.7 39
-84.5 73-119.5s73.7-60.2 119-75.5c6-2 9-5.7 9-11s-3-9-9-11c-45.3-15.3-85-40.5
-119-75.5s-58.3-74.8-73-119.5c-4.7-14-8.3-27.3-11-40-1.3-6.7-3.2-10.8-5.5
-12.5-2.3-1.7-7.5-2.5-15.5-2.5-14 0-21 3.7-21 11 0 2 2 10.3 6 25 20.7 83.3 67
151.7 139 205zm96 379h399894v40H0zm0 0h399904v40H0z`,

    // The short left harpoon has 0.5em (i.e. 500 units) kern on the left end.
    // Ref from mhchem.sty: \rlap{\raisebox{-.22ex}{$\kern0.5em
    baraboveshortleftharpoon: `M507,435c-4,4,-6.3,8.7,-7,14c0,5.3,0.7,9,2,11
c1.3,2,5.3,5.3,12,10c90.7,54,156,130,196,228c3.3,10.7,6.3,16.3,9,17
c2,0.7,5,1,9,1c0,0,5,0,5,0c10.7,0,16.7,-2,18,-6c2,-2.7,1,-9.7,-3,-21
c-32,-87.3,-82.7,-157.7,-152,-211c0,0,-3,-3,-3,-3l399351,0l0,-40
c-398570,0,-399437,0,-399437,0z M593 435 v40 H399500 v-40z
M0 281 v-40 H399908 v40z M0 281 v-40 H399908 v40z`,

    rightharpoonaboveshortbar: `M0,241 l0,40c399126,0,399993,0,399993,0
c4.7,-4.7,7,-9.3,7,-14c0,-9.3,-3.7,-15.3,-11,-18c-92.7,-56.7,-159,-133.7,-199,
-231c-3.3,-9.3,-6,-14.7,-8,-16c-2,-1.3,-7,-2,-15,-2c-10.7,0,-16.7,2,-18,6
c-2,2.7,-1,9.7,3,21c15.3,42,36.7,81.8,64,119.5c27.3,37.7,58,69.2,92,94.5z
M0 241 v40 H399908 v-40z M0 475 v-40 H399500 v40z M0 475 v-40 H399500 v40z`,

    shortbaraboveleftharpoon: `M7,435c-4,4,-6.3,8.7,-7,14c0,5.3,0.7,9,2,11
c1.3,2,5.3,5.3,12,10c90.7,54,156,130,196,228c3.3,10.7,6.3,16.3,9,17c2,0.7,5,1,9,
1c0,0,5,0,5,0c10.7,0,16.7,-2,18,-6c2,-2.7,1,-9.7,-3,-21c-32,-87.3,-82.7,-157.7,
-152,-211c0,0,-3,-3,-3,-3l399907,0l0,-40c-399126,0,-399993,0,-399993,0z
M93 435 v40 H400000 v-40z M500 241 v40 H400000 v-40z M500 241 v40 H400000 v-40z`,

    shortrightharpoonabovebar: `M53,241l0,40c398570,0,399437,0,399437,0
c4.7,-4.7,7,-9.3,7,-14c0,-9.3,-3.7,-15.3,-11,-18c-92.7,-56.7,-159,-133.7,-199,
-231c-3.3,-9.3,-6,-14.7,-8,-16c-2,-1.3,-7,-2,-15,-2c-10.7,0,-16.7,2,-18,6
c-2,2.7,-1,9.7,3,21c15.3,42,36.7,81.8,64,119.5c27.3,37.7,58,69.2,92,94.5z
M500 241 v40 H399408 v-40z M500 435 v40 H400000 v-40z`,
    accentrightarrow: `M400000 126L400000 94C399971 84 399915 58 399863 0L399832 0
C399852 39 399896 77 399915 90L399580 90L399580 130L399915 130
C399896 143 399852 181 399832 220L399863 220C399915 162 399971 136 400000 126zM0 90
V130H399600V90z`,
    accentleftarrow: `M0 126C29 136 85 162 137 220L168 220C148 181 104 143 85 130
L420 130L420 90L85 90C104 77 148 39 168 0L137 0C85 58 29 84 0 94zM400 90V130H400000
V90z`,
    accentrightharpoon: `M400000 130L400000 94C399971 84 399915 58 399863 0L399832 0
C399852 39 399896 77 399915 90L399580 90L399580 130zM0 90V130H399600V90z`,
    accentleftharpoon: `M0 130L420 130L420 90L85 90C104 77 148 39 168 0L137 0
C85 58 29 84 0 94zM400 90V130H400000V90z`,
    underaccentrightarrow: `M400000 298L400000 266C399971 256 399915 230 399863 172
L399832 172C399852 211 399896 249 399915 262L399580 262L399580 302L399915 302
C399896 315 399852 353 399832 392L399863 392C399915 334 399971 308 400000 298zM0 262
V302H399600V262z`,
    underaccentleftarrow: `M0 298C29 308 85 334 137 392L168 392
C148 353 104 315 85 302L420 302L420 262L85 262C104 249 148 211 168 172L137 172
C85 230 29 256 0 266zM400 262V302H400000V262z`,
    widehat5: `M2384 193L1218 0L1169 0L0 194L5 220L1192 63L2378 220z`,
    widecheck5: `M2378 0L1192 157L5 0L0 26L1169 220L1218 220L2384 27z`,
    tilde5: `M2354 0C2326 67 2041 99 1884 99C1818 99 1473 88 1327 65
C1052 23 663 0 564 0C381 0 36 45 0 166L29 166C63 100 402 67 550 67
C611 67 888 79 1035 102C1353 150 1651 166 1855 166C2060 166 2354 117 2384 0z`,
};

export const tallDelim = function(label: string, midHeight: number): string {
    switch (label) {
        case "lbrack":
            return `M403 1759 V84 H666 V0 H319 V1759 v${midHeight} v1759 v84 h347 v-84
H403z M403 1759 V0 H319 V1759 v${midHeight} v1759 v84 h84z`;
        case "rbrack":
            return `M347 1759 V0 H0 V84 H263 V1759 v${midHeight} v1759 H0 v84 H347z
M347 1759 V0 H263 V1759 v${midHeight} v1759 h84z`;
        case "vert":
            return `M145 15 v585 v${midHeight} v585 c2.667,10,9.667,15,21,15
c10,0,16.667,-5,20,-15 v-585 v${-midHeight} v-585 c-2.667,-10,-9.667,-15,-21,-15
c-10,0,-16.667,5,-20,15z M188 15 H145 v585 v${midHeight} v585 h43z`;
        case "doublevert":
            return `M145 15 v585 v${midHeight} v585 c2.667,10,9.667,15,21,15
c10,0,16.667,-5,20,-15 v-585 v${-midHeight} v-585 c-2.667,-10,-9.667,-15,-21,-15
c-10,0,-16.667,5,-20,15z M188 15 H145 v585 v${midHeight} v585 h43z
M367 15 v585 v${midHeight} v585 c2.667,10,9.667,15,21,15
c10,0,16.667,-5,20,-15 v-585 v${-midHeight} v-585 c-2.667,-10,-9.667,-15,-21,-15
c-10,0,-16.667,5,-20,15z M410 15 H367 v585 v${midHeight} v585 h43z`;
        case "lfloor":
            return `M319 602 V0 H403 V602 v${midHeight} v1715 h263 v84 H319z
MM319 602 V0 H403 V602 v${midHeight} v1715 H319z`;
        case "rfloor":
            return `M319 602 V0 H403 V602 v${midHeight} v1799 H0 v-84 H319z
MM319 602 V0 H403 V602 v${midHeight} v1715 H319z`;
        case "lceil":
            return `M403 1759 V84 H666 V0 H319 V1759 v${midHeight} v602 h84z
M403 1759 V0 H319 V1759 v${midHeight} v602 h84z`;
        case "rceil":
            return `M347 1759 V0 H0 V84 H263 V1759 v${midHeight} v602 h84z
M347 1759 V0 h-84 V1759 v${midHeight} v602 h84z`;
        case "lparen":
            return `M863,9c0,-2,-2,-5,-6,-9c0,0,-17,0,-17,0c-12.7,0,-19.3,0.3,-20,1
c-5.3,5.3,-10.3,11,-15,17c-242.7,294.7,-395.3,682,-458,1162c-21.3,163.3,-33.3,349,
-36,557 l0,${midHeight + 84}c0.2,6,0,26,0,60c2,159.3,10,310.7,24,454c53.3,528,210,
949.7,470,1265c4.7,6,9.7,11.7,15,17c0.7,0.7,7,1,19,1c0,0,18,0,18,0c4,-4,6,-7,6,-9
c0,-2.7,-3.3,-8.7,-10,-18c-135.3,-192.7,-235.5,-414.3,-300.5,-665c-65,-250.7,-102.5,
-544.7,-112.5,-882c-2,-104,-3,-167,-3,-189
l0,-${midHeight + 92}c0,-162.7,5.7,-314,17,-454c20.7,-272,63.7,-513,129,-723c65.3,
-210,155.3,-396.3,270,-559c6.7,-9.3,10,-15.3,10,-18z`;
        case "rparen":
            return `M76,0c-16.7,0,-25,3,-25,9c0,2,2,6.3,6,13c21.3,28.7,42.3,60.3,
63,95c96.7,156.7,172.8,332.5,228.5,527.5c55.7,195,92.8,416.5,111.5,664.5
c11.3,139.3,17,290.7,17,454c0,28,1.7,43,3.3,45l0,${midHeight + 9}
c-3,4,-3.3,16.7,-3.3,38c0,162,-5.7,313.7,-17,455c-18.7,248,-55.8,469.3,-111.5,664
c-55.7,194.7,-131.8,370.3,-228.5,527c-20.7,34.7,-41.7,66.3,-63,95c-2,3.3,-4,7,-6,11
c0,7.3,5.7,11,17,11c0,0,11,0,11,0c9.3,0,14.3,-0.3,15,-1c5.3,-5.3,10.3,-11,15,-17
c242.7,-294.7,395.3,-681.7,458,-1161c21.3,-164.7,33.3,-350.7,36,-558
l0,-${midHeight + 144}c-2,-159.3,-10,-310.7,-24,-454c-53.3,-528,-210,-949.7,
-470,-1265c-4.7,-6,-9.7,-11.7,-15,-17c-0.7,-0.7,-6.7,-1,-18,-1z`;
        default:
            // We should not ever get here.
            throw new Error("Unknown stretchy delimiter.");
    }
};
