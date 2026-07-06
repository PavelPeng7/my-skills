---
name: video-to-article
description: >
  Turn a video URL/file or subtitle file into article-style notes, transcript
  study materials, or large-course imports with screenshots, yt-dlp, ffmpeg,
  and Whisper. Trigger when the user asks to turn a video into notes or an
  article, download and transcribe a video, study subtitles, extract key
  screenshots, or batch-import a course into Obsidian or Markdown.
allowed-tools: Read, Write, Terminal, File, Vision, Search
---

# Video → Article 全能视频转图文工作流

## 核心能力矩阵

| 模式 | 输入 | 输出 | 适用场景 |
|------|------|------|---------|
| **A: 单视频笔记** | 视频URL/文件 | 图文混排Obsidian笔记+Git推送 | 影评、教程、烹饪、Vlog |
| **B: 字幕学习** | 已有字幕文件(.srt/.vtt) | 摘要/测验/词汇表/问答 | 已有字幕，只想提取知识 |
| **C: 大课程导入** | 课程文件夹(50+视频) | Section级图文文章+index索引 | Udemy/慕课等批量课程 |

## 模式 A: 单视频 → 图文笔记

### 触发词

"转成笔记"、"图文笔记"、"下载这个视频"、"分析这条视频"

### 工作流（9步）

#### Step 1: 识别平台 + 认证

**平台速查表**：

| 平台 | Cookie | 格式策略 | 备注 |
|------|--------|---------|------|
| Bilibili (b23.tv/bilibili.com) | ✅ 需要 | 先 `-F` 查看格式ID | BV号格式，412反爬 |
| YouTube (youtube.com/youtu.be) | ❌ | `bestvideo[height<=720]+bestaudio` | 直下 |
| TED/Coursera/Udemy | 视情况 | `-F` 查看 | 付费内容需登录 |
| 抖音/TikTok/小红书 | ❌ | 自动 | 短视频 |
| 其他1700+平台 | 视情况 | `-F` 查看 | |

**Bilibili Cookie处理**：
```bash
# 将浏览器 Cookie 导出为 Netscape 格式
python3 path/to/bili_cookie_to_netscape.py
```

#### Step 2: 解析视频ID + 获取元信息

```bash
# Bilibili短链解析
VIDEO_ID=$(curl -sL "https://b23.tv/XXXXX" -o /dev/null -w "%{url_effective}" | sed 's/.*\/video\///;s/[\/?].*//')

# 获取信息
yt-dlp --no-download --print "%(title)s|%(duration)s|%(uploader)s" "<URL>"
```

#### Step 3: 下载视频

**策略**：< 4分钟 → 1080p；≥ 4分钟 → 720p

```bash
# 先查格式
yt-dlp -F "<URL>"

# 下载（Bilibili需加--cookies）
mkdir -p "<TEMP_DIR>/<VIDEO_ID>"
yt-dlp -o "<TEMP_DIR>/<VIDEO_ID>/video.%(ext)s" \
  -f "<选定的格式ID>" --merge-output-format mp4 "<URL>"
```

#### Step 4: Whisper语音转文字

```bash
python3 << 'PYEOF'
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu", compute_type="float32",
                     download_root="<CACHE_DIR>")
segments, _ = model.transcribe("<TEMP_DIR>/<ID>/video.mp4", language="zh", beam_size=5)
with open("<TEMP_DIR>/<ID>/transcript.txt", "w") as f:
    for seg in segments:
        f.write(f"[{seg.start:.1f}s - {seg.end:.1f}s] {seg.text.strip()}\n")
PYEOF
```

语言：中文→`language="zh"`，英文→`language="en"`，自动→省略参数
模型：tiny(最快) < base(推荐) < small(最准)
Apple Silicon加速：`device="mps", compute_type="float16"`

#### Step 5: 内容分类 + 截图规划

**先根据转录内容为视频分类**，再按类型决定截图策略：

| 视频类型 | 特征 | 截图数 | 密度 |
|---------|------|--------|------|
| **讲演/影评** | 核心论点递进，口播为主 | 8-12张 | 每30-40秒文字配1张 |
| **实操/教程** | 步骤递进，操作画面 | 3-8张 | 每步骤1张 |
| **论坛/对谈** | 多人讨论，观点交错 | 5-8张 | 每人切换/话题转折1张 |
| **Vlog/杂谈** | 松散叙事 | 3-5张 | 场景切换时 |
| **<30s短视频** | 单点信息 | 1张 | 开头 |
| **30-120s** | 简短内容 | 3-5张 | 分段截取 |

**截图时刻判断**：
- 讲演类：开头标题画面→引出核心概念→每个论点首帧→金句出现→结尾
- 实操类：操作步骤变化→UI/界面变化→有代表性画面
- ❌ 不截：过渡语、纯口播无画面变化、重复画面

**截图文件名**：kebab-case英文，两位数字前缀（`01-intro.jpg`、`02-core-concept.jpg`）

#### Step 6: 批量截图

```bash
VIDEO="<TEMP_DIR>/<ID>/video.mp4"
OUTDIR="<TEMP_DIR>/<ID>/screenshots"
mkdir -p "$OUTDIR"
# -ss 放 -i 前面 = 精确seek，速度快
ffmpeg -y -ss <秒> -i "$VIDEO" -frames:v 1 "$OUTDIR/01-intro.jpg"
```

#### Step 7: 生成图文笔记

```bash
mkdir -p "<VAULT>/assets/video/<VIDEO_ID>"
cp <TEMP_DIR>/<ID>/screenshots/*.jpg "<VAULT>/assets/video/<VIDEO_ID>/"
```

笔记结构：

```markdown
---
title: <核心主题>
source: <Bilibili|YouTube|...>
author: <UP主/频道>
type: 文献笔记
tags: [视频笔记, <主题标签>]
created: <YYYY-MM-DD>
---

# <作者>：<标题>

> **来源**：<平台> @<作者>

## 📌 核心洞见
1-2段概括

![[../../../assets/video/<ID>/02-xxx.jpg]]

## ⚡ <分节标题>
...
![[../../../assets/video/<ID>/xxx.jpg]]
> 「<原文引用>」

## 🎯 行动清单
- [ ] ...

## 💬 金句
> ...

## 🔗 相关链接
- [[已有笔记]] — 关联原因
```

引用格式：`![[../../../assets/video/<ID>/<filename>.jpg]]`

#### Step 8: 知识库关联

```bash
find "<VAULT>" -name "*.md" | xargs grep -li "<核心关键词>"
```

#### Step 9: Git推送

```bash
cd "<VAULT>" && git add -A && git commit -m "文献笔记(图文): <标题>" && git push
```

---

## 模式 B: 字幕深度学习

### 触发词

"学习这个字幕"、"总结内容"、"出几道题"、"整理术语"、"考考我"

### 前置：输入来源

| 来源 | 获取方式 | 预处理 |
|------|---------|--------|
| 视频自带 .srt/.vtt | 直接读取 | 有则先用 |
| 无字幕但已下载视频 | yt-dlp下字幕或Whisper转录 | 剥离时间码→纯文本 |
| 直接粘贴字幕文本 | 用户提供 | 直接使用 |

### 5种学习模式

#### B1: 知识提取（默认）

生成结构化学习指南：Key Concepts / Key Takeaways / Examples / Glossary

#### B2: 章节摘要

按主题切换自动分章，每章2-3句总结。检测信号：过渡语("Now let's talk about...")、长停顿(>5s间歇)、新术语大量出现。

#### B3: 关键词汇表

提取领域术语、高频词、明确定义的词汇，输出表格含术语/翻译/上下文解释/出现位置。

### 字幕预处理（SRT→纯文本）

原始SRT的55%是元数据，必须先剥离：

```python
import re
def strip_srt(srt_text):
    lines = srt_text.split('\n')
    result = []
    for line in lines:
        line = line.strip()
        if re.match(r'^\d+$', line): continue      # 序号
        if re.match(r'^\d{2}:\d{2}:\d{2}', line): continue  # 时间码
        if not line: continue
        result.append(line)
    return ' '.join(result)
```

### 陷阱

- **超大文件**：分段读取，一次≤1500行
- **自动字幕误听**：标记 `[可能的转录错误]`
- **视觉依赖内容**：标注 `[此处为视觉内容]`
- **多人对话**：自动字幕可能混搭说话人

---

## 模式 C: 大课程批量导入

### 六 Phase 流程

| Phase | 做什么 | Token策略 |
|-------|--------|-----------|
| ① 目录分析 | 列出Section结构、视频树 | 极低（~500） |
| ② 字幕预处理 | 批量剥离SRT→纯文本 | 终端脚本，零token |
| ③ 截图规划 | 预计算slug+ffmpeg命令 | 终端脚本，零token |
| ④ 批量截图 | ffmpeg一锅端 | 后台终端，零token |
| ⑤ 并行写文章 | 子代理×最多3个Section | 仅传纯文本+slug表 |
| ⑥ 收尾 | index.md+日志 | 极低 |

### Phase ① 目录分析

遍历目录，建立 `{Section: [视频列表]}` 结构。按数字前缀精确匹配目录名。

### Phase ② 字幕预处理

使用 `templates/preprocess-srt.py`：复制到课程目录 → 修改配置 → 运行。输出 `_preprocessed/section-{slug}.txt`。

### Phase ③ 截图规划

使用 `templates/plan-screenshots.py`：根据时长和内容类型自动确定截图点。输出 `_screenshot_plan.json` + `_batch_screenshots.sh`。

### Phase ④ 批量截图

```bash
bash _batch_screenshots.sh
```

后台执行，ffmpeg不并发。

### Phase ⑤ 并行写文章

**子代理Context三原则（实测省90% token）**：

1. 明确声明"截图已就绪，不要验证文件"
2. 提供完整slug→label表（不让子代理计算）
3. 标注不放截图的视频

```python
# ✅ 最优Context（实测~16K input token）
context = """
用中文写图文笔记。

输入：_preprocessed/section-01.txt

截图已全部就绪，不要验证文件。直接写引用：
  ![[../../../assets/<course>/<slug>-<label>.jpg]]

slug表（每slug配 overview/detail/result 三张）：
- Installation → installation（3张）
- Intro → intro（不放截图）

密度：Intro不放截图，其余3张/课。

输出：sources/<course>/section-01-xxx.md
"""
```

并行分配：最多3个子代理，每个最多4个Section。

### Phase ⑥ 收尾

1. 仅主代理统一更新index.md（子代理不碰）
2. 写导入日志
3. Git提交

---

## 前置条件

- **yt-dlp** — 视频下载（1700+平台）
- **ffmpeg** — 音频处理、视频截图
- **faster-whisper** — Python库，语音转文字
- **Obsidian Vault** — 配置为 Git 版本控制
- **Git** — 版本控制与推送

检查命令：
```bash
which yt-dlp ffmpeg 2>&1
python3 -c "from faster_whisper import WhisperModel; print('OK')" 2>&1
```

---

## 路径约定

| 变量 | 用途 | 示例 |
|------|------|------|
| `<TEMP_DIR>` | 临时下载/处理 | 项目 workspace 下的临时目录 |
| `<VAULT>` | Obsidian 库根目录 | B:/你的库路径 或 ~/Documents/Obsidian |
| `<ATTACH_DIR>` | 截图在Vault中的位置 | `<VAULT>/assets/video/<VIDEO_ID>/` |
| `<NOTE_DIR>` | 笔记存放目录 | `<VAULT>/文献笔记/` |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| B站412反爬 | 刷新Cookie，过期需扫码重登 |
| B站格式ID不可用 | 先用 `-F` 查看，格式ID随视频而异 |
| YouTube下载失败 | 地区限制→代理；格式不可用→`-f "best[height<=720]"` |
| Whisper太慢 | 换`tiny`模型；Apple Silicon换`device="mps"` |
| 截图文件导致Link异常 | 用kebab-case英文命名 |
| Git推送失败 | `git pull --rebase && git push` |
| 子代理过度验证截图 | Context写死slug表+声明"不要验证" |
