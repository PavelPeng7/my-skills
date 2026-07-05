# 子代理 Context 优化 — 实测数据

## 实测对比

| Context写法 | input token | 子代理工具调用 |
|------------|------------|--------------|
| 只说"截图在目录，格式是..." | ~214K | 15次 search_files 验证 |
| 明确"不要验证"+slug表 | ~22K | read_file+write_file |
| slug表+toolset=['file'] | ~16K | read_file+write_file |

核心结论：让子代理不验证文件 = 省90% input token。

## 黄金模板

```python
context = f"""
用中文写图文笔记。

输入：{path}/section{N}.txt

截图已全部就绪，不要验证文件。直接写引用：
  ![[../../../assets/{course}/{slug}-{label}.jpg]]

slug表：
- Section Overview → section-overview(不放截图)
- XXXX → xxxx-slug（3张：overview, detail, result）

密度：Overview和Recap不放截图。其余每课3张。

输出：{vault}/sources/{course}/section-{N}-{slug}.md
"""
```

## 六条铁律

1. **slug表写死**：不让子代理计算
2. **声明"不要验证"**：阻止文件验证循环
3. **不放截图的单独列出**：避免找不存在的文件
4. **工具限制**：`toolsets=['file']` 不给search
5. **纯文本入参**：传预处理后的纯文本
6. **index.md由主代理统一更新**：子代理只写文章

## 反模式

```python
# ❌ 错误：让子代理自己找截图
context = "截图在 assets/ 目录，格式是 {视频名}-{序号}.jpg"

# ❌ 错误：让子代理判断截图密度
context = "根据需要自行决定截图密度"

# ❌ 错误：给全部工具（不限制 toolsets）
```
