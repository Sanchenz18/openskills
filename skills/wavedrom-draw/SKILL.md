---
name: wavedrom-draw
description: Author, revise, validate, and render WaveDrom timing diagrams (WaveJSON to SVG/PNG) for digital hardware documentation — clocks, buses, valid/ready handshakes, pipeline, cache, and FSM timing. Enforces short on-figure labels with longer explanations moved to numbered notes below the figure, renders with the Python wavedrom engine, and gates delivery on a source lint plus an SVG geometry check that flags overlapping or overflowing text. Use whenever a task needs a timing diagram created or an existing diagram's labels fixed; do not use for analog waveforms, software sequence diagrams, or flowcharts.
---

# WaveDrom Draw

Turn a timing description into a WaveJSON source plus a rendered SVG whose labels never overlap, overflow their boxes, or run off the canvas. Keep the source and the rendered figure as a pair with the same basename (`<name>.json` and `<name>.svg`); regenerate the SVG from the source after every edit instead of editing the SVG by hand.

## Workflow

1. **Build a timing contract first.** Identify the clock domain and time unit, the active edge, each signal's initial state and active level, the ordered events, and the final state. Treat a supplied specification, RTL, trace, or timing table as authoritative; state any assumption that changes the timing semantics.
2. **Read the reference before authoring.** Read [references/wavejson-and-layout.md](references/wavejson-and-layout.md) for the WaveJSON syntax summary and the layout rules with their numeric limits.
3. **Author the WaveJSON under the layout rules.** Keep one diagram to one scenario. Put short markers on the figure and move every longer explanation into a numbered notes list that belongs below the figure in the document; return that notes list with the diagram.
4. **Lint the source.** Run `python3 scripts/lint.py <name>.json`. Fix every error it reports (label too long for its segment, edge text over budget, edge pointing at a missing node) and re-run until it passes. Do not weaken the limits to make a crowded diagram pass — shorten labels, raise `hscale`, or split the diagram instead.
5. **Render.** Run `python3 scripts/render.py <name>.json --svg <name>.svg --png <name>.png`. If it reports a missing package, create the environment it names and re-run; do not install packages system-wide.
6. **Check the rendered geometry.** Run `python3 scripts/lint.py <name>.json --svg <name>.svg`. It estimates every text element's box in the SVG and fails on text overlapping other text, text spilling onto unrelated boxes, and text outside the canvas. Fix the source and re-render until it passes.
7. **Look at the PNG.** Open `<name>.png` and inspect it: labels readable, arrows clear of text, nothing clipped. If your environment cannot display images, still deliver the PNG path and state plainly that the visual pass is outstanding — never claim a diagram looks right when only the lints have passed.
8. **Deliver the set.** Return the JSON source, the SVG, the PNG, and the numbered notes list, plus any assumptions from step 1. In a document, place the notes list directly below the figure and refer to markers by number.

## Layout rules (summary)

- Edge (arrow) text: at most 12 display-width units and at most 2 words; prefer no edge text at all and explain the arrow in the notes. Display width counts a CJK or full-width character as 2 and any other character as 1.
- Data labels must fit the wave segment they sit on; the lint enforces the fit from the segment length and `hscale`. Shorten the label or lengthen the segment — never shrink the font.
- Use `config.hscale` of at least 2 whenever any data label exceeds 6 display-width units.
- Signal names stay short (one or two words); put qualifiers in the notes.
- Node markers are single letters; an edge may only reference nodes that exist.
- Split a diagram that needs more than about 10 slots of dense annotation into two diagrams, one per scenario.

## Dependencies

- Python 3.10 or newer.
- `scripts/render.py` needs the `wavedrom` package to render and `cairosvg` for the PNG preview. `scripts/lint.py` uses only the standard library.
- When the packages are missing, create a virtual environment once and call the scripts with its interpreter:

```text
python3 -m venv ~/.cache/wavedrom-draw/venv
~/.cache/wavedrom-draw/venv/bin/pip install wavedrom cairosvg
~/.cache/wavedrom-draw/venv/bin/python scripts/lint.py <name>.json --svg <name>.svg
```
