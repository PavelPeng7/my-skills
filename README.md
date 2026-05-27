# 🛠️ My Skills

A personal library of installable skills for AI coding agents — compatible with **Codex CLI**, **Claude Code**, and **Hermes Agent**.

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

### For Codex CLI / Claude Code (via NPX — recommended)

Install one skill at a time with a single command:

```bash
npx skills add https://github.com/PavelPeng7/my-skills/blob/main/skills/<category>/<skill-name>/ -y -g
```

For example, to install a skill named `example-skill` in the `productivity` category:

```bash
npx skills add https://github.com/PavelPeng7/my-skills/blob/main/skills/productivity/example-skill/ -y -g
```

**Why NPX?**
- One command, no manual copying or symlinking
- Installs only the skill you need (no need to clone the whole repo)
- Auto-detects the correct agent config directory
- Supports version pinning via commit/tag in the URL

### For Hermes Agent

Skills are auto-discovered from the cloned directory:

```bash
# Clone the repo (one-time)
git clone https://github.com/PavelPeng7/my-skills.git
```

Hermes Agent automatically scans for `skills/` directories. Alternatively, symlink individual skills:

```bash
# Windows (admin shell)
# mklink /J "%USERPROFILE%\AppData\Local\hermes\skills\<skill-name>" "<repo-path>\skills\<category>\<skill-name>"

# Linux / macOS
# ln -s $(pwd)/skills/<category>/<skill-name> ~/.local/share/hermes/skills/<skill-name>
```

## License

MIT
