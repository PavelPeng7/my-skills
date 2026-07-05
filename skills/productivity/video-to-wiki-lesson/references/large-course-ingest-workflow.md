# 大课程批量导入 — 6 Phase 详解

## 课程目录结构

```
CourseName/
├── Level 1 - Basics/
│   ├── 1. Intro.mp4 + 1. Intro.en.srt
│   └── ...
├── Level 2 - Advanced/
├── _preprocessed/        ← Phase ② 输出
├── _screenshot_plan.json ← Phase ③ 输出
└── _batch_screenshots.sh ← Phase ③ 输出
```

## Phase ① 目录分析

数字前缀精确匹配目录名（`"1 "` → Level 1）。⚠️ 避免模糊匹配。

## Phase ② 字幕预处理

使用 `templates/preprocess-srt.py`：复制→修改配置→运行。输出每Section一个纯文本文件。

## Phase ③ 截图规划

使用 `templates/plan-screenshots.py`：根据时长自动确定帧数（<30s=1帧, 30-120s=2帧, >120s=3帧）。Intro/总结类不放截图。

## Phase ④ 批量截图

```bash
bash _batch_screenshots.sh
```
后台执行，不并发（ffmpeg是CPU密集）。

## Phase ⑤ 并行写文章

子代理分配：最多3个并行，每个最多4个Section。

**Context模板**（实测~16K token）：

```
用中文写图文笔记。

输入：{path}/section-{N}.txt

截图已全部就绪，不要验证文件。直接写引用：
  ![[../../../assets/{course}/{slug}-{label}.jpg]]

slug表（每slug配 overview/detail/result 三张）：
- Overview → overview（不放截图）
- Installation → installation（3张）

密度：Intro和Recap不放截图。其余每课3张。

输出：{vault}/sources/{course}/section-{N}-{slug}.md
```

### 子代理不要做的事

❌ 不碰 index.md ❌ 不验证截图 ❌ 不计算slug

## Phase ⑥ 收尾

1. 主代理统一更新index.md（子代理不碰）
2. 写导入日志
3. Git提交

## 常见陷阱

- **Level映射错误**：逐条验证Section的level字段
- **视频前缀匹配**：用完整前缀 `"2.2. "` 而非 `"2.2"`
- **index.md的 `---` 陷阱**：用固定标记行定位插入点
