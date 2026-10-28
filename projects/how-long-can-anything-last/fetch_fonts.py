#!/usr/bin/env python3
"""Stage the woff2 files theme.ts loads into public/fonts/ and verify them (idempotent).

Adapted from projects/how-a-cat-lands/fetch_fonts.py (video 15, QA passed). No earlier project's public/fonts survives in
this container, so the files are FETCHED from fonts.gstatic.com: the exact URLs @remotion/google-fonts itself would request
(getInfo(), read through the package's ES-module build). The headless render browser never touches the network: theme.ts
hands the package's own metadata (getInfo) to its from-info loader with staticFile() URLs.

File naming (theme.ts depends on it): <ImportName>-<style>-<weight>-<subset>.woff2
Faces (art-direction.md 'Type' = video 13's display + mono faces; scene_plan.metadata.typography):
  Saira Condensed 600/700   display: rung NAMES ('WALK', 'FALCON (dive)', 'PARKER (fastest built)', >= 28 px), the YOU tag,
                            'ENERGY NEEDED', the placards (600; measured below)
  IBM Plex Mono 400/500     data (SLASHED ZEROS): rung numbers ('~107,000', '1,079,252,849'), the decade ticks, the ZEROS
                            counter, the LHC readout '99.9999991 %', 'km/h · log scale', honesty tags (>= 24 px)
  Bricolage Grotesque 800   captions + the settle CTA (channel standard)
  Spline Sans Mono 600      honesty tab (channel standard)

Lesson 10 checks, printed and asserted:
  1. ESM: every face resolves through the package's ES-module build (node import -> dist/esm/<Name>.mjs), and getInfo()
     lists every weight we load in the 'latin' subset.
  2. Glyphs: every character of every on-screen string is in the cmap of EVERY look face (Saira 600, 700, Plex Mono 400,
     500: a builder may set any verified string in any of them), built from scene_plan.metadata.verified_on_screen_strings
     + placards (+ fine print) + digits + the counter / readout extras; captions + the CTA in Bricolage; the tab words in
     Spline. Probed explicitly: · ~ % : ( ) ' ’ - × ° → ≈ ✓ ⁹. Arrows are DRAWN as SVG (shared/Icons.tsx) and '~' tall by
     shared/Type.tsx <Rich>: '→' / '≈' / '✓' are never set.
  3. Slashed zero: IBM Plex Mono's default '0' is slashed (asserted: its 'zero' glyph has more contours than 'O').
  4. Placard fit (lesson 31: fine print >= 24 px): each placard's main line and fine print measured in Saira Condensed 600
     and IBM Plex Mono 400 against the 716 px text width; the chosen face (Saira 600) must fit main >= 22 px on one line and
     fine print at >= 24 px on one line inside the 80 px rail -> printed + fonts.manifest.json 'placard_fit'.
Writes shared/metrics.generated.ts (advance widths for measure()).
Licence: SIL Open Font License 1.1 (all four).
Run from anywhere: python3 projects/how-long-can-anything-last/fetch_fonts.py
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPOSER = HERE.parent.parent / "remotion-composer"
OUT = HERE / "public" / "fonts"

# (import name, style, weights, subsets)
WANT = [
    ("SairaCondensed", "normal", ["600", "700"], ["latin"]),
    ("IBMPlexMono", "normal", ["400", "500"], ["latin"]),
    ("BricolageGrotesque", "normal", ["800"], ["latin"]),
    ("SplineSansMono", "normal", ["600"], ["latin"]),
]
PROBE = {"·": 0xB7, "~": 0x7E, "%": 0x25, ":": 0x3A, "(": 0x28, ")": 0x29, "'": 0x27, "’": 0x2019, "-": 0x2D, "×": 0xD7,
         "°": 0xB0, ",": 0x2C, "?": 0x3F, "/": 0x2F, "=": 0x3D, "→": 0x2192, "≈": 0x2248, "✓": 0x2713, "⁹": 0x2079}
# characters that are DRAWN, never set (arrows / approx / tick marks -> SVG)
DRAWN = {"→", "≈", "✓"}
PLACARD_TEXT_W = 772 - 2 * 28
# the placards as BUILT (build_props.py PLACARDS; placard 3 reworded for lesson 32, see there)
PLACARDS_BUILT = [
    ("cheetah: collar study, Wilson et al., Nature 2013", "falcon dive ~390 km/h is commonly cited, weakly sourced"),
    ("sound: 343 m/s in 20 °C air · Earth: 29.78 km/s (NASA)", "km/h on a log scale: each tick is 10x"),
    ("Parker Solar Probe: ~692,000 km/h (Dec 2024)", "NASA's figure as reported by Space.com · speed from falling toward the Sun"),
    ("c = 299,792,458 m/s exactly (NIST)", "energy needed grows without limit as speed nears c"),
    ("CERN LHC: protons at 6.8 TeV (2022)", "0.999999991 of light speed"),
]


def required() -> dict[str, str]:
    plan = json.loads((HERE / "artifacts/scene_plan.json").read_text())
    script = json.loads((HERE / "artifacts/script.json").read_text())
    md = plan["metadata"]
    strings = md["verified_on_screen_strings"] + [p["text"] + p.get("fine_print", "") for p in md["placards"]] + [a + b for a, b in PLACARDS_BUILT]
    look = "".join(strings) + "0123456789 ,.~%:·-() ×°=/'"
    for k in DRAWN:
        look = look.replace(k, "")
    caps = "".join(s["text"] for s in script["sections"]) + "What's the fastest thing you've ridden?"
    tab = "MEASURED PROBABLY MAYBE · "
    return {"SairaCondensed": look, "IBMPlexMono": look, "BricolageGrotesque": caps, "SplineSansMono": tab}


def info(import_name: str) -> tuple[dict, str]:
    js = (f"const r = import.meta.resolve('@remotion/google-fonts/{import_name}');"
          f"import('@remotion/google-fonts/{import_name}').then(m => process.stdout.write(JSON.stringify({{r, i: m.getInfo()}})))")
    out = json.loads(subprocess.run(["node", "--input-type=module", "-e", js], cwd=COMPOSER, check=True,
                                    capture_output=True, text=True).stdout)
    return out["i"], out["r"]


def advance(file: str, px: float):
    from fontTools.ttLib import TTFont
    f = TTFont(str(OUT / file))
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    space = hmtx[cmap[32]][0]
    return lambda s: sum(hmtx[cmap[ord(c)]][0] if ord(c) in cmap else space for c in s) / upm * px


def placard_fit(strict: bool = True) -> dict:
    faces = {"SairaCondensed600": "SairaCondensed-normal-600-latin.woff2", "IBMPlexMono400": "IBMPlexMono-normal-400-latin.woff2"}
    out = {}
    for name, file in faces.items():
        rows = []
        for text, fine in PLACARDS_BUILT:
            main_ok = next((px for px in (26, 25, 24, 23, 22) if advance(file, px)(text) <= PLACARD_TEXT_W), None)
            fine_px = next((px for px in (26, 25, 24) if advance(file, px)(fine) <= PLACARD_TEXT_W), None) if fine else None
            rows_h = (main_ok * 1.15 if main_ok else 999) + (fine_px * 1.15 + 2 if fine and fine_px else (0 if not fine else 999))
            rows.append({"text": text, "fine_print": fine, "main_px_one_line": main_ok, "fine_px": fine_px,
                         "main_w_at_24": round(advance(file, 24)(text), 1), "fine_w_at_24": round(advance(file, 24)(fine), 1) if fine else None,
                         "fits_80px_rail": bool(main_ok and (not fine or fine_px) and rows_h <= 74)})
        out[name] = rows
        print(name, [(r["main_px_one_line"], r["fine_px"], r["fine_w_at_24"], r["fits_80px_rail"]) for r in rows])
    if strict:
        assert all(r["fits_80px_rail"] for r in out["SairaCondensed600"]), out["SairaCondensed600"]
    return out


def slashed_zero(file: str) -> bool:
    """IBM Plex Mono's default zero is slashed: the 'zero' glyph carries more contours than 'O' (the slash adds one)."""
    from fontTools.ttLib import TTFont
    f = TTFont(str(OUT / file))
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    from fontTools.pens.recordingPen import RecordingPen
    n = {}
    for ch in "0O":
        pen = RecordingPen()
        gs[cmap[ord(ch)]].draw(pen)
        n[ch] = sum(1 for op, _ in pen.value if op == "closePath")
    return n["0"] > n["O"]


def main() -> None:
    import sys
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    req = required()
    for name, style, weights, subsets in WANT:
        meta, resolved = info(name)
        assert "/dist/esm/" in resolved and resolved.endswith(".mjs"), (name, resolved)
        for w in weights:
            for sub in subsets:
                assert sub in meta["fonts"][style][w], (name, w, sub)
                url = meta["fonts"][style][w][sub]
                dst = OUT / f"{name}-{style}-{w}-{sub}.woff2"
                if not (dst.exists() and dst.stat().st_size > 1000):
                    subprocess.run(["curl", "-sSfL", "--retry", "3", "-o", str(dst), url], check=True)
                    print("fetched", dst.name)
                rows.append({"family": meta["fontFamily"], "import": name, "weight": w, "esm": resolved.split("node_modules/")[-1],
                             "file": dst.name, "url": url, "bytes": dst.stat().st_size})
    from fontTools.ttLib import TTFont
    bad = []
    for r in rows:
        cmap = TTFont(str(OUT / r["file"])).getBestCmap()
        r["probe"] = {g: (cp in cmap) for g, cp in PROBE.items()}
        need = sorted(set(req[r["import"]]) - {"\n"})
        missing = [c for c in need if ord(c) not in cmap]
        r["required_missing"] = missing
        r["lacks"] = [g for g, ok in r["probe"].items() if not ok]
        if missing:
            bad.append((r["file"], missing))
        print(f'{r["file"]:<46} {r["esm"]:<56}', " ".join(f"{g}{'+' if ok else '-'}" for g, ok in r["probe"].items()),
              "| required missing:", missing or "none")
    sz = {f: slashed_zero(f) for f in ("IBMPlexMono-normal-400-latin.woff2", "IBMPlexMono-normal-500-latin.woff2")}
    print("slashed zero:", sz)
    assert all(sz.values()), ("IBM Plex Mono zero is not slashed", sz)
    fit = placard_fit(strict="--nofit" not in sys.argv)
    (OUT / "fonts.manifest.json").write_text(json.dumps({"faces": rows, "slashed_zero": sz, "placard_fit": fit}, indent=1, ensure_ascii=False) + "\n")
    assert not bad, bad
    print(len(rows), "font files in", OUT, "- all ESM, all required glyphs present")


def write_metrics() -> None:
    """shared/metrics.generated.ts: per-face advance widths (em), cap height, ascent, descent - shared/Type.tsx measure()
    sizes text synchronously at render time (no canvas measureText / font-load race)."""
    from fontTools.ttLib import TTFont
    faces = {"display": "SairaCondensed-normal-700-latin.woff2", "displaySemi": "SairaCondensed-normal-600-latin.woff2",
             "mono": "IBMPlexMono-normal-400-latin.woff2", "monoMed": "IBMPlexMono-normal-500-latin.woff2",
             "caption": "BricolageGrotesque-normal-800-latin.woff2"}
    out = {}
    for k, f in faces.items():
        t = TTFont(str(OUT / f))
        cmap, hm, upm, os2 = t.getBestCmap(), t["hmtx"], t["head"].unitsPerEm, t["OS/2"]
        out[k] = {"adv": {chr(c): round(hm[g][0] / upm, 4) for c, g in cmap.items() if c < 0x2300},
                  "cap": round(getattr(os2, "sCapHeight", 0) / upm, 4), "asc": round(t["hhea"].ascent / upm, 4),
                  "desc": round(-t["hhea"].descent / upm, 4), "space": round(hm[cmap[32]][0] / upm, 4)}
    (HERE / "shared/metrics.generated.ts").write_text(
        "// GENERATED (fetch_fonts.py, from public/fonts via fontTools): per-face advance widths in em, cap height, ascent, descent.\n"
        "// Used by shared/Type.tsx measure() so text width is known synchronously at render time (no measureText / font-load race).\n"
        "export const METRICS: Record<\"display\" | \"displaySemi\" | \"mono\" | \"monoMed\" | \"caption\", { adv: Record<string, number>; cap: number; asc: number; desc: number; space: number }> = "
        + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")


if __name__ == "__main__":
    main()
    write_metrics()
