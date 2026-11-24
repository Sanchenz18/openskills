#!/usr/bin/env python3
"""Lint a WaveJSON source (and optionally its rendered SVG) for label problems.

Source checks (always):
  - edge text over budget (display width > 12, or more than 2 words)
  - data label wider than the wave segment it sits on
  - edge referencing a node that does not exist
  - data label count differing from the number of data segments (warning)
  - long data labels while config.hscale < 2 (warning)

SVG checks (with --svg):
  - estimated text boxes overlapping each other
  - text boxes overlapping an unrelated rect (text is allowed on its own
    background rect, i.e. a rect that fully contains it and nothing else)
  - text boxes extending outside the root canvas

Display width: CJK / full-width characters count 2, everything else 1.
Exit code 0 = pass (warnings allowed), 1 = errors found, 2 = bad input.
Only the Python standard library is used.
"""

import argparse
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

EDGE_TEXT_MAX_UNITS = 12
EDGE_TEXT_MAX_WORDS = 2
UNITS_PER_SLOT = 2.8  # conservative fit budget per wave slot at hscale 1


def disp_width(s):
    w = 0.0
    for ch in s:
        w += 2.0 if unicodedata.east_asian_width(ch) in ("W", "F") else 1.0
    return w


def load_wavejson(path):
    text = open(path, encoding="utf-8").read()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Tolerant fallback for JSON5-ish sources: strip comments, trailing commas.
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r",\s*([}\]])", r"\1", text)
    text = re.sub(r"([{,]\s*)([A-Za-z_$][\w$-]*)\s*:", r'\1"\2":', text)
    text = text.replace("'", '"')
    return json.loads(text)


def wave_slots(wave):
    """Collapse <...> sub-cycle groups to a single slot marker."""
    out = []
    i = 0
    while i < len(wave):
        if wave[i] == "<":
            j = wave.find(">", i)
            if j == -1:
                out.append(wave[i])
                i += 1
            else:
                out.append("<")
                i = j + 1
        else:
            out.append(wave[i])
            i += 1
    return out


def data_segments(wave):
    """Return slot lengths of data segments (runs started by = or 2-9,
    continued by '.' or the same character)."""
    chars = wave_slots(wave)
    segs = []
    i = 0
    while i < len(chars):
        c = chars[i]
        if c in "=23456789":
            j = i + 1
            while j < len(chars) and (chars[j] == "." or chars[j] == c):
                j += 1
            segs.append(j - i)
            i = j
        else:
            i += 1
    return segs


def lint_source(doc):
    errors, warnings = [], []
    cfg = doc.get("config", {}) if isinstance(doc, dict) else {}
    hscale = cfg.get("hscale", 1) or 1
    nodes = set()
    signals = doc.get("signal", []) if isinstance(doc, dict) else []

    def walk(items):
        for it in items:
            if isinstance(it, list):
                walk(it)
            elif isinstance(it, dict):
                if "node" in it:
                    nodes.update(ch for ch in it["node"] if ch.isalnum())
                wave = it.get("wave")
                if wave:
                    name = it.get("name", "?")
                    segs = data_segments(wave)
                    data = it.get("data", [])
                    if isinstance(data, str):
                        data = [data]
                    if len(data) != len(segs):
                        warnings.append(
                            f"signal '{name}': {len(data)} data labels for "
                            f"{len(segs)} data segments"
                        )
                    for label, slots in zip(data, segs):
                        budget = UNITS_PER_SLOT * slots * hscale
                        if disp_width(str(label)) > budget:
                            errors.append(
                                f"signal '{name}': data label '{label}' is "
                                f"{disp_width(str(label)):.0f} units wide but its "
                                f"segment holds about {budget:.0f} (slots={slots}, "
                                f"hscale={hscale}); shorten the label, lengthen "
                                f"the segment, or raise hscale"
                            )
                        elif disp_width(str(label)) > 6 and hscale < 2:
                            warnings.append(
                                f"signal '{name}': data label '{label}' is long "
                                f"while hscale={hscale}; prefer hscale >= 2"
                            )

    walk(signals)
    for edge in doc.get("edge", []) if isinstance(doc, dict) else []:
        m = re.match(r"\s*(\S+?)\s*(?:[-~]+[>)\]])\s*(\S+?)\s*(.*)$", str(edge))
        if not m:
            warnings.append(f"edge '{edge}': could not parse")
            continue
        src, dst, text = m.group(1), m.group(2), m.group(3).strip()
        for nd in (src, dst):
            base = re.sub(r"[^A-Za-z0-9]", "", nd)
            if base and base not in nodes:
                errors.append(f"edge '{edge}': node '{base}' does not exist")
        if text:
            if disp_width(text) > EDGE_TEXT_MAX_UNITS:
                errors.append(
                    f"edge '{edge}': text '{text}' is {disp_width(text):.0f} "
                    f"units (limit {EDGE_TEXT_MAX_UNITS}); move the explanation "
                    f"to the numbered notes below the figure"
                )
            if len(text.split()) > EDGE_TEXT_MAX_WORDS:
                errors.append(
                    f"edge '{edge}': text '{text}' has more than "
                    f"{EDGE_TEXT_MAX_WORDS} words; keep at most a keyword or two"
                )
    return errors, warnings


# ---------------- SVG geometry ----------------

def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _char_em(ch):
    return 1.0 if unicodedata.east_asian_width(ch) in ("W", "F") else 0.55


def collect_boxes(root):
    texts, rects = [], []

    def walk(el, dx, dy):
        if _local(el.tag) == "defs":
            return  # template shapes are not placed on the canvas
        tr = el.get("transform", "")
        for fn, args in re.findall(r"(translate|scale)\(([^)]*)\)", tr or ""):
            vals = [float(v) for v in re.split(r"[,\s]+", args.strip()) if v]
            if fn == "translate" and vals:
                dx += vals[0]
                dy += vals[1] if len(vals) > 1 else 0.0
        tag = _local(el.tag)
        if tag == "text":
            content = "".join(el.itertext()).strip()
            if content:
                style = el.get("style", "") or ""
                m = re.search(r"font-size:\s*([\d.]+)px", style)
                fs = float(m.group(1)) if m else 11.0
                x = float(el.get("x", 0)) + dx
                y = float(el.get("y", 0)) + dy
                w = sum(_char_em(c) for c in content) * fs
                anchor = el.get("text-anchor", "start")
                if anchor == "middle":
                    x0 = x - w / 2
                elif anchor == "end":
                    x0 = x - w
                else:
                    x0 = x
                texts.append(
                    {"text": content, "box": (x0, y - 0.85 * fs, x0 + w, y + 0.25 * fs)}
                )
        elif tag == "rect":
            try:
                x = float(el.get("x", 0)) + dx
                y = float(el.get("y", 0)) + dy
                w = float(el.get("width", 0))
                h = float(el.get("height", 0))
                if w > 0 and h > 0:
                    rects.append((x, y, x + w, y + h))
            except ValueError:
                pass
        for child in el:
            walk(child, dx, dy)

    walk(root, 0.0, 0.0)
    return texts, rects


def overlap(a, b, pad=0.0):
    return (
        min(a[2], b[2]) - max(a[0], b[0]) > pad
        and min(a[3], b[3]) - max(a[1], b[1]) > pad
    )


def lint_svg(path):
    errors = []
    tree = ET.parse(path)
    root = tree.getroot()
    vb = root.get("viewBox")
    if vb:
        parts = [float(v) for v in re.split(r"[,\s]+", vb.strip()) if v]
        canvas = (parts[0], parts[1], parts[0] + parts[2], parts[1] + parts[3])
    else:
        w = float(re.sub(r"[^0-9.]", "", root.get("width", "0")) or 0)
        h = float(re.sub(r"[^0-9.]", "", root.get("height", "0")) or 0)
        canvas = (0, 0, w, h)
    texts, rects = collect_boxes(root)
    for i, t in enumerate(texts):
        b = t["box"]
        if b[0] < canvas[0] - 1 or b[1] < canvas[1] - 1 or b[2] > canvas[2] + 1 or b[3] > canvas[3] + 1:
            errors.append(f"svg: text '{t['text']}' extends outside the canvas")
        for u in texts[i + 1 :]:
            if overlap(b, u["box"], pad=0.5):
                errors.append(
                    f"svg: texts '{t['text']}' and '{u['text']}' overlap"
                )
        for r in rects:
            if overlap(b, r, pad=0.5):
                contains = r[0] <= b[0] and r[1] <= b[1] and r[2] >= b[2] and r[3] >= b[3]
                if not contains:
                    errors.append(
                        f"svg: text '{t['text']}' spills onto a box it does not belong to"
                    )
                    break
    return errors


def main():
    ap = argparse.ArgumentParser(description="WaveDrom label lint")
    ap.add_argument("source", help="WaveJSON source file")
    ap.add_argument("--svg", help="rendered SVG to geometry-check")
    args = ap.parse_args()
    try:
        doc = load_wavejson(args.source)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: cannot parse {args.source}: {e}")
        return 2
    errors, warnings = lint_source(doc)
    if args.svg:
        try:
            errors += lint_svg(args.svg)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR: cannot parse {args.svg}: {e}")
            return 2
    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASS: 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
