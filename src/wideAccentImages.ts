export type WideAccentImage = [string, number, number, number];

// Images for \widehat, \widecheck, \widetilde and \utilde. Each list is
// indexed by the number of characters under the accent, the last entry
// covering anything longer. An entry is [path name, viewBox width,
// viewBox height, height in em]; the image is stretched to the width of
// its base.
const widehat: WideAccentImage[] = [
    ["widehat1", 1062, 239, 0.24],
    ["widehat1", 1062, 239, 0.24],
    ["widehat2", 2364, 300, 0.3],
    ["widehat2", 2364, 300, 0.3],
    ["widehat3", 2364, 360, 0.3],
    ["widehat3", 2364, 360, 0.3],
    ["widehat4", 2364, 420, 0.42],
];

const widecheck: WideAccentImage[] = widehat.map(
    ([name, ...rest]) => [name.replace("widehat", "widecheck"), ...rest]);

const tilde: WideAccentImage[] = [
    ["tilde1", 600, 260, 0.26],
    ["tilde1", 600, 260, 0.26],
    ["tilde2", 1033, 286, 0.286],
    ["tilde2", 1033, 286, 0.286],
    ["tilde3", 2339, 306, 0.3],
    ["tilde3", 2339, 306, 0.3],
    ["tilde4", 2340, 312, 0.34],
];

const wideAccentImages: Record<string, WideAccentImage[]> =
    {widehat, widecheck, widetilde: tilde, utilde: tilde};

export default wideAccentImages;
