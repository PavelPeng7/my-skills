# Whisper STT 批量转录工作流

当视频课程没有 `.srt` 字幕文件时，使用 `faster-whisper` 从音频提取文字。

## 安装

```bash
# 在 Hermes 的 venv 中安装
/c/Users/27263/AppData/Local/hermes/hermes-agent/venv/Scripts/pip install faster-whisper
```

Whisper Python 路径：`C:\Users\27263\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`

## 脚本结构

### `_whisper_helper.py` — 单个视频转录

```python
import sys, json, os, subprocess, tempfile

video_path = sys.argv[1]
output_path = sys.argv[2]

audio_path = os.path.join(tempfile.gettempdir(), "whisper_temp_" + os.path.basename(video_path) + ".wav")

# Extract audio
subprocess.run([
    "ffmpeg", "-y", "-i", video_path,
    "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
    audio_path
], check=True, capture_output=True, timeout=300)

# Transcribe
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu", compute_type="int8")

# language="en" 会强制英文识别。对不确定语言的视频（文件名含中文等），用 language=None 让模型自动检测
segments, info = model.transcribe(audio_path, language=None, beam_size=5, vad_filter=True)

result = {
    "language": info.language,
    "language_probability": info.language_probability,  # 含语言置信度，辅助判断
    "duration": info.duration,
    "segments": []
}
for seg in segments:
    result["segments"].append({
        "start": round(seg.start, 1),
        "end": round(seg.end, 1),
        "text": seg.text.strip()
    })

try:
    os.unlink(audio_path)
except FileNotFoundError:
    pass

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False)

print(f"Transcribed: {len(result['segments'])} segments, {result['duration']:.0f}s")
```

**关键约束**：文件必须以 `import sys` 开头，不可有前导空白行。

### `_mass_transcriber.py` — 批量遍历所有 Section

```python
import os, json, subprocess

BASE = "B:/DownLoad/Make a Mario Kart style racing game in Unity 6"
TRANSCRIPTS_DIR = os.path.join(BASE, "_transcripts")
ASSETS_BASE = "B:/GitHub/Obsadian/CourseWiki/assets/mario-kart-unity-6"
WHISPER_PY = r"C:\Users\27263\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"

section_map = {
    "1 - Drive setup": "1-drive-setup",
    "2 - Map Layout": "2-map-layout",
    # ... 所有 Sections
}

HELPER = os.path.join(TRANSCRIPTS_DIR, "_whisper_helper.py")

def screenshot(video_path, timestamp, output_path):
    ts = f"{int(timestamp//3600):02d}:{int((timestamp%3600)//60):02d}:{int(timestamp%60):02d}.000"
    subprocess.run(["ffmpeg", "-ss", ts, "-i", video_path, "-vframes", "1", "-q:v", "3", output_path, "-y"],
                   capture_output=True, timeout=30)

# 截图数量策略
# < 30s: 1 帧 at 30%
# 30-120s: 2 帧 at 30%, 70%
# > 120s: 3 帧 at 25%, 50%, 75%
```

## 运行方式

```bash
# 单个进程串行处理所有 Sections
/c/Users/27263/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -u \
  "B:/DownLoad/.../_transcripts/_mass_transcriber.py" \
  > "B:/DownLoad/.../_transcripts/_batch_log.txt" 2>&1

# 在 Hermes 中用 background 模式启动
terminal(background=true, notify_on_complete=true, timeout=14400)
```

## 性能数据

| 指标 | 值 |
|------|-----|
| 模型 | faster-whisper base (CPU, int8) |
| 速度 | ~15 秒/分钟音频 |
| 104 课总耗时 | ~2-4 小时 |
| 转录 JSON 大小 | 每课 1-5 KB |
| 截图 JPG 大小 | 每张 ~30-80 KB |

## 陷阱

1. **不要用 `language="en"` 硬编码**：用户视频可能是中文或其他语言。用 `language=None` 自动检测。中文视频的 `info.language` 应为 `"zh"`，英文为 `"en"`
2. **不要并行**：CPU 模式下多个 Whisper 进程竞争资源，比串行更慢
2. **不要用 subagent**：100+ 视频的 delegate_task 超时 + 消耗近百万 token
3. **ffprobe 不可用**：Windows MSYS/bash 下 ffprobe 返回空；用 transcript JSON 的 `duration` 字段
4. **辅助脚本首行**：不能有空行——用 `patch` 修复时检查开头
5. **后台输出缓冲**：Python 用 `-u` 标志关闭输出缓冲，否则看不到实时日志
