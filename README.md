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

- **[eagle-library-agent](skills/productivity/eagle-library-agent/SKILL.md)** — 操作 Eagle 素材资源库（.library 格式）：搜索素材、统计概览、文件夹树、导出清单。支持小火人共创互利资源库和问尔美术库。
- **[video-to-wiki-lesson](skills/productivity/video-to-wiki-lesson/SKILL.md)** — 将视频课程逐节转化为图文并茂的 Obsidian LLM Wiki 笔记：字幕处理、关键帧截图、Section 级图文文章编写、从字幕提取知识点生成学习资料（摘要/测验/词汇表）。适用于大课程批量导入（6-Phase 流程）和已有字幕的内容学习。

### Health

Health and wellness tools.

<!-- Add skills here -->

### Game Dev

Game development workflows for Unity, Blender, and related tools.

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
