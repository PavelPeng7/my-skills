# Section 级综合文章格式

当课程超过 50 个视频时，不逐课编写文章，而是按 Section 编写综合文章。

## 适用场景

- 课程有明确的 Section 划分（11 个 Section，104 个视频）
- 每个 Section 内课程内容相关性强
- 104 篇独立文章管理成本过高

## 文件命名与存放

```
wiki/sources/{course-dir}/
├── README.md                          ← 课程入口页
├── section-1-drive-setup.md           ← Section 1
├── section-2-map-layout.md
├── section-10-ai-spawn.md
└── section-11-multiplayer.md
```

## 文章结构

```markdown
# Section {N}: {Section Title}

tags: [source, {course-tag}, ...]

## Summary
2-4 句话概括该 Section 核心内容。

## Key Takeaways
- 5-10 个最重要的知识点
- 每个要点一句话

## Full Lesson Content with Screenshots

### 1. {课程子标题}
{详细内容说明}

![[../../../assets/{course-slug}/{section-slug}/{screenshot}.jpg]]

> *"{引用原文}"*

{技术分析}
---

### 2. {下一课标题}
...

## Architecture Diagram
树形图总结该 Section 的代码/场景架构。

## Section Info
**Course**: {课程名称}
**Section**: {N} — {Title}
**Duration**: ~{N} minutes ({N} videos)
**Type**: Video + XXX
```

## 内容组织原则

1. **每课一小节**：用 `### N. 标题` 标识每节课内容
2. **截图精选**：每个 Section 10-15 张截图（不是每课都要配图）
3. **代码块**：关键 C#/Python 代码用 markdown 代码块展示
4. **表格**：参数配置/对比用 markdown 表格
5. **架构图**：末尾补充代码/场景的 Architecture Diagram

## index.md 索引格式

```markdown
### 📁 {Course Name} (`sources/{course-dir}/`)

|- [[section-1-{slug}]] — 一句话描述
|- [[section-2-{slug}]] — 一句话描述
...
```

## 截图路径

从 `sources/{course-dir}/` 到 `assets/{course-slug}/{section-slug}/` 的相对路径：
```
![[../../../assets/{course-slug}/{section-slug}/{filename}.jpg]]
```

## 配套文件

| 文件 | 作用 |
|------|------|
| `README.md` | 课程索引页，列出所有 Section 文章 |
| `wiki/log/{date}-Ingest-{desc}.md` | 导入日志 |
