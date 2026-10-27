#!/usr/bin/env python3
"""Stage the woff2 files theme.ts loads into public/fonts/ and verify them (idempotent).

Pattern copied from projects/what-if-earth-stopped-spinning/fetch_fonts.py (video 12, delivered, QA passed). The channel
faces (Bricolage Grotesque 800, Spline Sans Mono 600) are COPIED from video 12; the look faces are fetched from
fonts.gstatic.com (the URLs @remotion/google-fonts itself would request). The headless render browser never touches the
network: theme.ts hands the package's own metadata (getInfo) to its from-info loader with staticFile() URLs.

File naming (theme.ts depends on it): <ImportName>-<style>-<weight>-<subset>.woff2
Faces (art-direction.md 'Type'; scene_plan.metadata.typography):
  Saira Condensed 700      display: rung numbers ('56.7 °C' 96 px, '> 5,000,000,000,000 K' 88 px, '1.4 × 10' + a raised
                           '32' + ' K' 104 px), compact rung labels, and the PLACARDS (measured below: IBM Plex Mono at
                           >= 24 px cannot fit the KSTAR / Planck placards in the 716 px rail - BUILD.md §9)
  IBM Plex Mono 400/500    data: rung descriptions, rail marks, tags, chips, 'log scale', the floor label
  Bricolage Grotesque 800  captions + the settle CTA (channel standard)
  Spline Sans Mono 600     honesty tab (channel standard)

Lesson 10 checks, printed and asserted:
  1. ESM: every face resolves through the package's ES-module build (node import -> dist/esm/<Name>.mjs).
  2. Glyphs: every character of every on-screen string is in the cmap of EVERY look face (Saira 700, Plex 400, Plex 500:
     a builder may set any verified string in any of them), built from scene_plan.metadata.verified_on_screen_strings +
     placards (+ fine print) + digits + the counter / chip extras; captions + the CTA in Bricolage; the tab words in
     Spline. Probed explicitly: × ° · ~ > - (U+002D) − (U+2212) ^ ⁰-⁹ superscripts , ' ’ : / ( ) ? and → ≈.
     The exponent in '1.4 × 10^32 K' is DRAWN as a raised smaller '32' (shared/Type.tsx <Sci>), so '^' is never set and
     is removed from the requirement; arrows are SVG (shared/Icons.tsx). The verified strings use ASCII '-' (hyphen-minus)
     in '0 K = -273.15 °C' and the CTA: that is the character set on screen ('−' U+2212 is probed and reported only).
  3. Placard fit (lesson 31: fine print >= 24 px): each placard's main line and fine print measured in Saira Condensed 700
     and IBM Plex Mono 400 against the 716 px text width; the chosen face (Saira) must fit main >= 22 px on <= 2 lines and
     fine print at >= 24 px on one line inside the 80 px rail -> printed + fonts.manifest.json 'placard_fit'.
Writes shared/metrics.generated.ts (advance widths for measure()).
Licence: SIL Open Font License 1.1 (all).
Run from anywhere: python3 projects/how-hot-can-it-get/fetch_fonts.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPOSER = HERE.parent.parent / "remotion-composer"
OUT = HERE / "public" / "fonts"
V12 = HERE.parent / "what-if-earth-stopped-spinning" / "public" / "fonts"

# (import name, style, weights, subsets)
WANT = [
    ("SairaCondensed", "normal", ["700"], ["latin"]),
    ("IBMPlexMono", "normal", ["400", "500"], ["latin"]),
    ("BricolageGrotesque", "normal", ["800"], ["latin"]),
    ("SplineSansMono", "normal", ["600"], ["latin"]),
]
PROBE = {"×": 0xD7, "°": 0xB0, "·": 0xB7, "~": 0x7E, ">": 0x3E, "-": 0x2D, "−": 0x2212, "^": 0x5E, "³": 0xB3, "²": 0xB2,
         ",": 0x2C, "'": 0x27, "’": 0x2019, ":": 0x3A, "/": 0x2F, "(": 0x28, ")": 0x29, "?": 0x3F, "=": 0x3D, "→": 0x2192, "≈": 0x2248}
# characters that are DRAWN, never set ('^' -> the raised exponent; arrows / approx -> SVG)
DRAWN = {"^", "→", "≈"}
PLACARD_TEXT_W = 772 - 2 * 28


def required() -> dict[str, str]:
    plan = json.loads((HERE / "artifacts/scene_plan.json").read_text())
    script = json.loads((HERE / "artifacts/script.json").read_text())
    md = plan["metadata"]
    strings = md["verified_on_screen_strings"] + [p["text"] + p.get("fine_print", "") for p in md["placards"]]
    look = "".join(strings) + "0123456789 ,.~>×°·-: K °C zeros"
    for k in DRAWN:
        look = look.replace(k, "")
    caps = "".join(s["text"] for s in script["sections"]) + "Floor or ceiling - which is stranger?"
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


def placard_fit() -> dict:
    plan = json.loads((HERE / "artifacts/scene_plan.json").read_text())
    faces = {"SairaCondensed700": "SairaCondensed-normal-700-latin.woff2", "IBMPlexMono400": "IBMPlexMono-normal-400-latin.woff2"}
    out = {}
    for name, file in faces.items():
        rows = []
        for pl in plan["metadata"]["placards"]:
            main_ok = next((px for px in (26, 25, 24, 23, 22) if advance(file, px)(pl["text"]) <= PLACARD_TEXT_W), None)
            two = None
            if main_ok is None and " · " in pl["text"]:
                t = pl["text"]
                cuts = [i for i in range(len(t)) if t.startswith(" · ", i)]
                best = min(cuts, key=lambda i: max(advance(file, 22)(t[:i]), advance(file, 22)(t[i + 3:])))
                two = next((px for px in (26, 25, 24, 23, 22) if max(advance(file, px)(t[:best + 2]), advance(file, px)(t[best + 3:])) <= PLACARD_TEXT_W), None)
            fine = pl.get("fine_print")
            fine_px = next((px for px in (26, 25, 24) if advance(file, px)(fine) <= PLACARD_TEXT_W), None) if fine else None
            lines = 1 if main_ok else 2
            size = main_ok or two
            rows_h = (lines * size * 1.15 if size else 999) + (fine_px * 1.15 + 2 if fine and fine_px else (0 if not fine else 999))
            rows.append({"text": pl["text"], "main_px_one_line": main_ok, "main_px_two_lines": two, "fine_px": fine_px,
                         "main_w_at_24": round(advance(file, 24)(pl["text"]), 1), "fine_w_at_24": round(advance(file, 24)(fine), 1) if fine else None,
                         "fits_80px_rail": bool(size and (not fine or fine_px) and rows_h <= 74)})
        out[name] = rows
        print(name, [(r["main_px_one_line"], r["main_px_two_lines"], r["fine_px"], r["fits_80px_rail"]) for r in rows])
    assert all(r["fits_80px_rail"] for r in out["SairaCondensed700"]), out["SairaCondensed700"]
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    req = required()
    for name, style, weights, subsets in WANT:
        meta, resolved = info(name)
        assert "/dist/esm/" in resolved and resolved.endswith(".mjs"), (name, resolved)
        for w in weights:
            for sub in subsets:
                url = meta["fonts"][style][w][sub]
                dst = OUT / f"{name}-{style}-{w}-{sub}.woff2"
                if not (dst.exists() and dst.stat().st_size > 1000):
                    if (V12 / dst.name).exists():
                        shutil.copy2(V12 / dst.name, dst)
                        print("copied", dst.name, "from video 12")
                    else:
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
        print(f'{r["file"]:<44} {r["esm"]:<52}', " ".join(f"{g}{'+' if ok else '-'}" for g, ok in r["probe"].items()),
              "| required missing:", missing or "none")
    fit = placard_fit()
    (OUT / "fonts.manifest.json").write_text(json.dumps({"faces": rows, "placard_fit": fit}, indent=1, ensure_ascii=False) + "\n")
    assert not bad, bad
    print(len(rows), "font files in", OUT, "- all ESM, all required glyphs present")


def write_metrics() -> None:
    """shared/metrics.generated.ts: per-face advance widths (em), cap height, ascent, descent - shared/Type.tsx measure()
    sizes text synchronously at render time (no canvas measureText / font-load race)."""
    from fontTools.ttLib import TTFont
    faces = {"display": "SairaCondensed-normal-700-latin.woff2", "mono": "IBMPlexMono-normal-400-latin.woff2",
             "monoMed": "IBMPlexMono-normal-500-latin.woff2", "caption": "BricolageGrotesque-normal-800-latin.woff2"}
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
        "export const METRICS: Record<\"display\" | \"mono\" | \"monoMed\" | \"caption\", { adv: Record<string, number>; cap: number; asc: number; desc: number; space: number }> = "
        + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")


if __name__ == "__main__":
    main()
    write_metrics()
