---
name: video-to-wiki-lesson
description: 将视频课程逐节转化为图文并茂的 Obsidian LLM Wiki 笔记 — 字幕处理、关键帧截图、Section 级图文文章编写、从字幕提取知识点生成学习资料（摘要/测验/词汇表）适用于大课程批量导入（6-Phase 流程）和已有字幕的内容学习
allowed-tools: Read, Write, Terminal, File, Vision, Search
---

# 视频课程 → Obsidian 图文笔记 + 字幕学习工作流

## 核心原则（节省 Token）

1. **字幕预处理优先**：不要将原始 SRT 直接喂给文章编写 agent。先用脚本剥离时间码和序号，只传纯文本。
2. **截图引用先写，帧批量后截**：写文章时用预计算 slug 写 `![[wikilink]]`，不边写边截。ffmpeg 批量一锅端。
3. **文章密度倾斜**：Intro/总结类课程（标题含 "Intro"、"Wrap-Up"、"Overview"）1-2 句带过。实操/演示/项目类课程详细展开。
4. **并行 Section**：200+ 视频的大课程用 `delegate_task` 并行处理 Section（最多 3 个并行）。

## 单视频/独立文件/会议处理

当用户直接发一个独立视频文件（非课程系列视频），走简化流程。详见 `references/single-video-ingest.md`。

## 字幕学习模式

当用户只想从已有字幕文件中学习/提取知识点（不做课程导入），使用 `references/subtitle-study-modes.md`。支持 5 种模式：知识提取、章节摘要、测验生成、关键词汇、交互式问答。

## 大课程策略（50+ 视频 / 100+ 视频）

### 原则

**六 Phase 流程**（见 `references/large-course-ingest-workflow.md`）：

| Phase | 做什么 | Token 策略 |
|-------|--------|-----------|
| ① 目录分析 | 列出 Section 结构、视频列表 | 极低（~500 tokens） |
| ② 字幕预处理 | 批量剥离 SRT 元数据 → 纯文本 | 一次性终端脚本，零 token 消耗 |
| ③ 截图规划 | 预计算所有 slug + ffmpeg 命令 | 一次性终端脚本，零 token 消耗 |
| ④ 批量截图 | ffmpeg 批量执行 | 后台 terminal，零 token 消耗 |
| ⑤ 并行写文章 | delegate_task × 最多 3 个 Section | 每篇仅传纯文本（SRT 量的 45%） |
| ⑥ 收尾 | index.md + log + README | 极低 |

### ② 字幕预处理脚本

复用模板（见 `templates/preprocess-srt.py`）：
1. 复制到课程目录
2. 修改 `SECTIONS` 定义和 `LEVEL_DIRS` 路径
3. 运行

```python
# srt_to_text.py: 批量剥离 SRT 元数据，按 Section 分组输出纯文本
import re, os, glob

def strip_srt(srt_path):
    with open(srt_path, encoding='utf-8') as f:
        text = f.read()
    lines = text.split('\n')
    result = []
    for line in lines:
        line = line.strip()
        if re.match(r'^\d+$', line): continue
        if re.match(r'^\d{2}:\d{2}:\d{2}', line): continue
        if not line: continue
        result.append(line)
    return ' '.join(result)

# 批量处理，按 Section 输出
for section_videos in sections:
    texts = []
    for num, name in section_videos:
        srt_path = find_srt(num, name)
        texts.append(f"== Video {num}: {name} ==\n{strip_srt(srt_path)}")
    with open(f"_preprocessed/section-{slug}.txt", 'w') as f:
        f.write('\n\n'.join(texts))
```

### ③ 截图规划脚本

```python
# plan_screenshots.py: 预计算 slug + ffmpeg 命令
# 短 < 30s: 1帧 (overview)
# 中 30-120s: 2帧 (overview, detail)
# 长 > 120s: 3帧 (overview, detail, result)
# Section 级: ~12帧精选
```

### ④ 批量截图

写好 ffmpeg 命令列表到 `.sh` 文件，一次性执行：
```bash
bash _batch_screenshots.sh
```
用 `terminal(background=true, notify_on_complete=true, timeout=3600)` 运行。

### ⑤ 并行写文章

```python
delegate_task(
    goal=f"写 Level 1 Module 1 的综合图文文章",
    context=f"""
    SECTION: L1-M01 - Claude Code Basics
    包含 8 个视频，纯文本内容如下：

    {preprocessed_text}

    文章要求：
    - Intro 类视频 1-2 句带过
    - 实操类详细展开
    - 截图引用用预计算的 slug
    - 中文撰写
    """,
    toolsets=['file']
)
```

## 前置条件

- FFmpeg 已安装（检查：`ffmpeg -version`）
- 视频文件 (.mp4) 在同一目录下
- 字幕来源有两种方式：
  - **方式 A（优先）**：英文字幕文件 `.en.srt` 存在，直接读取
  - **方式 B（兜底）**：无字幕时，用 Whisper STT 从视频音频提取语音文字（见 `references/whisper-stt-batch.md`）
- Obsidian vault 路径为 `B:\GitHub\Obsadian\CourseWiki`
- 截图路径从 sources/ 目录到 assets/ 目录：`![[../../../assets/{lesson-dir}/{filename}.jpg]]`

## 哪些时刻值得截图（课程类）

- UI / 界面发生变化时（新组件渲染、布局改变）
- 代码编辑器展示代码结构时（目录树、文件内容）
- 演示操作步骤时（点击按钮、输入命令）
- 视觉效果有代表性的画面（终端输出、截图、图表）
- 作者展示文档 / 网页时

**不要截**：纯讲演无画面变化的时间段、过渡语（"Let's take a look"）、纯讲解

## 文章密度规则

| 视频类型 | 篇幅 | 截图数量 |
|---------|------|---------|
| Intro/Module 介绍 | 1-2 句 + 不截图 | 0 |
| Wrap-Up/总结 | 2-3 句概要 | 0 |
| 概念讲解（What is X?） | 半段 + 1 张说明性截图 | 1 |
| 配置/安装教程 | 一段 + 2-3 张操作截图 | 2-3 |
| 实操/演示/项目 | 详细展开 + 3-5 张截图 | 3-5 |
| 最佳实践/技巧 | 一段列表形式 | 1-2 |

## 工作流步骤（优化版）

### Phase 1: 课程结构分析
1. 遍历目录，列出所有 `.en.srt` 文件 → 建立 `{level}/{section}/{videos}` 结构
2. 按 Module 分组确定 Section 边界
3. **Output**: Section 列表

### Phase 2: 字幕预处理（终端脚本，零 token）

用脚本批量将 SRT 纯文本化：
```bash
python _preprocess_srt.py
```
输出到 `_preprocessed/` 目录，每 Section 一个 `.txt` 文件。

### Phase 3: 截图规划（终端脚本，零 token）

用脚本读取字幕 + ffmpeg 获取视频时长 → 确定每 Section 截图点：
```bash
python _plan_screenshots.py
```
输出：
- `_screenshot_plan.json` — 所有截图的时间点、slug、label
- `_batch_screenshots.sh` — 可执行的 ffmpeg 命令列表

### Phase 4: 批量截图（后台 terminal，零 token）

```bash
bash _batch_screenshots.sh
```

### Phase 5: 并行写 Section 文章（delegate_task，最少 token）

一次派发最多 3 个 Section。**Context 构建的关键规则**：

1. **明确声明截图就绪** — 用"截图已全部就绪，不要验证文件"替代"截图在 XXX 目录"
2. **提供完整的 slug→label 表** — 子代理不会自己去算 slug
3. **声明哪些视频不放截图** — Intro/Wrap-Up 类单独列出
4. **设置 density rules 表** — 不是让子代理判断，而是直接告诉它
5. **限制 toolsets=['file']** — 不给 search 工具能省大笔 token。如果必须给，在 context 中加"不要 search_files 验证截图"

```python
# ❌ 错误示范（子代理会花大量 token 去验证文件）
context = f"""
截图在 assets/claude-code-mastery/ 目录
slug 格式是 {video-name}-{label}.jpg
视频列表：...
"""

# ✅ 正确示范（子代理直接写引用，零验证）
context = f"""
截图已全部就绪，不要验证文件。直接写引用：
  ![[../../../assets/claude-code-mastery/{slug}-{label}.jpg]]

slug 表（每个 slug 都有 overview/detail/result 三张，直接使用）：
- What is X → what-is-x
- Installation → installation
- Intro M01 → intro-m01（不放截图，只有 2 帧）

密度规则：intro-m01 不放截图，其他每课 3 张截图。
"""
```

**最佳实践 vs token 消耗（本课程实测数据）：**

| Context 写法 | input token | 子代理工具调用 |
|-------------|------------|--------------|
| 只说"截图在目录" | ~214K | 15 次 search_files 验证 |
| 明确"不要验证"+slug 表 | ~22K | 仅 read_file+write_file |
| 同上+toolset 限制 | ~16K | 仅 read_file+write_file |

结论：**Phase 5 的核心优化不在文章内容，而在不让子代理做文件验证**。写死 slug 表 + 明确"不要验证"能省 90% input token。toolsets 建议只给 `['file']`，不给 search 工具。

#### 文章结构模板

```
# {Section Title}

tags: [source, claude-code-mastery, {level}]

## Summary

2-4 句话概括本节核心内容。

## Key Takeaways

- 列出 5-10 个最重要的知识点

## Full Lesson Content with Screenshots

### 1. {课程标题}

Intro 类：1-2 句带过。

---

### 2. {实操课程标题}

{详细展开}

![[../../../assets/claude-code-mastery/{screenshot-filename}.jpg]]

> *"{引用字幕原文}"*

---

## Architecture / Workflow Summary

代码结构 / 工作流总结。

## Section Info

**Course**: Claude Code Mastery
**Level**: {Level}
**Videos**: {N}
**Screenshots**: {N} in `assets/claude-code-mastery/`
```

### Phase 6: 收尾

1. 统一更新 `index.md`
2. 写导入日志 `wiki/log/{date}-Ingest-Claude-Code-Mastery.md`
3. 创建 README.md

## 文件位置约定

```
B:/DownLoad/Claude Code Mastery From Zero to Super Hero/
├── Claude Code Mastery - Level 1/  ← 原始视频 + 字幕
├── Claude Code Mastery - Level 2/
├── Claude Code Mastery - Level 3/
├── _preprocessed/                   ← 预处理纯文本（Phase 2 输出）
├── _screenshot_plan.json            ← 截图规划（Phase 3 输出）
└── _batch_screenshots.sh            ← 批量截图命令（Phase 3 输出）

B:/GitHub/Obsadian/CourseWiki/
├── assets/
│   └── claude-code-mastery/         ← 所有截图
├── wiki/
│   ├── index.md
│   ├── log/
│   └── sources/
│       └── claude-code-mastery/     ← 10 篇 Section 文章
```

## 模板文件

本 skill 包含以下可复用模板：

| 文件 | 用途 | 使用方式 |
|------|------|---------|
| `templates/preprocess-srt.py` | Phase 2 字幕预处理 | 复制到课程目录，修改 LEVEL_DIRS + SECTIONS 定义，运行 |
| `templates/plan-screenshots.py` | Phase 3 截图规划 | 复制到课程目录，修改 sections + level_dirs + asset_dir，运行 |

两个模板都使用 `<PLACEHOLDER>` 标记供替换。

## index.md 更新模式（固定）

更新 index.md 时使用以下固定模式，避免 `---` 分隔符的多处匹配问题：

```python
from hermes_tools import read_file, write_file

content = read_file("wiki/index.md", limit=500)["content"]
lines = content.split('\n')

# 找到 "## Analysis" 行（或目标插入点前的标记）
insert_marker = "## Analysis"
insert_idx = None
for i, line in enumerate(lines):
    if line.strip().startswith(insert_marker):
        insert_idx = i
        break

# 在标记前插入新内容
new_section = [
    "",
    "## Claude Code Mastery (`sources/claude-code-mastery/`)",
    "",
    "### Level 1 — Basics",
    "- [[section-01-claude-code-basics]] — 描述（N 张截图）",
    "### Level 2 — Pro Workflows",
    "### Level 3 — Advanced",
    "",
    "---",
    "",
]

new_lines = lines[:insert_idx] + new_section + lines[insert_idx:]
new_content = '\n'.join(new_lines)
write_file("wiki/index.md", new_content)
```

## 覆盖导入：清理旧文章

当课程之前已经导入过单课文章，现在要替换为 Section 级文章时：

1. **先清理旧文章和截图**，再写新文章
2. index.md 中旧 Section 的逐课条目也需清理
3. 清理时注意不要在 index.md 中误删其他课程的内容

```bash
rm -f "B:/GitHub/Obsadian/CourseWiki/wiki/sources/{course-dir}/"*.md
```

### index.md 清理

旧 index.md 可能包含多级子 Section（`#### Section 2 - Setup from Zero`），需要一并清理：

```python
from hermes_tools import read_file, write_file

content = read_file("B:/GitHub/Obsadian/CourseWiki/wiki/index.md", limit=500)["content"]
lines = content.split('\n')

start_marker = "### Build Your Own Claude Code"
end_marker = "---\n"
# ...找到旧条目并删除
```

**关键**：旧 index.md 的格式不稳定（可能有页码残留如 `7|` 前缀）。用 `content.find()` + `content.rfind()` 定位比 `patch` 更安全。

1. **写文章时不碰 index.md** — 子代理只写自己的 Section 文章文件
2. **主代理最后统一更新 index.md** — 等所有文章写完，一次性地插入所有条目
3. **截图路径定稿后不能改** — Phase 3 输出的 slug 在整个流程中冻结
4. **文章文件名约定**：`section-{number}-{slug}.md`（如 `section-01-claude-code-basics.md`）
5. **不要传截图路径以外的 JSON 给子代理** — 只传纯文本内容 + slug 列表，减少 input token

## 子代理 Context 构建（实测优化）

当用 delegate_task 写文章时，context 的写法直接决定 token 消耗：

| Context 写法 | input token | 子代理工具调用 | 来源课程 |
|-------------|------------|--------------|---------|
| 只说"截图在目录" | ~214K | 15 次 search_files 验证 | Hermes Agent |
| 明确"不要验证"+slug 表 | ~22K | 仅 read_file+write_file | Claude Code |
| 同上+toolset=['file'] | ~16K | 仅 read_file+write_file | Claude Code |

**核心原则**：
1. **明确声明"截图已全部就绪，不要验证文件"** — 这句话让子代理跳过 file 验证循环
2. **提供完整的 slug→label 表** — 子代理不会自己去算 slug
3. **明确声明哪些视频不放截图** — Intro/Wrap-Up 类单独列一行
4. **限制 toolsets=['file']** — 不给 search 工具。子代理有 `read_file`+`write_file`就够了
5. **slug 表直接写死**，不让子代理计算

### Context 模板

```
用中文写 Obsidian LLM Wiki 笔记。

输入数据：{path}/S{num}.txt

截图全部就绪，不要验证文件。直接写引用：![[../../../assets/{course-dir}/{slug}-{label}.jpg]]

slug 表：
- Section Overview → section-overview(不放截图)
- XXXX → xxxx-slug（3张：overview, detail, result）
- XXXX → xxxx-slug2（3张）

密度：Section Overview 和 Recap 不放截图。其他 N 课每课 3 张截图。

输出：{vault_path}/wiki/sources/{course-dir}/section-{num}-{slug}.md
```

## 目录结构识别（跨课程通用）

### 通用目录匹配策略

不同课程的目录命名模式各不相同。**用数字前缀精确匹配**：

```python
# 正确做法：按数字前缀匹配
for d in os.listdir(base):
    if os.path.isdir(os.path.join(base, d)):
        if d.startswith(f"{num} "):
            sec_dirs[sec_id] = os.path.join(base, d)
```

**历史教训**：避免用 `"Setup" in "Pro Subagents"` 这类模糊匹配。**永远用数字前缀匹配**。

### 视频文件名匹配

```python
def find_srt(level_dir, video_num):
    for f in os.listdir(level_dir):
        if f.endswith('.en.srt') and '(1)' not in f:
            base_name = f.replace('.en.srt', '')
            if base_name.startswith(f"{video_num}. ") or base_name.startswith(f"{video_num}."):
                return os.path.join(level_dir, f)
    return None
```

### Level 映射错误

Section 的 `level` 字段容易写错。一定要逐条验证：
```python
# ❌ 常见错误
"L2-M05": {"title": "GitHub Integration", "level": "Level 1", ...}
# ✅ 正确
"L2-M05": {"title": "GitHub Integration", "level": "Level 2", ...}
```

### 视频前缀匹配细节

`startswith("2.2")` **不会**匹配 `"2.2. A..."`。必须传完整前缀（含点号）：
```python
if base.startswith(num_prefix + '.') or base.startswith(num_prefix + ' '):
```

## 陷阱与注意事项

- **当前模型不支持 vision**（如 DeepSeek）时，依赖字幕原文推断截图内容，不要反复尝试 vision
- **截图不是越多越好** — Section 级文章 10-15 张足够
- **SRT 预处理不可少**：原始 SRT 的 55% 是元数据，喂给 agent 就是烧 token
- **视频路径含空格时，ffmpeg 要用双引号包裹**
- **`.en.srt` 是唯一字幕格式**，不要匹配其他后缀
- **截图文件名做 kebab-case**，不要用中文或空格
- **index.md 的 `---` 陷阱**：用 `execute_code` 中的 `content.find()` + `content.rfind()` 定位插入
- **后台进程并发**：ffmpeg 是 CPU 密集，批量截图不要同时跑多个进程
- **Preprocessed 文本中保留视频标题行** — 写文章时需要知道哪段文字对应哪个视频
