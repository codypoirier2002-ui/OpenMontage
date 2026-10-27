// THE BLACK-BODY ENGINE (pure, import-free: shared/blackbody.test.ts runs it under `node --experimental-strip-types`).
// The light is the meter: every glow colour in this film is COMPUTED from temperature, never eyeballed
// (art-direction.md; scene_plan.metadata.risks[0]):
//   Planck's law  B(lambda, T) ~ 1 / (lambda^5 (exp(c2 / (lambda T)) - 1)),  c2 = 1.4387769e-2 m K
//   x  the CIE 1931 2-degree colour-matching functions (CMF_5NM below: 380-780 nm at 5 nm, the CIE table as published,
//      copied from colour-science's MSDS_CMFS['CIE 1931 2 Degree Standard Observer'])
//   -> XYZ (sum over lambda) -> linear sRGB (the IEC 61966-2-1 D65 matrix, NO chromatic adaptation)
//   -> negative channels clipped to 0 (out-of-gamut deep reds), normalised so the largest channel = 1 (chromaticity only;
//      brightness is the glow's own intensity channel) -> the sRGB transfer curve -> 0-255.
// Known points (unit-tested against an independent 1 nm 360-830 nm integration): 1,000 K #FF1700 (deep orange-red),
// 1,500 K #FF6600, 3,000 K #FFB86D, 5,800 K #FFF1EB (near white), 10,000 K #CDD9FF, 40,000 K #9EB8FF, 1e9 K #94B1FF
// (the Rayleigh-Jeans limit: past ~40,000 K the colour is within a few levels of it - 'colour barely changes').
// Below the Draper point (~525 degC = 798 K) nothing visibly glows: DRAPER_K gates the ambient glow (GlowField), and the
// rungs below it (Death Valley, Venus) are drawn unlit (thermal false colour in their window, always labelled).

export const C2 = 1.4387769e-2; // second radiation constant, m K
export const DRAPER_K = 798.15; // ~525 degC: the first visible glow
export const SUN_SURFACE_K = 5773.15; // ~5,500 degC
export const CONVERGE_K = 40000; // 'colour barely changes past ~40,000 K'
export const C_TO_K = 273.15;

/** CIE 1931 2-degree CMFs [xbar, ybar, zbar], 380..780 nm step 5 nm (81 rows) */
export const CMF_5NM: ReadonlyArray<readonly [number, number, number]> = [
  [0.001368, 3.9e-05, 0.00645],
  [0.002236, 6.4e-05, 0.01055],
  [0.004243, 0.00012, 0.02005],
  [0.00765, 0.000217, 0.03621],
  [0.01431, 0.000396, 0.06785],
  [0.02319, 0.00064, 0.1102],
  [0.04351, 0.00121, 0.2074],
  [0.07763, 0.00218, 0.3713],
  [0.13438, 0.004, 0.6456],
  [0.21477, 0.0073, 1.03905],
  [0.2839, 0.0116, 1.3856],
  [0.3285, 0.01684, 1.62296],
  [0.34828, 0.023, 1.74706],
  [0.34806, 0.0298, 1.7826],
  [0.3362, 0.038, 1.77211],
  [0.3187, 0.048, 1.7441],
  [0.2908, 0.06, 1.6692],
  [0.2511, 0.0739, 1.5281],
  [0.19536, 0.09098, 1.28764],
  [0.1421, 0.1126, 1.0419],
  [0.09564, 0.13902, 0.81295],
  [0.05795, 0.1693, 0.6162],
  [0.03201, 0.20802, 0.46518],
  [0.0147, 0.2586, 0.3533],
  [0.0049, 0.323, 0.272],
  [0.0024, 0.4073, 0.2123],
  [0.0093, 0.503, 0.1582],
  [0.0291, 0.6082, 0.1117],
  [0.06327, 0.71, 0.07825],
  [0.1096, 0.7932, 0.05725],
  [0.1655, 0.862, 0.04216],
  [0.22575, 0.91485, 0.02984],
  [0.2904, 0.954, 0.0203],
  [0.3597, 0.9803, 0.0134],
  [0.43345, 0.99495, 0.00875],
  [0.51205, 1, 0.00575],
  [0.5945, 0.995, 0.0039],
  [0.6784, 0.9786, 0.00275],
  [0.7621, 0.952, 0.0021],
  [0.8425, 0.9154, 0.0018],
  [0.9163, 0.87, 0.00165],
  [0.9786, 0.8163, 0.0014],
  [1.0263, 0.757, 0.0011],
  [1.0567, 0.6949, 0.001],
  [1.0622, 0.631, 0.0008],
  [1.0456, 0.5668, 0.0006],
  [1.0026, 0.503, 0.00034],
  [0.9384, 0.4412, 0.00024],
  [0.85445, 0.381, 0.00019],
  [0.7514, 0.321, 0.0001],
  [0.6424, 0.265, 5e-05],
  [0.5419, 0.217, 3e-05],
  [0.4479, 0.175, 2e-05],
  [0.3608, 0.1382, 1e-05],
  [0.2835, 0.107, -1.90582e-21],
  [0.2187, 0.0816, 0],
  [0.1649, 0.061, 0],
  [0.1212, 0.04458, 0],
  [0.0874, 0.032, 0],
  [0.0636, 0.0232, 0],
  [0.04677, 0.017, 0],
  [0.0329, 0.01192, 0],
  [0.0227, 0.00821, 0],
  [0.01584, 0.005723, 0],
  [0.0113592, 0.004102, 0],
  [0.00811092, 0.002929, 0],
  [0.00579035, 0.002091, 0],
  [0.00410946, 0.001484, 0],
  [0.00289933, 0.001047, 0],
  [0.00204919, 0.00074, 0],
  [0.00143997, 0.00052, 0],
  [0.000999949, 0.0003611, 0],
  [0.000690079, 0.0002492, 0],
  [0.000476021, 0.0001719, 0],
  [0.000332301, 0.00012, 0],
  [0.000234826, 8.48e-05, 0],
  [0.00016615, 6e-05, 0],
  [0.000117413, 4.24e-05, 0],
  [8.30753e-05, 3e-05, 0],
  [5.87065e-05, 2.12e-05, 0],
  [4.15099e-05, 1.499e-05, 0]
];
export const CMF_START_NM = 380;
export const CMF_STEP_NM = 5;

/** sRGB (D65) from XYZ: IEC 61966-2-1 */
const M = [
  [3.2404542, -1.5371385, -0.4985314],
  [-0.969266, 1.8760108, 0.041556],
  [0.0556434, -0.2040259, 1.0572252],
] as const;

/** relative XYZ of a black body at T kelvin (unnormalised; T >= ~1e7 uses the Rayleigh-Jeans form exactly) */
export const bbXYZ = (T: number): [number, number, number] => {
  let X = 0, Y = 0, Z = 0;
  for (let i = 0; i < CMF_5NM.length; i++) {
    const lam = (CMF_START_NM + i * CMF_STEP_NM) * 1e-9;
    const x = C2 / (lam * T);
    // spectral radiance shape; expm1 keeps precision for small x; scaled by T to stay finite for large T
    const B = x < 1e-7 ? 1 / (lam ** 4 * C2) : 1 / (lam ** 5 * Math.expm1(x) * T);
    X += B * CMF_5NM[i][0];
    Y += B * CMF_5NM[i][1];
    Z += B * CMF_5NM[i][2];
  }
  return [X, Y, Z];
};

const encode = (v: number) => (v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055);

/** linear sRGB, negatives clipped, max channel = 1 */
export const bbLinear = (T: number): [number, number, number] => {
  const [X, Y, Z] = bbXYZ(T);
  const lin = M.map((r) => Math.max(0, r[0] * X + r[1] * Y + r[2] * Z));
  const mx = Math.max(lin[0], lin[1], lin[2], 1e-30);
  return [lin[0] / mx, lin[1] / mx, lin[2] / mx];
};

const CACHE = new Map<number, [number, number, number]>();
/** sRGB 0-255 (rounded) of a black body at T kelvin (cached per 0.001 decade) */
export const bbRgb = (T: number): [number, number, number] => {
  const key = Math.round(Math.log10(Math.max(1, T)) * 1000);
  const hit = CACHE.get(key);
  if (hit) return hit;
  const Tq = Math.pow(10, key / 1000);
  const v = bbLinear(Tq).map((c) => Math.round(255 * encode(c))) as [number, number, number];
  if (CACHE.size > 4000) CACHE.clear();
  CACHE.set(key, v);
  return v;
};

export const bbHex = (T: number) => "#" + bbRgb(T).map((c) => c.toString(16).padStart(2, "0")).join("").toUpperCase();
export const bbCss = (T: number, alpha = 1) => {
  const [r, g, b] = bbRgb(T);
  return `rgba(${r},${g},${b},${alpha})`;
};

/** CIE 1976 u'v' chromaticity of a black body (for the convergence test) */
export const bbUV = (T: number): [number, number] => {
  const [X, Y, Z] = bbXYZ(T);
  const d = X + 15 * Y + 3 * Z;
  return [(4 * X) / d, (9 * Y) / d];
};

/** mix an sRGB colour toward white by k (0..1): caption number tones are lifted for contrast */
export const lighten = (rgb: [number, number, number], k: number): [number, number, number] =>
  rgb.map((c) => Math.round(c + (255 - c) * k)) as [number, number, number];

/** log10 of a temperature in kelvin (the ladder rail's axis) */
export const logK = (T: number) => Math.log10(T);

/** the relative LUMINANCE of a just-glowing body for display (QA B9): the colour channels are max-normalised (hue only),
 *  but the first glow at the Draper point is a DIM dull red. 0.35 at 798 K rising to 1 by ~1,500 K (log ramp); 1 above.
 *  Hue is unchanged: multiply the rgb by this. */
export const glowLum = (T: number) => {
  const a = Math.log10(DRAPER_K), b = Math.log10(1500);
  const s = Math.max(0, Math.min(1, (Math.log10(Math.max(1, T)) - a) / (b - a)));
  return 0.35 + 0.65 * Math.pow(s, 0.8);
};
