#!/usr/bin/env python3
"""Stage the woff2 files theme.ts loads into public/fonts/ and verify them (idempotent).

Copied from projects/how-a-mosquito-drinks/fetch_fonts.py (video 14, QA passed). ALL FOUR faces are COPIED from video 14's
public/fonts (the same woff2 files @remotion/google-fonts would request; curl only if one were missing). The headless render browser never touches the network: theme.ts
hands the package's own metadata (getInfo) to its from-info loader with staticFile() URLs.

File naming (theme.ts depends on it): <ImportName>-<style>-<weight>-<subset>.woff2
Faces (art-direction.md 'Type'; scene_plan.metadata.typography):
  IBM Plex Sans Condensed 600/700  display: labels ('FRONT' / 'BACK', >= 28 px), stamps ('IMPOSSIBLE?',
                                   'NOT ALWAYS'), the ledger's figures, and the PLACARDS (600; measured below)
  Roboto Mono 400/500              data: 'PROCEDURE: LANDING', the checklist rows, the ELAPSED clock, readouts ('total spin: 0'), the ledger,, honesty tags (>= 24 px)
  Bricolage Grotesque 800          captions + the settle CTA (channel standard)
  Spline Sans Mono 600             honesty tab (channel standard)

Lesson 10 checks, printed and asserted:
  1. ESM: every face resolves through the package's ES-module build (node import -> dist/esm/<Name>.mjs), and getInfo()
     lists every weight we load in the 'latin' subset.
  2. Glyphs: every character of every on-screen string is in the cmap of EVERY look face (Plex Cond 600, 700, Roboto Mono
     400, 500: a builder may set any verified string in any of them), built from scene_plan.metadata.verified_on_screen_strings
     + placards (+ fine print) + digits + the clock / gauge extras ('0:00', '%', '~'); captions + the CTA in Bricolage; the
     tab words in Spline. Probed explicitly: · ~ % : ( ) ' ’ - × ° → ≈ ✓. Ticks, arrows and the '~' are DRAWN as SVG
     (shared/Icons.tsx, shared/Type.tsx <Rich>): '→' / '≈' / '✓' are never set.
  3. Placard fit (lesson 31: fine print >= 24 px): each placard's main line and fine print measured in Plex Sans Condensed
     600 and Roboto Mono 400 against the 716 px text width; the chosen face (Plex Cond 600) must fit main >= 22 px on one
     line and fine print at >= 24 px on one line inside the 80 px rail -> printed + fonts.manifest.json 'placard_fit'.
Writes shared/metrics.generated.ts (advance widths for measure()).
Licence: SIL Open Font License 1.1 (Plex, Bricolage, Spline) / Apache 2.0 (Roboto Mono).
Run from anywhere: python3 projects/how-a-cat-lands/fetch_fonts.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPOSER = HERE.parent.parent / "remotion-composer"
OUT = HERE / "public" / "fonts"
V13 = HERE.parent / "how-a-mosquito-drinks" / "public" / "fonts"   # video 14: all four faces (no network)

# (import name, style, weights, subsets)
WANT = [
    ("IBMPlexSansCondensed", "normal", ["600", "700"], ["latin"]),
    ("RobotoMono", "normal", ["400", "500"], ["latin"]),
    ("BricolageGrotesque", "normal", ["800"], ["latin"]),
    ("SplineSansMono", "normal", ["600"], ["latin"]),
]
PROBE = {"É": 0xC9, "·": 0xB7, "~": 0x7E, "%": 0x25, ":": 0x3A, "(": 0x28, ")": 0x29, "'": 0x27, "’": 0x2019, "-": 0x2D, "×": 0xD7,
         "°": 0xB0, ">": 0x3E, ",": 0x2C, "?": 0x3F, "/": 0x2F, "→": 0x2192, "≈": 0x2248, "✓": 0x2713}
# characters that are DRAWN, never set (arrows / approx / tick marks -> SVG)
DRAWN = {"→", "≈", "✓"}
PLACARD_TEXT_W = 772 - 2 * 28


def required() -> dict[str, str]:
    plan = json.loads((HERE / "artifacts/scene_plan.json").read_text())
    script = json.loads((HERE / "artifacts/script.json").read_text())
    md = plan["metadata"]
    strings = md["verified_on_screen_strings"] + [p["text"] + p.get("fine_print", "") for p in md["placards"]]
    look = "".join(strings) + "0123456789 ,.~%:·-() ELAPSED s"
    for k in DRAWN:
        look = look.replace(k, "")
    caps = "".join(s["text"] for s in script["sections"]) + "Seen a cat do this?"
    tab = "MEASURED PROBABLY MAYBE · "
    return {"IBMPlexSansCondensed": look, "RobotoMono": look, "BricolageGrotesque": caps, "SplineSansMono": tab}


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
    plan = json.loads((HERE / "artifacts/scene_plan.json").read_text())
    faces = {"IBMPlexSansCondensed600": "IBMPlexSansCondensed-normal-600-latin.woff2", "RobotoMono400": "RobotoMono-normal-400-latin.woff2"}
    out = {}
    for name, file in faces.items():
        rows = []
        for pl in plan["metadata"]["placards"]:
            main_ok = next((px for px in (26, 25, 24, 23, 22) if advance(file, px)(pl["text"]) <= PLACARD_TEXT_W), None)
            fine = pl.get("fine_print")
            fine_px = next((px for px in (26, 25, 24) if advance(file, px)(fine) <= PLACARD_TEXT_W), None) if fine else None
            rows_h = (main_ok * 1.15 if main_ok else 999) + (fine_px * 1.15 + 2 if fine and fine_px else (0 if not fine else 999))
            rows.append({"text": pl["text"], "fine_print": fine, "main_px_one_line": main_ok, "fine_px": fine_px,
                         "main_w_at_24": round(advance(file, 24)(pl["text"]), 1), "fine_w_at_24": round(advance(file, 24)(fine), 1) if fine else None,
                         "fits_80px_rail": bool(main_ok and (not fine or fine_px) and rows_h <= 74)})
        out[name] = rows
        print(name, [(r["main_px_one_line"], r["fine_px"], r["fine_w_at_24"], r["fits_80px_rail"]) for r in rows])
    if strict:
        assert all(r["fits_80px_rail"] for r in out["IBMPlexSansCondensed600"]), out["IBMPlexSansCondensed600"]
    return out


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
                    if (V13 / dst.name).exists():
                        shutil.copy2(V13 / dst.name, dst)
                        print("copied", dst.name, "from video 14")
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
        print(f'{r["file"]:<46} {r["esm"]:<56}', " ".join(f"{g}{'+' if ok else '-'}" for g, ok in r["probe"].items()),
              "| required missing:", missing or "none")
    fit = placard_fit(strict="--nofit" not in sys.argv)
    (OUT / "fonts.manifest.json").write_text(json.dumps({"faces": rows, "placard_fit": fit}, indent=1, ensure_ascii=False) + "\n")
    assert not bad, bad
    print(len(rows), "font files in", OUT, "- all ESM, all required glyphs present")


def write_metrics() -> None:
    """shared/metrics.generated.ts: per-face advance widths (em), cap height, ascent, descent - shared/Type.tsx measure()
    sizes text synchronously at render time (no canvas measureText / font-load race)."""
    from fontTools.ttLib import TTFont
    faces = {"display": "IBMPlexSansCondensed-normal-700-latin.woff2", "displaySemi": "IBMPlexSansCondensed-normal-600-latin.woff2",
             "mono": "RobotoMono-normal-400-latin.woff2", "monoMed": "RobotoMono-normal-500-latin.woff2",
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
