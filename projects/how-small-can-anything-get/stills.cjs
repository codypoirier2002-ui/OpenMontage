#!/usr/bin/env node
// Batch stills: bundle ONCE, then render many frames (much faster than still.sh per frame).
//   node stills.cjs --frames 0,40,90,148 [--scale 0.5] [--out renders/review/all]
//   node stills.cjs --scenes [--per 4] [--scale 0.5]      # 4 frames per scene at 15/40/65/90% of its window
//   node stills.cjs --frames 0,1506 --layers picture        # the picture layer only (no overlay plane)
//   node stills.cjs --frames 300 --props some_props.json    # alternative props (A/B comparisons)
// Output: <out>/f<NNNN>.png. Uses remotion-composer's node_modules via createRequire. The bundle dir is created up
// front (mkdtemp) and deleted in a finally, even when bundling or a render fails.
const path = require("node:path");
const fs = require("node:fs");
const { createRequire } = require("node:module");

const HERE = __dirname;
const COMPOSER = path.resolve(HERE, "../../remotion-composer");
const req = createRequire(path.join(COMPOSER, "package.json"));
const { bundle } = req("@remotion/bundler");
const { renderStill, selectComposition } = req("@remotion/renderer");

const arg = (k, d) => {
  const i = process.argv.indexOf(`--${k}`);
  return i >= 0 ? process.argv[i + 1] : d;
};
const props = JSON.parse(fs.readFileSync(arg("props", null) ? path.resolve(arg("props", null)) : path.join(HERE, "artifacts/props.json"), "utf8"));
if (arg("layers", null)) props.layers = arg("layers", "all");
const scale = Number(arg("scale", "0.5"));
const out = path.resolve(HERE, arg("out", "renders/review/all"));
let frames = [];
if (process.argv.includes("--scenes")) {
  const per = Number(arg("per", "4"));
  const qs = per === 4 ? [0.15, 0.4, 0.65, 0.9] : Array.from({ length: per }, (_, i) => (i + 0.5) / per);
  for (const s of props.timeline.scenes) for (const q of qs) frames.push(s.from + Math.floor(s.durationInFrames * q));
} else {
  frames = arg("frames", "0").split(",").map(Number);
}

(async () => {
  fs.mkdirSync(out, { recursive: true });
  // the bundle dir is chosen up front so the finally below removes it even when bundling itself fails
  const serveUrl = fs.mkdtempSync(path.join(require("node:os").tmpdir(), "remotion-webpack-bundle-"));
  try {
    await bundle({
      outDir: serveUrl,
      entryPoint: path.join(HERE, "index.tsx"),
      publicDir: path.join(HERE, "public"),
      webpackOverride: (c) => ({
        ...c,
        resolve: { ...c.resolve, modules: [...(c.resolve?.modules ?? ["node_modules"]), path.join(COMPOSER, "node_modules")] },
      }),
    });
    const browserExecutable = process.env.REMOTION_BROWSER_EXECUTABLE || "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
    const composition = await selectComposition({ serveUrl, id: "ScaleWell", inputProps: props, browserExecutable });
    for (const f of frames) {
      const t0 = Date.now();
      const output = path.join(out, `f${String(f).padStart(4, "0")}.png`);
      await renderStill({ serveUrl, composition, frame: f, output, inputProps: props, scale, browserExecutable });
      console.log(output, `${Date.now() - t0} ms`);
    }
  } finally {
    // ALWAYS delete the webpack bundle (an earlier build filled the disk with stale bundles)
    fs.rmSync(serveUrl, { recursive: true, force: true });
    console.log("removed bundle", serveUrl);
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
