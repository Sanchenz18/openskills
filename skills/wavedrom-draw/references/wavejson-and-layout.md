# WaveJSON syntax and layout rules

Read this before authoring or revising a WaveJSON source. The syntax part is a compact summary of the official WaveDrom format; the layout part is the binding quality contract for this skill.

## Syntax summary

A diagram is a JSON object with a `signal` array, an optional `edge` array, and an optional `config` object.

### Wave characters (one character per time slot)

| Char | Meaning |
| --- | --- |
| `p` / `n` | clock, positive / negative edge (with tick marks) |
| `P` / `N` | clock without tick marks |
| `0` / `1` | low / high level |
| `x` | unknown or don't care |
| `z` | high impedance |
| `.` | continue the previous state |
| `=` | data box, label taken from the signal's `data` list in order |
| `2`–`9` | data box with a color group, label also from `data` |
| `\|` | gap (break in the time axis) |
| `<...>` | sub-cycle group: the enclosed characters share one slot |

A data state continues through following `.` characters, so `=..` is one data box three slots wide. Data labels are consumed in order, one per data box, so the `data` list length must equal the number of data boxes.

### Signal fields

- `name`: the row label. Keep it to one or two words.
- `wave`: the wave string.
- `data`: a string or a list of strings, the labels for the data boxes.
- `node`: a string parallel to `wave`; each letter marks a named point in time that edges can reference (for example `".a..b"`). Use single letters.
- `phase` and `period`: shift the row in time; use only when the contract needs it.
- Group rows with a nested array whose first element is the group title: `["Group", {...}, {...}]`. Add `{}` as an element for a spacer row.

### Edges

Each edge is a string `"<from><arrow><to> <optional text>"`, for example `"a->b"` or `"a~>b wait"`. Arrow forms: `->` straight, `~>` curved, `-|>` and similar for elbow variants; `>` may be replaced by other end markers per the official syntax. The optional text is rendered along the arrow — it is the single largest source of label collisions, which is why the layout rules below ration it strictly.

### Config

- `config.hscale`: horizontal stretch, integer, default 1. One slot is about 20 units wide at hscale 1.
- `config.skin`: `"default"` or `"narrow"`.
- `head` / `foot`: optional `text` and `tick` fields for a title row or footer.

## Layout rules (binding)

Display width counts a CJK or full-width character as 2 units and any other character as 1 unit.

1. **Edge text budget.** Edge text is at most 12 units and at most 2 words. Prefer no edge text: put a node letter at each end and explain the relationship in the numbered notes below the figure. Long causal explanations never belong on an arrow.
2. **Data label fit.** A data label must fit its segment: budget ≈ 2.8 units per slot times `hscale`. If it does not fit, shorten the label (abbreviate, drop qualifiers), lengthen the segment (let the data state run over more slots with `.`), or raise `hscale`. Never accept a label that touches the segment's edges.
3. **hscale floor.** When any data label exceeds 6 units, set `config.hscale` to at least 2.
4. **One scenario per diagram.** If two scenarios share a figure, split it. A figure wider than about 14 slots with dense labels is a split candidate.
5. **Short names.** Signal names are one or two words; put instance qualifiers and conditions in the notes.
6. **Notes pattern.** Explanations removed from the figure go into a numbered list placed directly below the figure in the document, keyed by the node letters or data labels they explain, for example: “1. a→b: I1 waits at the queue head until I2 has issued (head-of-line wait).” The figure itself carries only the markers.
7. **Node hygiene.** Every letter referenced by an edge exists in some `node` string, and every defined node that an explanation depends on is referenced or listed in the notes.

## Worked example

Before (edge text collides with the arrow and the neighbouring box):

```json
{ "signal": [
  {"name": "clk", "wave": "p........."},
  {"name": "I1 issue", "wave": "x=.x......", "data": ["I1: T3"], "node": ".a........"},
  {"name": "I2 issue", "wave": "x.=.x.....", "data": ["I2: DW"], "node": "..b......."},
  {"name": "I3 commit", "wave": "x...=.x...", "data": ["I3: WB"], "node": "....c....."}
],
 "edge": ["a~>b I1: T3 HOL wait", "b->c commit"],
 "config": {"hscale": 1}
}
```

After (short labels, hscale 2, no edge text; the explanation moves to the notes):

```json
{ "signal": [
  {"name": "clk", "wave": "p........."},
  {"name": "I1", "wave": "x=..x.....", "data": ["T3"], "node": ".a........"},
  {"name": "I2", "wave": "x.=.x.....", "data": ["DW"], "node": "..b......."},
  {"name": "I3", "wave": "x...=..x..", "data": ["WB"], "node": "....c....."}
],
 "edge": ["a~>b", "b->c"],
 "config": {"hscale": 2}
}
```

Notes below the figure:

1. a→b: I1 (T3 load) waits at the head of the issue queue until I2 has issued — head-of-line wait.
2. b→c: I3 commits once its writeback data is in place.
