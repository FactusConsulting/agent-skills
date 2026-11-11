---
name: d2-diagrams
description: Create, edit, validate, and render D2 diagrams — .d2 files and fenced d2 blocks in documentation. Use when asked for a D2 diagram, when editing or rendering existing .d2 files, or when a diagram needs nested containers, precise layout, or SVG/PNG/ASCII output that Mermaid handles poorly.
---

> **Skill loaded:** when you load this skill, announce it to the user as `📐 d2-diagrams`.

# D2 diagrams

## Workflow

1. Check the syntax for anything beyond shapes, connections, and containers
   — see References. Do not guess D2 syntax; it is not Mermaid or Graphviz.
2. Write the diagram as a `.d2` file next to the docs it belongs to. A
   fenced ` ```d2 ` block only where the renderer supports it — GitHub does
   not render D2, so commit the rendered SVG alongside for GitHub docs.
3. Format, then validate. Both must pass before presenting:
   ```bash
   d2 fmt diagram.d2
   d2 validate diagram.d2
   ```
   Non-zero exit means invalid; errors are `line:col: message`.
4. Render:
   ```bash
   d2 diagram.d2 diagram.svg                 # default output
   d2 diagram.d2 "${TMPDIR:-/tmp}/d.txt"     # ASCII preview for terminal/chat
   ```
   Inspect the ASCII or SVG output before presenting. If `d2` is not
   installed, say the diagram is unvalidated — do not claim it renders.

## Syntax essentials

```d2
direction: right                      # down (default) | right | left | up
user: User {shape: person}            # key: label {attributes}
api: API {                            # container: nested map
  db: Postgres {shape: cylinder}
}
user -> api.db: query                 # connect by dotted path; label after ':'
api.db -> user: rows {style.stroke-dash: 3}
```

- Keys are IDs; labels are display text. Reference nested shapes by dotted
  path (`api.db`); `_` refers to the parent container.
- Connections: `->`, `<-`, `<->`, `--`. Repeating `a -> b` creates a
  second edge, not a no-op.
- Multi-board docs (`layers`, `scenarios`, `steps`) render to multiple
  outputs; `--target` picks one.

## Layout & rendering

- Engines bundled: `dagre` (default), `elk` (`--layout=elk`, better for
  dense or orthogonal diagrams). `tala` is commercial — do not assume it.
- `--theme=N` / `--dark-theme=N` choose themes; `--sketch` for hand-drawn
  look; `--pad` controls margin.
- Prefer layout hints (`direction`, containers, `elk`) over hand-placed
  `near`/coordinates.

## References

- Language tour: https://d2lang.com/tour/intro
- Shapes catalog: https://d2lang.com/tour/shapes
- Playground: https://play.d2lang.com

## Rules

1. Never present or commit D2 that failed `d2 validate`.
2. Keep the `.d2` source in version control; rendered images are
   derived artifacts committed next to it, never instead of it.
3. Run `d2 fmt` before committing so diffs stay minimal.
4. Prefer the smallest diagram that answers the question; one diagram per
   concern beats a mega-diagram.
