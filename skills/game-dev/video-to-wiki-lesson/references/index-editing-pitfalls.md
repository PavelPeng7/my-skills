# index.md 编辑陷阱清单

## 常见损坏类型

### 1. `||- [[xxx]]` 格式损坏

**表现**：index.md 列表中出现了 `||- [[xxx]]` 或 `||- [[xxx]]` 开头的行

**原因**：这是 markdown table 单元格内容的残留。当你复制/生成 wikilink 时，如果不小心在表格编辑器中操作或在 markdown 表格行的 `|` 分隔符后多加了 `-`，就会产生这种语法。Obsidian 不会渲染它，该条目会变成纯文本。

**修复**：用 `patch` 替换 `||- [[` 为 `- [[` 或直接删除整行。

### 2. 重复的 Source 区块

**表现**：同一个课程标题（如 `### 📁 Build Your Own Claude Code`）出现两次或更多次

**原因**：多个 subagent 同时 patch index.md，各自都添加了标题行

**修复**：用一个大 patch 删除整个重复区块，保留最后一个正确的

### 3. 章节标题错位

**表现**：BYOCC 的课程条目出现在 AI Apprenticeship 区块下

**原因**：patch 时缺少 `---` 分隔符导致标题解析错误

**修复**：在修复 (2) 后通常会自动恢复；如果不行，手动设置正确的 `---` 分隔

## 修复原则

- **一次大 patch 优先于多次小 patch** — 小 patch 容易踩到唯一性问题（多个 `---` 匹配不完全）
- **先读全文看结构**（read_file 不带 offset/limit），确认损坏范围
- **锚点用完整行文本**（如 `### 📁 Build Your Own Claude Code`），不要用部分匹配
- **修复后再次 read_file 全文验证**
- 永远不要在多个 subagent 之间共享 index.md 的写权限
