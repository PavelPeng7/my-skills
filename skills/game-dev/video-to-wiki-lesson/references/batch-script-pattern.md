# 健壮的批量转录脚本模式

## 视频文件名解析

Windows 上 Unity 课程视频文件名格式不统一，常见有：

| 真实文件名 | 格式规律 |
|-----------|---------|
| `1 -Introduction.mp4` | `{num} -{name}.mp4` — 数字后空格-dash，无空格 |
| `10 -Reverse.mp4` | 同上 |
| `2 -Create a project.mp4` | 同上 |

用正则表达式解析：
```python
import re, glob, os

def get_videos(section_path):
    files = sorted(glob.glob(os.path.join(section_path, "*.mp4")))
    result = []
    for f in files:
        basename = os.path.basename(f)
        m = re.match(r'^(\d+)\s+-(.+?)\.mp4$', basename)
        if m:
            num = int(m.group(1))
            name = m.group(2).strip()
            result.append((num, name, f))
    return sorted(result, key=lambda x: x[0])
```

**不要用**硬编码的视频列表（subagent 留下的 `_batch_process_v2.py` 模式）。**要用**目录扫描模式，因为：
- 文件名可能有细微格式差异（空格数量、大小写）
- 硬编码列表无法复用

## 截图时间戳计算策略

用转录 JSON 的 `duration` 字段（Whisper 返回），不要用 ffprobe（Windows MSYS 下不可用）：

```python
def get_frame_positions(duration_sec):
    if duration_sec < 30:
        return [0.30]                    # 短: 1 帧
    elif duration_sec <= 90:
        return [0.30, 0.65]              # 中: 2 帧
    else:
        return [0.25, 0.50, 0.75]        # 长: 3 帧

def get_screenshot_timestamps(duration_sec, positions):
    result = []
    for pct in positions:
        pos = duration_sec * pct
        h, m, s = int(pos // 3600), int((pos % 3600) // 60), pos % 60
        result.append(f"{h:02d}:{m:02d}:{s:06.3f}")
    return result
```

## 截图文件名

```python
def slugify(name):
    return name.lower().replace(' ', '-').replace(',', '').replace("'", '').replace('.', '')

# 3 帧 → ["overview", "detail", "result"]
# 2 帧 → ["overview", "detail"]
# 1 帧 → ["overview"]
labels = ["overview", "detail", "result"]
jpg_name = f"{num:02d}-{slugify(name)}-{labels[i]}.jpg"
# 示例: 01-create-a-race-track-overview.jpg
```

## 完整批量脚本模板

```python
"""_batch_v3.py — Batch transcribe + screenshot all sections."""
import subprocess, json, os, sys, glob, re, time

BASE = "B:/DownLoad/<course-folder>"
WHISPER_PY = "C:/Users/27263/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
HELPER = os.path.join(BASE, "_transcripts/_whisper_helper.py")
SCREENSHOT_DIR = "B:/GitHub/Obsadian/CourseWiki/assets/<course-slug>"
FFMPEG = "ffmpeg"

SECTION_MAP = {
    "1 - Section Name": "section-slug",
    # ...
}

def get_videos(section_name):
    section_path = os.path.join(BASE, section_name)
    files = sorted(glob.glob(os.path.join(section_path, "*.mp4")))
    result = []
    for f in files:
        basename = os.path.basename(f)
        m = re.match(r'^(\d+)\s+-(.+?)\.mp4$', basename)
        if m:
            result.append((int(m.group(1)), m.group(2).strip(), f))
    return sorted(result, key=lambda x: x[0])

def process_video(section_short, num, name, video_path):
    transcript_dir = os.path.join(BASE, "_transcripts", section_short)
    os.makedirs(transcript_dir, exist_ok=True)
    json_path = os.path.join(transcript_dir, f"{num:02d}-{slugify(name)}.json")
    
    # 1. Transcribe (skip if exists)
    if os.path.exists(json_path):
        with open(json_path) as f:
            actual_duration = json.load(f).get('duration', 0)
        print(f"[SKIP] {section_short} {num:02d} - {name}")
    else:
        print(f"[TRANSCRIBE] {section_short} {num:02d} - {name}", flush=True)
        result = subprocess.run([WHISPER_PY, HELPER, video_path, json_path],
                                capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr[:200]}", flush=True)
            return False
        with open(json_path) as f:
            actual_duration = json.load(f).get('duration', 0)
    
    # 2. Screenshots (skip if exist)
    positions = get_frame_positions(actual_duration)
    timestamps = get_screenshot_timestamps(actual_duration, positions)
    screenshot_dir = os.path.join(SCREENSHOT_DIR, section_short)
    os.makedirs(screenshot_dir, exist_ok=True)
    labels = ["overview", "detail", "result"]
    for i, ts in enumerate(timestamps):
        label = labels[i] if i < len(labels) else f"frame-{i+1}"
        jpg_name = f"{num:02d}-{slugify(name)}-{label}.jpg"
        jpg_path = os.path.join(screenshot_dir, jpg_name)
        if os.path.exists(jpg_path):
            continue
        subprocess.run([FFMPEG, "-ss", ts, "-i", video_path, "-vframes", "1", "-q:v", "3", jpg_path, "-y"],
                       capture_output=True, timeout=60)
        if os.path.exists(jpg_path):
            print(f"  SCREENSHOT: {jpg_name}", flush=True)
    return True

# Usage: python _batch_v3.py "Section Name" "Section Name" ...
targets = sys.argv[1:] if len(sys.argv) > 1 else list(SECTION_MAP.keys())
```

## 运行方式（关键）

```bash
# 方法 A（推荐）：单进程串行处理全部
python -u "_batch_v3.py" > "_log.txt" 2>&1
# 在 Hermes 中：terminal(background=true, notify_on_complete=true, timeout=14400)

# 方法 B：分成 3 批并行（每批 3-4 个 Sections）
python -u "_batch_v3.py" "Section A" "Section B" "Section C" > "_log_A-C.txt" 2>&1

# 不推荐用 delegate_task 或 subagent
```

## 性能基准

| 指标 | 值 |
|------|-----|
| 模型 | faster-whisper base (CPU, int8) |
| 转录速度 | ~15s / 分钟音频 |
| 截图速度 | <1s / 帧 (ffmpeg) |
| 100 视频总耗时 | ~2-4 小时 (串行) |
| JSON 大小 | 每课 1-5 KB |
| JPG 大小 | 每张 30-120 KB |

## 2 帧与 3 帧的 label 命名

```python
# 截图 label 名取决于帧数：
if len(timestamps) == 3:
    labels = ["overview", "detail", "result"]
elif len(timestamps) == 2:
    labels = ["overview", "detail"]   # 没有 "result" 帧
else:  # 1 帧
    labels = ["overview"]
```

写文章时，只引用 overview 帧（第一帧）通常就够了。不需要为每帧都配文。

## 写入文章时的截图引用验证

写入截图引用后，一定要用 `execute_code` 批量验证文件存在性：

```python
import os, re, glob

# 提取所有 ![[...]] 引用并检查文件存在
articles = glob.glob(".../*.md")
for apath in articles:
    with open(apath) as f:
        content = f.read()
    refs = re.findall(r'!\[\[([^\]]+)\]\]', content)
    for r in refs:
        parts = r.split('/')
        rel_part = '/'.join(parts[3:])  # 跳过 ../../../
        full_path = f"B:/GitHub/Obsadian/CourseWiki/{rel_part}"
        if not os.path.exists(full_path):
            # 检查是否批处理尚未处理该 Section（目录不存在或为空）
            base_dir = os.path.dirname(full_path)
            if not os.path.exists(base_dir) or len(os.listdir(base_dir)) == 0:
                print(f"PENDING: {os.path.basename(full_path)} — batch not yet done")
            else:
                print(f"MISMATCH: {os.path.basename(full_path)} — wrong filename")
```

## index.md 插入陷阱（`---` 分隔符）

`index.md` 有多个 `---` 分隔符。`patch` 的 `old_string` 如果包含 `---` 会匹配多个位置。用 `execute_code` 安全插入：

```python
from hermes_tools import read_file, write_file

result = read_file("wiki/index.md", limit=2000)
content = result['content']

# 通过内容定位插入点，不依赖分隔符
marker = "### 📁 Build Your Own Claude Code"
idx = content.find(marker)    # 找到目标 Section
before = content.rfind("---", 0, idx)  # 找到前面的 ---

new_section = """---
### 📁 New Section (`sources/new/`)
|- [[page]] — description
"""

new_content = content[:before] + new_section + content[before:]
write_file("wiki/index.md", new_content)
```

## 文件名 slug 与文章引用匹配

写文章时先确定实际 slug 再写入引用。用脚本预计算所有 slug：

```python
def slugify(name):
    return name.lower().replace(' ', '-').replace(',', '').replace("'", '').replace('.', '')

for num, name in videos:
    print(f"{num:02d}-{slugify(name)}-overview.jpg")
```

**常见坑**：视频名 "Stop the kart when hitting obstacles" 的 slug 是 `09-stop-the-kart-when-hitting-obstacles`（含 "the"），写文章时容易漏掉。始终基于实际视频名生成 slug 再写引用。

## 批处理进程恢复策略

当后台批处理进程因系统清理（SIGTERM/exit 137/exit -15）被中断时：

1. **不要重新所有 Sections**。先检查已有截图和转录进度
2. 用 `execute_code` 扫描每个 Section 的截图数 vs 期望数（videos × 3）
3. 只重新运行缺少的部分
4. 重新运行时用**单个串行进程**覆盖所有剩余 Sections：
   ```bash
   python -u "_batch_v3.py" "Section A" "Section B" "..." > "_log_retry.txt" 2>&1
   ```
5. 如果系统频繁杀进程，分批重试（一次只处理 2-3 个 Sections 减少运行时间）

## 陷阱清单

- **文件名解析**：用 `re.match(r'^(\d+)\s+-(.+?)\.mp4$', ...)` 匹配所有变体。Windows 路径中的反斜杠在 Python 正则中要 escape 或使用 raw string
- **ffprobe 不可用**：Windows MSYS/bash 下 ffprobe 返回空。用 JSON duration 字段
- **输出缓冲**：Python 脚本加 `-u` 标志，否则终端里看不到实时日志
- **Whisper 首行**：`_whisper_helper.py` 必须以 `import sys` 开头，不能有前导空行（否则 MSYS/bash 下传参偏移）
- **后台进程数量**：不要同时启动 3+ 个 Whisper 进程。CPU 模式下单核串行最快。并行 3 个比串行慢 3 倍且更容易被系统 OOM killer 杀掉
- **subagent 不适用**：100+ 视频用 delegate_task 会超时 + 消耗近百万 token
- **SIGTERM/SIGKILL 恢复**：批量进程可能被系统清理（exit 137/-15）。规划时假设进程可能在任意时刻被杀，每个视频的转录+截图要原子化（先确认 JSON 存在再跳过）
- **旧进程退出通知**：Hermes 会为每个已退出进程发送 `[IMPORTANT: Background process ... completed]`。多个旧进程（来自 delegate_task、之前启动的并行任务等）会陆续退出。忽略它们，只关注最新的主动进程即可
