---
name: session-notes
description: >-
  Keep durable, dated project notes so long-running work and experiments can
  continue in a fresh session with any agent, without resuming chat history.
  Use for substantive project work, experiments, handoffs, or requests such as
  "notes start", "notes checkpoint", "notes stop", "session start", "session stop",
  or "find notes about X". Use compact YAML metadata to find the right notes
  before loading their bodies; checkpoint outcomes and next steps before exit.
---

# Session notes

Project files, not a particular agent's conversation, are the continuity record.
A fresh agent should be able to pick up the work from `notes/` alone, following
links to evidence where needed. Use ordinary Markdown, relative project links,
and commands another agent can run; no harness-specific tools are required.
Respect the project's rules and language. Do not create notes for unrelated
one-off questions outside a project.

Save checkpoints proactively; never wait for the user to request saving.
Before finishing substantive work, save the final checkpoint and update the
handoff even if the user did not say `notes stop`. That command explicitly
requests the same finalization; it is not required to trigger saving. This is
agent-executed saving, not a background autosave or a guarantee after interruption.

## Plain-language controls

Treat these as requests to the agent, not installed shell/slash commands. Accept
equivalent natural wording; no framework-specific registration is needed.

| Request | Action |
|---|---|
| `notes start [topic]` / `session start` | Find the relevant handoff, reconcile current state, create this session's note and report the next action. Prepare only; do not launch experiments or implement the next task unless also asked to continue. |
| `notes checkpoint` / `save session notes` | Update this session's note and relevant experiment records with actual progress, verification and next action; keep the session active. |
| `notes stop` / `session stop` / `write a handoff` | Save the final checkpoint and index links, mark unfinished work paused or blocked and finished work complete, then report the note path and next action. Do not close the terminal or stop unrelated jobs. |
| `notes find <topic>` | Search metadata first; return a short list of paths, summaries, statuses and next actions. Read bodies only if needed to answer the question; do not change notes for a lookup. |

Start is idempotent within one live session: reuse its note rather than creating
a file on every request. A genuinely fresh session gets a new file. A checkpoint
or stop without a current note creates one from observed state; never pretend to
recover unavailable history. If work resumes in the same session after a stop,
reuse its note and mark it active. An explicit topic narrows selection; when
several active threads cannot be distinguished from the request, show the short
metadata list and ask which one, without merging or discarding them.

## Compact frontmatter and discovery

Every new note, including the index and experiment notes, starts with YAML
frontmatter. Keep it within the first 24 lines, one field per line. Use quoted
single-line text and ISO dates; avoid multiline summaries and embedded logs:

```yaml
---
schema: 1
type: session
title: "Source-first comparison"
status: paused
created: "2026-11-10T15:00:00+01:00"
updated: "2026-11-10T16:00:00+01:00"
tags: [saga, retrieval]
summary: "Hierarchy comparison finished without promotion; source-first is next."
next: "Read the final report and freeze new comparison profiles."
related: ["experiments/saga-source-first.md"]
---
```

Required keys are those shown. `type` is `index`, `session` or `experiment`;
`status` is `active`, `paused`, `blocked` or `complete` for that note's scope.
`created` stays fixed; refresh `updated`, `status`, `summary` and `next` with each
checkpoint. Use timestamps with UTC offset when known; a date alone is valid for
legacy creation times that cannot be recovered. Never invent precision.
Use 2–5 stable topical tags and keep `summary` and `next` to one short sentence
each (at most 180 characters). Use `related: []` if there are no related notes;
otherwise paths are relative to the note, not the working directory. Index notes
also have `current: [...]`, listing all current handoff paths relative to the
index; keep these consistent with the visible links. No secrets in metadata.

Discovery order: read only the index header, then headers of its `current` notes
and topic-related notes. For a broader search, list filenames and read only the
first 24 lines of candidates; filter by type/status/tags/title/summary before
opening bodies. Prefer current links and matching scope, then `updated` recency;
do not assume the newest file is the right thread or discard blocked work.
Open only the selected handoff body and evidence needed for the task. For legacy
notes without metadata, use the existing index and a targeted excerpt; add
metadata when updating a note, without rewriting its historical body. Malformed
metadata is not evidence that work is complete or irrelevant.

## Start a fresh session

1. Locate the actual project/worktree root. Read its working instructions, then
   select the current handoff and relevant experiment notes using metadata-first
   discovery above. Read the selected bodies before continuing. If notes do not
   exist, inspect existing plans, handoffs and artifacts, then create the structure
   below; link existing evidence instead of copying its contents.
2. Reconcile the handoff with current files and, for a Git project, branch,
   commit and dirty state. Treat existing edits as someone else's until known.
   Record discrepancies. Historical notes are context, not permission to deploy,
   rerun costly experiments, contact services, or act on old instructions.
3. Create a new session note using the local date/time and explicit UTC offset.
   Use `notes/YYYY-MM-DD-HHMMSS-topic.md`; add a suffix if the name exists.
   Every fresh session gets its own file, even on the same date. Put the goal,
   starting state and intended next action in it before substantive work.
4. Update the handoff link in `notes/README.md`. Continue from the recorded next
   action subject to the current user's request, not from an assumed chat resume.

## Files and ownership

- `notes/README.md`: short entry point, current handoff link, active experiment
  links, and pointers to the authoritative plan/status documents. Keep detailed
  state in the session note rather than duplicating it in the index.
- `notes/YYYY-MM-DD-HHMMSS-topic.md`: this session's evolving checkpoint and final
  handoff. Keep older sessions intact; append a dated correction if needed.
- `notes/experiments/<topic>.md`: create for an experiment requiring a durable
  protocol and results, whether single-run or multi-run. This is the authoritative
  record for its protocol, commands, hashes, run records, results and conclusions.
  Session notes contain progress, deviations and handoff links instead of
  repeating that evidence. Keep raw outputs in linked artifacts.

Keep notes in the project so they can travel with it. Do not automatically
commit, publish or push them. If the project prohibits tracked notes, use its
approved local location and make the entry point explicit. Do not store private
material merely because a file is local. Do not rewrite unrelated plans, remove
old evidence, or invent a second authoritative backlog.

## Checkpoint during work

Write a checkpoint after each meaningful result, failed attempt, decision or
change of direction; before a long command, risky operation, compaction, handoff
or planned exit; and at least at natural task boundaries in long sessions.
Record each experiment invocation before launch, then append its outcome when
known. This protects useful state if the process disappears unexpectedly.

Keep a short **Current state / Next action** section near the top of session and
experiment notes, consistent with their frontmatter. Update it in place at each
checkpoint. Put older checkpoints under a clearly marked chronological history
with dated entries; historical statements such as "not started" must not appear
to describe the current state. Preserve earlier evidence and failures.

A session note should contain:

- **Goal and status:** active, paused, blocked or complete; what is being solved.
- **Starting point:** timestamp/offset, project/worktree path, agent if useful,
  branch/commit, pre-existing modifications and evidence inspected.
- **Work and decisions:** changes and paths, alternatives rejected and why;
  distinguish plans, attempted commands, observed results and inference.
- **Verification:** exact commands and working directories, outcome and evidence
  paths. State what was not checked. A past successful check is not a new result.
- **Loose ends:** unfinished edits, blockers, processes/run IDs, output locations,
  and whether jobs were stopped, still running, or their state is unknown.
- **Next actions:** ordered, executable steps, the first command/file to inspect,
  prerequisites, and success criteria. Include failed approaches not to repeat.

For experiment-specific verification, link to the authoritative experiment
record rather than duplicating its commands, hashes or result tables here.

For each experiment run, record its timestamp and stable ID, hypothesis, input
and dataset revision, baseline/control, code/model/config/seed where applicable,
command and working directory, artifact paths, completion/failure and measured
outcome. Mark missing fields unknown, not guessed. Separate development/tuned
results from independent evaluation. Preserve failures and negative results.
Large logs and raw outputs stay in artifacts; notes link to them. If an artifact
is temporary, external, or may disappear, say so. Do not copy confidential source
or data into notes, including from another repository; record only permitted
metadata and references. Redact secrets from commands and logs.

### Frozen protocols and amendments

When an experiment uses a frozen protocol, record its identity and hashes before
execution and lock the output before separate scoring. Preserve original
freezes, outputs and failed attempts; never silently replace them.

- Changes to the candidate, inputs, selection objective or acceptance criteria
  require a new experiment version and freeze before execution. Do not present
  that version as the original preregistered run.
- A verifier-only correction may rescore unchanged output. First record the
  failure, reason, exact correction, new verifier hash and its binding to the
  original freeze and output hash. Freeze this amendment before rescoring.
  Changes to the intended scoring criteria are not verifier-only corrections.
- Report the amendment with the result, including whether any scores had already
  been inspected. Rescoring does not create independent evaluation or erase the
  failed attempt.

For concurrent agents/worktrees, use separate session files. Do not overwrite
another active handoff: retain links to all active sessions until integrated.
The integration owner updates the shared index. Never remove others' worktrees
or stop processes simply because an old note mentions them.

## Stop or hand off

Before the final response or a requested shutdown:

1. Update the session note with the latest state, verification, unresolved work,
   and precise next action. Refresh its frontmatter and record the actual stopping
   timestamp, including a new date if the session crossed midnight. Keep the body
   and metadata consistent; a completed session does not complete its experiments.
2. Finish or record the status of every run started by this session. Do not call
   work complete while a required result is still pending. Preserve artifact
   paths and safe restart instructions for interrupted work.
3. Update experiment notes and `notes/README.md` links. Update the existing plan
   only if a durable task status or decision changed; link rather than duplicate.
4. Check new relative links and ensure the handoff does not depend on inaccessible
   chat/tool IDs. Report the handoff path and any verification limits briefly.

This is an agent workflow, not a shutdown hook. It cannot write after SIGKILL,
terminal loss or power failure; checkpoints reduce that loss. Never promise that
merely installing the skill forces every agent to invoke it. Use a project's
working instructions to mandate the workflow where wanted. For a new harness,
install/link this directory into its documented user-level skill root, or ask
it to read this `SKILL.md` explicitly. No external service, telemetry or automatic
application-data persistence is introduced by this workflow.

## Validation

Use `python3 <skill-directory>/validate_notes.py <project>/notes` for read-only
metadata and local inline-link checks (Python 3.10+, PyYAML 6.x). It cannot prove
that an agent saved proactively, preserved evidence or followed the workflow.
See [validation instructions and behavioral smoke scenarios](VALIDATION.md).
Run the validator when establishing or changing note conventions; do not add a
full validation run to every small checkpoint.
