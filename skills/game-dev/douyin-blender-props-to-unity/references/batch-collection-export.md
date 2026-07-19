# Collection 批量导出到 Unity

> 来源: `batch-export-collection-to-unity`

## 适用场景

Blender Collection 中多个独立网格需要按空间位置排序命名并批量导出。

## 两种模式

### 模式 A：排序重命名导出（默认）

每次执行前问三个问题：
1. 排序方向 — 从小到大还是从大到小？
2. 命名格式 — 前缀 + 起始序号（如 shoes_0）
3. 排序轴 — X、Y 还是 Z？

### 模式 B：直接导出不重命名

用户说「不需要重命名」时使用。保持对象原名，所有文件放目标目录下。

## 目录结构

模式 A（broomstick1 格式）：
```
Meshes/{模型名_0}/final.fbx + {模型名_0}_basecolor.png
```

模式 B（flat 格式）：
```
TargetDir/floor1.fbx + floor1_basecolor.png
```

## 排序陷阱

位置归零后不能用 location 排序，要用网格世界边界框中心 X。

## Tripo 朝向陷阱

导出前检查所有模型 Z 旋转值，非零归零并烘焙。

## 贴图导出策略

- 导出贴图 → embed_textures=True + path_mode='COPY' + 贴图保存
- 只嵌入贴图 → embed_textures=True + path_mode='COPY' + 跳过贴图保存
- 只导网格 → embed_textures=False + path_mode='STRIP' + 跳过贴图保存

贴图保存用 img.filepath_raw 临时重定向 + img.save() + 恢复原路径。不用 img.save_render()。
