This file provides guidance to agents when working with code in this repository.

## Repository Purpose

This is a personal library of **skills** — installable prompt extensions that give AI coding agents new capabilities. Each skill is a `SKILL.md` file containing a YAML frontmatter block and a detailed instruction body.

Compatible with: Codex CLI, Hermes Agent, and other AI coding agents that support skills.

## Structure

```
skills/
  <category>/
    <skill-name>/
      SKILL.md
```

Current categories: `aigc`, `engineering`, `productivity`, `health`, `game-dev`

## Skill Format

Every `SKILL.md` must start with a YAML frontmatter block:

```yaml
---
name: <kebab-case-slug>
description: >
  One or more sentences describing what the skill does and when it triggers.
  Include explicit TRIGGER conditions to help the model route correctly.
---
```

The body after the frontmatter is the full instruction set the model follows when the skill is invoked.

## Skill Reference Maintenance

Whenever adding or modifying a skill, update both reference lists:
- Root `README.md`
- Category README at `skills/{category_name}/README.md`

Keep each reference's link, name, and short description aligned with the skill's current behavior.
