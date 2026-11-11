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

The repository is a Nix flake. Each skill is a package, `default` holds all of
them, and a Home Manager module links them into the user-level skill
directories:

```nix
# flake.nix
inputs.agent-skills = {
  url = "git+ssh://git@github.com/FactusConsulting/agent-skills";
  inputs.nixpkgs.follows = "nixpkgs";
};

# a Home Manager module
imports = [ inputs.agent-skills.homeManagerModules.default ];
programs.agent-skills.enable = true;
# programs.agent-skills.skills = [ "session-notes" ];   # default: all
```

Each skill becomes a link `~/.agents/skills/<name>` (Pi, Codex, Copilot,
Cursor) and `~/.claude/skills/<name>` (Claude Code) into the Nix store. Only
the skills from here are linked; vendor-managed skills beside them are left
alone. `devsetup` consumes the flake this way and moves its lock forward on
its own schedule, so a merged change here reaches every machine on its next
profile update.

`nix flake check` validates every skill's frontmatter and runs the
session-notes validator's tests. `nix build .#<skill>` builds one skill.

To try an unmerged change on a machine before it lands, build the consumer
against the checkout: `--override-input agent-skills path:$HOME/source/agent-skills`.

Without Nix (Windows), symlink the checkout instead:

```bash
mkdir -p ~/.agents/skills ~/.claude/skills
for s in ~/source/agent-skills/skills/*/; do
  n=$(basename "$s")
  ln -sfn "$s" ~/.agents/skills/"$n"
  ln -sfn "$s" ~/.claude/skills/"$n"
done
```

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
