---
name: technical-writing
description: >-
  Use before drafting or rewriting technical descriptions, documentation,
  instructions, tool descriptions, prompts, error messages or status reports.
  Ask whether the user wants Danish or English, then use asd-std100 for Danish
  or asd-ste100 for English. Triggers: technical description, technical writing,
  clear documentation, describe this system, teknisk beskrivelse, teknisk dansk.
  Not for ordinary conversation, code-only changes, creative or marketing copy.
---

# Technical writing: choose the language first

## Language gate

Before drafting or rewriting technical text, establish the output language.
This gate takes precedence over a writing skill's rewritten-text-only format.

1. If the user explicitly chose Danish or English for this writing task, use it.
   A direct request to use `asd-std100` counts as Danish; a direct request to use
   `asd-ste100` counts as English. Automatic skill selection does not count.
2. Otherwise, ask exactly one question and wait before drafting:
   **"Would you like the technical description in Danish or English?"**
   If the conversation is Danish, ask:
   **"Vil du have den tekniske beskrivelse på dansk eller engelsk?"**
3. Do not infer the output language from the input text or conversation language.
4. Reuse the user's answer for revisions of the same description. Ask again for
   a new writing task unless the user explicitly set a session-wide preference.
5. If the user requests both languages, produce both. Do not ask them to pick one.
6. If repository instructions require a different language, explain the constraint
   before writing files. Offer the requested language as a separate chat draft;
   do not silently violate repository instructions.

## Route to the writing skill

- **Danish:** Load `asd-std100/SKILL.md` from the available skill catalog.
- **English:** Load `asd-ste100/SKILL.md` from the available skill catalog.
- **Both:** Load both and apply each only to its respective language.

Resolve skills through the harness's catalog or user-level skill directory.
Do not hardcode another user's home path. Do not loop back through language
selection after an explicit choice. Pass the established choice to the writing
skill so it does not ask again.

If a required skill is missing, report its name. Do not claim to have applied it.
Devsetup installs the English skill separately from this shared library.

Once the language is established, follow the selected skill's rules and output
format. Preserve facts, uncertainty, requirements and technical identifiers.
This is an agent instruction, not a runtime hook: it operates when the agent
loads and follows the skill.
