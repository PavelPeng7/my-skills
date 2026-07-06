# 🛠️ My Skills

A personal library of installable skills for AI coding agents — compatible with **Codex CLI**, **Claude Code**, and **Hermes Agent**.

Each skill is a `SKILL.md` file that gives the agent new capabilities: workflows, conventions, domain knowledge, and prompts.

## Categories

### AIGC

AI-generated content tools for image, video, and creative workflows.

- **[ui-cutout-splitter](skills/aigc/ui-cutout-splitter/SKILL.md)** — Remove chroma-key backgrounds and split UI sheets into reusable sprites. Supports green-screen / magenta removal, connected-component splitting, semantic renaming, and Unity-ready exports.

### Engineering

Software engineering workflows for code review, planning, testing, and more.

<!-- Add skills here -->

### Productivity

General workflow tools and productivity boosters.

- **[eagle-library-skill](skills/productivity/eagle-library-skill/SKILL.md)** — 操作 Eagle 素材资源库（.library 格式）：搜索素材、统计概览、文件夹树、导出清单。支持多个 Eagle 素材库。
- **[video-to-article](skills/productivity/video-to-article/SKILL.md)** — Turn a video URL/file or subtitle file into article-style notes, subtitle study materials, or batch course imports. Covers download, transcription, screenshot planning, Obsidian/Markdown note generation, and large-course ingestion with `yt-dlp`, `ffmpeg`, and `faster-whisper`.
- **[card-note](skills/productivity/card-note/SKILL.md)** — 将原始想法、阅读摘录、闪念笔记转化为原子化的 Zettelkasten 卡片笔记。支持分类输入、强制原子化、搜索邻近笔记、双向链接，适合 Obsidian 知识库写作。

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
