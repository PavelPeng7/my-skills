# 顶点组管理

> 来源: `vertex-group-manager-presets` (v1.0.0)

## 适用场景

Tripo 导入模型的顶点组清理 — 批量保留核心骨骼组、删除多余顶点组。

## 两种操作模式

### 模式 A：仅保留列表中的组（body 部位）

保留 4 核心组：pet_Sp_Hair1, pet_Sp_Hair2, pet_Sp_Spine, pet_Sp_hips2

### 模式 B：删除列表中的组（limbs/hands/feet 部位）

删除 7 组：pet_Sp_Hair1/2, pet_Sp_Spine, pet_Sp_hips2, pet_Eye_R/L, pet_Mouth

## MCP 上下文 fallback

vg_manager operator 在 MCP 中 poll() 可能失败。直接用 API fallback：

```python
def keep_vg_direct(obj, names_to_keep):
    to_remove = [vg.name for vg in obj.vertex_groups if vg.name not in names_to_keep]
    for name in to_remove:
        vg = obj.vertex_groups.get(name)
        if vg: obj.vertex_groups.remove(vg)

def delete_vg_direct(obj, names_to_delete):
    actual = [n for n in names_to_delete if n in [vg.name for vg in obj.vertex_groups]]
    for name in actual:
        vg = obj.vertex_groups.get(name)
        if vg: obj.vertex_groups.remove(vg)
```

## ⚠️ Body 覆盖范围预检

body 的 keep-list 不能盲目用 4 组。检查 body 网格 X 半幅：≤0.10 仅躯干（4 组），>0.10 延伸至肩部（需 6 组含 Shoulder_R/L）。

用户偏好覆盖：永远只保留 4 组，不询问。

## 完成管道

顶点组清理 → 权重绘制（anatomical-spine-weights）→ FBX 导出到 Unity

## 关键陷阱

- 清理前先通过 armature 绑定确认 mesh→armature 关系，不依赖命名猜测
- 清理后导出 FBX 可能触发 Auto Weights 重新生成顶点组（use_mesh_modifiers=True）
- limbs 的 ARMATURE modifier 可能指向空对象，导出前清理
- foots/hands/limbs 只做 vg_manager 删除操作，不做权重绘制/镜像
- 从参考物体复制顶点组结构恢复后补 Eye_R/L/Mouth
