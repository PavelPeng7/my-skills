# 🛠️ My Skills

A personal library of installable skills for AI coding agents — compatible with **Codex CLI** and **Hermes Agent**.

Each skill is a `SKILL.md` file that gives the agent new capabilities: workflows, conventions, domain knowledge, and prompts.

## Categories

### AIGC

AI-generated content tools for image, video, and creative workflows.

<!-- Add skills here -->

### Engineering

Software engineering workflows for code review, planning, testing, and more.

<!-- Add skills here -->

### Productivity

General workflow tools and productivity boosters.

<!-- Add skills here -->

### Health

Health and wellness tools.

<!-- Add skills here -->

### Game Dev

Game development workflows for Unity, Blender, and related tools.

<!-- Add skills here -->

## Installing a Skill

### For Hermes Agent

```bash
# Clone the repo
git clone https://github.com/PavelPeng7/my-skills.git
# Skills are auto-discovered by Hermes Agent from the skills/ directory
# Or symlink a skill:
# ln -s $(pwd)/skills/<category>/<skill-name> ~/.hermes/skills/<skill-name>
```

### For Codex CLI

See [Codex CLI skills documentation](https://github.com/openai/codex/blob/main/docs/skills.md).

## License

MIT
