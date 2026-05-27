# 大课程（50+ 视频）导入完整工作流

当处理 50+ 视频的大课程且无字幕文件时，采用 **并行管道模式**：截图批处理和文章编写同步进行。

## 完整步骤

### Phase 1: 侦察（5 分钟）

```bash
# 1. 看看课程目录结构
ls "B:/DownLoad/<course>/"
ls "B:/DownLoad/<course>/1 - First Section/"

# 2. 统计视频数量和是否有字幕
find "B:/DownLoad/<course>/" -name "*.mp4" | wc -l
find "B:/DownLoad/<course>/" -name "*.srt" | wc -l
```

### Phase 2: 环境准备（5 分钟）

```python
# 一次性创建目录
mkdir -p "B:/DownLoad/<course>/_transcripts/"
mkdir -p "B:/GitHub/Obsadian/CourseWiki/assets/<course-slug>/"

# 确认 Whisper 可用
pip install faster-whisper
```

### Phase 3: 启动批量转录（后台）

```python
# 用 _batch_v3.py 模板（参考 batch-script-pattern.md）
# 关键配置：
#   BASE = "B:/DownLoad/<course>"
#   SCREENSHOT_DIR = "B:/GitHub/Obsadian/CourseWiki/assets/<course-slug>"
#   SECTION_MAP 映射所有 Section 文件夹名 → 短 slug

# 后台启动（不要等）
terminal(background=True, notify_on_complete=True, timeout=14400)
# 命令：python -u "_batch_v3.py" > "_logs.txt" 2>&1
```

### Phase 4: 立即编写文章（与批处理并行）

批处理在后台运行的同时，**立即开始写文章**。不需要等截图完成。

**每节文章的截图引用**用预计算的 slug 写入：

```python
def slugify(name):
    return name.lower().replace(' ', '-').replace(',', '').replace("'", '').replace('.', '')

for num, name in section_videos:
    print(f"{num:02d}-{slugify(name)}-overview.jpg")
```

截图引用路径：
```
![[../../../assets/<course-slug>/<section-slug>/01-lesson-name-overview.jpg]]
```

**只引用 overview 帧**（第一帧）。detail 和 result 帧用作额外参考但不一定写入文章。

### Phase 5: 课程入口 + 索引 + 日志

每完成 3-4 篇文章后，统一创建配套文件：

1. **README.md** — 课程入口页面（Entity 格式，含所有 Section 的 `[[wikilink]]`）
2. **log 文件** — `wiki/log/YYYY-MM-DD-Ingest-<course>.md`
3. **index.md 更新** — 在 sources 部分插入新的课程区块，在 entities 部分添加课程条目

### Phase 6: 验证截图引用

```python
import os, re, glob

articles = glob.glob("wiki/sources/<course>/section-*.md")
ok, pending, mismatch = 0, 0, 0

for apath in articles:
    with open(apath) as f:
        content = f.read()
    refs = re.findall(r'!\[\[([^\]]+)\]\]', content)
    for r in refs:
        parts = r.split('/')
        rel_part = '/'.join(parts[3:])
        full_path = f"B:/GitHub/Obsadian/CourseWiki/{rel_part}"
        
        if os.path.exists(full_path):
            ok += 1
        else:
            base_dir = os.path.dirname(full_path)
            if not os.path.exists(base_dir) or len([
                f for f in os.listdir(base_dir) if f.endswith('.jpg')
            ]) == 0:
                pending += 1  # 批处理尚未完成
            else:
                mismatch += 1  # 文件名写错了
                print(f"MISMATCH: {os.path.basename(full_path)}")
```

pending 是正常的——batch 还没处理到那个 Section。mismatch 必须修复。

### Phase 7: Git push

```bash
cd "B:/GitHub/Obsadian/CourseWiki"
git add -A
git commit -m "YYYY-MM-DD: Import <course-name> course"
git push
```

## 输出检查清单

- [ ] `_batch_v3.py` 已在后台运行
- [ ] 11 篇 Section 文章已写完（即使有些截图还没生成）
- [ ] 所有截图引用格式正确（slug 预计算）
- [ ] README.md 已创建
- [ ] index.md 已更新 Sources + Entities
- [ ] 导入日志已创建
- [ ] git push 已完成

## 常见陷阱

- **不要等批处理完成才写文章**。文章编写和截图生成是两个独立管道。先写文章（用正确 slug），等截图到位后自动生效
- **不要在 index.md 上用 `patch`**。多个 `---` 分隔符让 old_string 难以唯一匹配。用 `execute_code` 中的 `content.find()` + `content.rfind()` 定位插入点，再 `write_file` 完整重写
- **不要启动多个 Whisper 进程**。串行更快，资源竞争更少
- **进程退出通知只是噪音**。Hermes 会为所有已退出进程发送通知，包括旧版本脚本和 delegate_task 遗留的子进程。忽略它们，只关注最新的活跃进程
- **截图引用用 overview 帧足矣**。不要为每帧都配文——overview 帧已足够作为文章配图
