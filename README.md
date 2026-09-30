f

# agent-skills

Shared agent skills for the Factus homelab estate — the cross-repo tier of
skill storage. Skills here apply to any repo a coding agent opens, so they
are installed **at user level**, not vendored into individual repos.

## Layout

```
skills/<name>/SKILL.md    # one skill per directory, SKILL.md is the entry point
```

## Installation

Clone once, symlink into the user-level skill directories each harness reads:

```bash
git clone git@github.com:FactusConsulting/agent-skills.git ~/source/agent-skills
mkdir -p ~/.agents/skills ~/.claude/skills
for s in ~/source/agent-skills/skills/*/; do
  n=$(basename "$s")
  ln -sfn "$s" ~/.agents/skills/"$n"   # Copilot / Codex / Cursor
  ln -sfn "$s" ~/.claude/skills/"$n"   # Claude Code
done
```

`wslsetup` runs this on a new workstation. Re-running after a `git pull` is
a no-op — the symlinks follow the checkout.

## Which tier a skill belongs to

| Skill is about…                                       | Lives in                                                                                                               |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| One repo's code (playbooks, stacks, manifests)         | That repo's`.agents/skills/`, symlinked from its `.claude/skills/`                                                 |
| Any repo, any project (diagrams, docs, tooling habits) | Here                                                                                                                   |
| Agents deployed on the openclaw fleet                  | `homelab/ansible/playbooks/openclaw/files/common-workspace/skills/` — a runtime pipeline, not a dev-machine harness |

A repo-local skill with the same name as one here wins for that repo —
that is how a repo customises a shared default.

## What belongs here

Only skills **we author**. Anything installed and updated by a vendor —
the Microsoft Azure skills pack, Context7's `find-docs`, the Hugging Face
`hf` skill, `drunk-claude` — stays vendor-managed at user level and must
not be copied or symlinked in here. Vendoring a third-party skill forks it
and silently breaks its updater; a `git pull` here would then serve a
stale copy to every machine. To adopt an upstream skill, pin it in
`wslsetup` instead.

## Conventions

- `SKILL.md` frontmatter: `name` (matches the directory) and `description`
  (says *when* to use it — harnesses match on this).
- Keep skills short; link to docs rather than restating them.
- A skill that mandates itself from an `AGENTS.md` says so there — this repo
  cannot mandate anything in other repos.
