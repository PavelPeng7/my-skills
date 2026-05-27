# 单视频 / 独立文件 / 会议内容处理

当用户直接发送一个独立视频文件（非课程文件夹内的系列视频），走此简化流程。

## 场景判断

| 内容类型 | 输出位置 | 截图策略 | 文章结构 |
|---------|---------|---------|---------|
| 课程/教程 | CourseWiki sources/ | 5-15 帧 | 标准图文结构 |
| 设计评审/产品会议 | CourseWiki + PavelObsidianNotes | 10-15 帧 | 分节 + 截图 + 原文引用 |
| 杂谈/播客 | 仅 PavelObsidianNotes 文献笔记 | 0-3 帧 | 纯文字摘要 |
| 其他 (不确定) | 先分析内容再决定 | 暂不截图 | 先问用户 |

## 简化流程

### Step 1: 确定输出目录

视频在下载目录（如 `D:/ChormDownload/`）时，输出目录建在视频同名文件夹下：
```
B:/DownLoad/<video-basename>/_transcripts/
```

### Step 2: 运行 Whisper 转录

```python
python "B:/DownLoad/<basename>/_transcripts/_whisper_helper.py" \
  "<video_path>" \
  "B:/DownLoad/<basename>/_transcripts/transcript.json"
```

用 `terminal(background=true, notify_on_complete=true, timeout=7200)` 运行。
- 语言参数 `language=None` → 自动检测
- Hermes venv Python：`C:\Users\27263\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`

### Step 3: 分析内容 → 决定归类

等待转录完成后，分析内容决定归类：
- 如果是课程/教程 → 导入 CourseWiki
- 如果是会议/杂谈 → 导入 PavelObsidianNotes 或仅保留文字记录

### Step 4: 截图

- 63 分钟视频约截 3 帧（overview / detail / result）
- 设计评审：截**UI 画面变化时**（新组件展示、设计稿对比、设置面板打开）
- 讨论类内容：截**视觉参考画面**（参考标准、对比图、当前实现截图）
- 纯讲话无画面变化时段不截

### Step 5: 写文章

- **CourseWiki** `sources/` 中写完整文章（含截图引用 + 全文内容分析）
- **PavelObsidianNotes** `文献笔记/` 中写精简版（提炼关键洞察 + 关联现有笔记）
- 在 index.md 中按内容类型独立分类（如「产品设计评审」独立分区）

### Step 6: 更新索引

- 创建或更新 index.md
- 写导入日志到 `wiki/log/`

## 与课程导入的区别

| 维度 | 课程 | 单视频/会议 |
|------|------|------------|
| 结构 | 逐 Section 多篇文章 | 一篇综合性文章 |
| 内容 | 课程体系的逐课讲解 | 讨论/对话为主 |
| 截图 | 按字幕时间点规划 | 关注视觉变化点 |
| 参与者 | 单一讲师 | 可能有多个 → 标注角色 |
| 术语 | 课程自带术语表 | 可能需要额外「术语解释」区 |
| 笔记存放 | 仅 CourseWiki | CourseWiki + PavelObsidianNotes 双重存放 |
