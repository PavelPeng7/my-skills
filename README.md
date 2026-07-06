# 🛠️ My Skills

一个面向 AI 编程代理的可安装 skills 个人仓库，兼容 **Codex CLI**、**Claude Code** 和 **Hermes Agent**。

每个 skill 都是一个 `SKILL.md` 文件，用来给代理补充新的工作流、约定、领域知识和提示词能力。

## Categories

### AIGC

面向图像、视频与创意生产流程的 AIGC 工具类 skills。

- **[ui-cutout-splitter](skills/aigc/ui-cutout-splitter/SKILL.md)** — 去除绿幕 / 品红底等色键背景，并将整张 UI 图拆分为可复用精灵。支持连通域切分、语义重命名，以及适合 Unity 的导出流程。

### Engineering

软件工程类工作流 skills，用于代码评审、规划、测试等任务。

<!-- Add skills here -->

### Productivity

通用工作流与效率增强类 skills。

- **[eagle-library-skill](skills/productivity/eagle-library-skill/SKILL.md)** — 操作 Eagle 素材资源库（.library 格式）：搜索素材、统计概览、文件夹树、导出清单。支持多个 Eagle 素材库。
- **[video-to-article](skills/productivity/video-to-article/SKILL.md)** — 将视频链接 / 本地视频 / 字幕文件转成图文笔记、字幕学习材料或批量课程导入内容。覆盖下载、转录、截图规划、Obsidian/Markdown 笔记生成，以及基于 `yt-dlp`、`ffmpeg`、`faster-whisper` 的大课程导入流程。
- **[card-note](skills/productivity/card-note/SKILL.md)** — 将原始想法、阅读摘录、闪念笔记转化为原子化的 Zettelkasten 卡片笔记。支持分类输入、强制原子化、搜索邻近笔记、双向链接，适合 Obsidian 知识库写作。

### Health

健康与生活管理相关 skills。

<!-- Add skills here -->

### Game Dev

面向 Unity、Blender 及相关工具链的游戏开发工作流 skills。

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
