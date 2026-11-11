# Validating session notes

## Mechanical checks

Requires Python 3.10+ and PyYAML 6.x (`python3 -m pip install 'PyYAML>=6,<7'`, preferably in a virtual environment).

```sh
python3 skills/session-notes/validate_notes.py /path/to/project/notes
python3 -m unittest discover -s skills/session-notes -p 'test_*.py'
```

The validator is read-only. It exits nonzero for missing/invalid required metadata, duplicate keys, oversized frontmatter or summary/next fields, invalid dates/statuses/tags, broken local inline links or metadata paths, and index handoffs without visible inline links. Date-only legacy timestamps are allowed; precise timestamps require offsets. It does not fetch external links. Fenced examples are excluded from link checks.

Scope limits: not a complete Markdown parser (reference-style links and HTML links are not checked), no fragment-anchor validation, and no verification of evidence truth, secrets, legal correctness, historical preservation, natural-language section content or assistant behavior. Apply to actual note directories, not arbitrary project documentation. A passing result is not a claim that an agent followed the skill.

## Behavioral smoke scenarios

Run these with synthetic material in a disposable project and a fresh agent that has loaded the skill. Inspect file changes and the transcript; do not use private project data. These are manual acceptance scenarios, not automated model evaluations.

1. **Start only:** Request `notes start example`. Expect a fresh session note and index link, but no experiment or implementation. Repeat in the same conversation: expect reuse, not another note.
2. **Proactive saving:** Ask the agent to perform a small local experiment and report its result, without asking it to save notes. Expect invocation recorded before execution, final checkpoint and handoff saved before the final answer. Record whether the ordering is visible in the transcript.
3. **Current state versus history:** Have a run fail, then fix it and finish. Expect the failure retained in dated history, current state showing completion, and next action consistent with frontmatter.
4. **One authoritative record:** Request a single preregistered experiment. Expect a standalone experiment note containing protocol/commands/hashes/results; the session note links to it rather than copying those tables and hashes.
5. **Verifier amendment:** Introduce a verifier schema mismatch against frozen synthetic output. Expect original failure/freeze/output preserved, a separately hashed amendment before rescoring, and disclosure of any scores already inspected. A changed objective must become a new experiment version, not a verifier-only correction.
6. **Restart and concurrency:** Start a fresh conversation using only the notes. Expect it to find the next action and existing evidence without relying on chat IDs or rerunning completed experiments. Include a second active handoff: expect its link and files to remain intact.
7. **Explicit stop:** Request `notes stop`. Expect final state and links saved, pending work accurately paused/blocked, and no unrelated processes stopped or automatic commit/push.

For each scenario record pass/fail, observed file paths, missing behavior and whether verification was mechanical or transcript-based. Do not describe an unexecuted scenario as passing.
