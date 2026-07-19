# 材质 Atlas 烘焙

> 来源: `blender-material-atlas`

## 适用场景

多个独立 Blender mesh 的细分材质合并为一张 Atlas 贴图，共享一个材质。适用于 Unity/游戏引擎导入。

## 默认配置

- 贴图类型: BaseColor 仅
- Atlas 尺寸: 4096×4096
- 布局: 2×2（保留一角备用）
- 渲染器: Cycles（默认）
- 烘焙采样: 16 samples（120s MCP 超时限制）
- 对象: 保持独立不合并

## 工作流

1. 锁定烘焙范围（贴图类型、对象范围、atlas 布局）
2. 检查源材质和 UV
3. 创建 Atlas 图片数据块
4. 构建 Atlas UV（复制源 UV → 缩放/偏移到对应象限）
5. 准备烘焙节点（保持源材质不变，添加临时烘焙目标）
6. 逐个对象烘焙
7. 创建共享材质 M_Atlas_Combined
8. 清理临时节点，保存

## Tripo 模型特殊处理

用 EMIT bake 替代 DIFFUSE。必须创建两个图片节点（源+目标）避免循环依赖。

## 关键陷阱

- 已有 Atlas_UV 时先重命名为 Legacy 再重建
- 中文 Blender 下 `nodes.new(type='BSDF_PRINCIPLED')` 在空节点树会失败
- Cycles bake >120s 超时 → 降低采样到 16
- 对象只有 Atlas_UV 无 UVMap → 先 smart_project 重建 UVMap
- `active_render` 属性在 Blender 4.x 不存在
