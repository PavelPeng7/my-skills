# Phase 5: 子代理 Context 构建最佳实践

本文档记录从 Claude Code Mastery 和 Hermes Agent 两轮课程导入中提炼的 delegate_task context 优化经验。

## 实测数据对比

| 写法 | Input Token | 子代理工具调用 | 耗时 |
|------|------------|--------------|------|
| 只说"截图在目录" | ~214K | 15 次 search_files 验证 | 85s |
| 明确"不要验证" + slug 表 | ~22K | read_file+write_file 仅 3 次 | 58s |
| 同上 + toolsets=['file'] | ~16K | read_file+write_file 仅 3 次 | 49s |

子代理默认行为：当你说"截图在 assets/ 目录"时，它会去逐个验证文件是否存在，
每个验证花 ~2K token。10 个视频 × 3 帧 = 30 次 search_files = 60K+ token。

## Context 构建模板

```
截图已全部就绪，不要验证文件。直接写引用：
  ![[../../../assets/{course-dir}/{slug}-{label}.jpg]]

slug 表（每个 slug 都有 overview/detail/result 三张，直接使用）：
- Video A → video-a
- Video B → video-b
- Intro N → intro-n（不放截图，只有 2 帧）

密度规则：intro-n 不放截图，其他每课 3 张截图。
```

## 关键规则

1. **第一行必须是"截图已全部就绪，不要验证文件"** — 阻止子代理的搜索冲动
2. **明确写 slug→label 对应** — 不要只写"按视频名"，子代理不会自己算 slug
3. **单独列出不放截图的视频** — 不能只在 slug 表中暗示（"只有 2 帧"不够）
4. **toolsets 只给 ['file']** — 不给 search 工具就堵死了验证路径
5. **不要给 JSON 文件路径让子代理自己读** — 把 slug 表直接内联到 context
