---
name: mermaid-diagrams
description: Create, edit, and validate Mermaid diagrams — .mmd files and fenced mermaid blocks in documentation. Use when asked to draw, generate, edit, or visualize any diagram (flowchart, sequence, architecture, ER, state, gitgraph), or when a doc change adds or modifies Mermaid content.
---

# Mermaid diagrams

## Signal that you loaded this

Begin your first reply after loading this skill with `🎯 mermaid-diagrams`
on its own line. Emit it once per session, when you load the skill — not on
every subsequent message.

## Workflow

1. Pick the diagram type. If the syntax is unfamiliar, look it up before
   writing — see Syntax references below. Do not guess Mermaid syntax.
2. Write the diagram:
   - Standalone diagram → a `.mmd` file next to the docs it belongs to.
   - Diagram that is part of a narrative → a fenced ` ```mermaid ` block in
     the Markdown file.
3. **Validate before presenting.** Never return unvalidated Mermaid syntax —
   a single unbalanced bracket renders as an error blob and silently breaks
   GitHub previews. Use whichever validator your harness has (below).
4. Preview when a preview mechanism is available; otherwise state that the
   diagram was validated but not rendered.

## Validation & preview by harness

- **VS Code with the Mermaid extension** (Copilot, Cursor): use the LM tools
  `mermaid-diagram-validator` (before presenting), `mermaid-diagram-preview`
  (after generating), and `get-syntax-docs-mermaid` (unfamiliar diagram type).
- **Any shell, no extension**:
  ```bash
  npx -y @mermaid-js/mermaid-cli -i diagram.mmd -o "${TMPDIR:-/tmp}/diagram.svg"
  ```
  Non-zero exit means invalid syntax; the error names the offending line.
  This renders via a headless browser — if it cannot run (no browser, no
  network), fall back to the manual checklist below and say so.
- **Manual checklist** (last resort): first line is a valid diagram keyword;
  every node has an ID; arrows are real tokens (`-->`, `---`, `-.->`, `==>`,
  `<-->`); brackets, quotes, and `subgraph`/`end` pairs are balanced; labels
  containing `()` or `|` are quoted with `"`.

## Syntax references

- Per-type syntax docs: https://mermaid.js.org/syntax/flowchart.html (and the
  sibling pages for each type).
- Interactive editor for quick iteration: https://mermaid.live

## Rules

1. Never present or commit unvalidated Mermaid.
2. Keep diagrams in version control as text (`.mmd` / fenced blocks), never
   as committed images only. If an image is also wanted, render it to the
   same directory.
3. A diagram managed by the Mermaid GitHub Sync app has a frontmatter `id:`
   block — do not hand-rewrite those; changes go through the sync workflow.
4. AI repair features (VS Code **Mermaid: Repair Diagram**) spend Mermaid AI
   credits — tell the user before invoking them.
5. Prefer the smallest diagram that answers the question; one diagram per
   concern beats a mega-diagram.
