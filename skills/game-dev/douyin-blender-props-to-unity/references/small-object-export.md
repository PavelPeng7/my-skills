# 静态小物件导出到 Unity

> 来源: `small-object-export-to-unity`

## 适用场景

无骨骼的独立网格（鞋子、道具、装饰品、武器、家具等）。

## 导出路径

| 项目 | 路径 |
|------|------|
| SoccerGame | `Assets/BounsSoccer/Meshes/{模型名}/` |
| XiaoHuoRen | `Assets/SkyRocketSkin2/{角色名}/` |
| DouyingGameTemplate (通用) | `Assets/Models/` |
| DouyingGameTemplate (Skyrocket) | `Assets/Skyrocket/Mesh/Rockets/{模型名}/` |

## 目录结构

两种命名风格可选：

**风格 A：通用固定名**（适用纯批量导出，统一文件名）
```
Assets/.../Meshes/{模型名}/
  final.fbx              ← 模型文件
  {模型名}_basecolor.png  ← 贴图
```

**风格 B：对象同名**（适用按序命名后直接导出）
```
Assets/.../Rockets/{对象名}/
  {对象名}.fbx            ← 模型文件（如 rocket_01.fbx）
  {对象名}_basecolor.png  ← 贴图
```

## 通用步骤

### 0. Tripo 朝向陷阱

Tripo 模型旋转值不统一，需检查 Z 旋转值并归零。首选用户手动 Ctrl+A → Rotation & Scale。

### 1. 变换烘焙

```python
orig_loc, orig_rot, orig_scale = obj.location.copy(), obj.rotation_euler.copy(), obj.scale.copy()
obj.location = (0,0,0); obj.rotation_euler = (0,0,0); obj.scale = (1,1,1)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# 导出后恢复
obj.location, obj.rotation_euler, obj.scale = orig_loc, orig_rot, orig_scale
```

### 2. 贴图处理

检查文件存在性 → 从内存写出（img.save()）或 shutil.copy2。img.save() 前必须检查 img.size[0] > 0 避免崩溃。

**Tripo 打包贴图**：Tripo 临时源文件（`AppData\Local\Temp\blender_*\tripo_convert_*\*.JPEG`）可能已被删除。但只要 img.packed_file is not None（像素已打包在 .blend 内），`img.save()` 仍然有效——直接从内存像素写出。不需要找源文件路径。写入前设置 `img.file_format = 'PNG'` 控制输出格式。

### 3. FBX 导出

默认 embed_textures=True。纯网格模式：embed_textures=False, path_mode='STRIP'。

## 导出集合（Export Collection）模式

当场景中有专用的 `export` 集合（Collection），内含已清理的模型副本（变换归零、旋转归零）时：

1. 从 `export` 集合取对象，按源编号（如 `rocket_07.001` → `07`）匹配目标文件夹
2. 不需要变换烘焙（副本已清理）
3. 贴图存盘用 `img.filepath_raw = fwd_slash_path`（用 `/` 正斜杠，避免 Windows 反斜杠引发 Blender `expected string` 错误）
4. 导出的 FBX 放入对应编号文件夹覆盖旧文件

```python
# 核心模式：从 export 集合按编号映射导出
import re, os
export_root = "G:/path/to/Unity/Assets/Skyrocket/Mesh/Rockets"
export_coll = bpy.data.collections.get('export')
export_rockets = list(export_coll.objects)
export_rockets.sort(key=lambda o: int(re.search(r'rocket_(\d+)', o.name).group(1)))

for obj in export_rockets:
    num = int(re.search(r'rocket_(\d+)', obj.name).group(1))
    dir_path = f"{export_root}/rocket_{num:02d}"
    os.makedirs(dir_path, exist_ok=True)
    # 存贴图
    for slot in obj.material_slots:
        mat = slot.material
        if mat and mat.node_tree:
            for n in mat.node_tree.nodes:
                if n.type == 'TEX_IMAGE' and n.image:
                    n.image.filepath_raw = f"{dir_path}/rocket_{num:02d}_basecolor.png"
                    n.image.file_format = 'PNG'
                    n.image.save()
    # 导 FBX
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=f"{dir_path}/rocket_{num:02d}.fbx",
        use_selection=True, embed_textures=True, path_mode='COPY',
        axis_forward='-Z', axis_up='Y', bake_space_transform=True,
        mesh_smooth_type='FACE', use_mesh_modifiers=True, object_types={'MESH'}
    )
```

## 用户决策树

- **「不要导出贴图」** → 跳过贴图保存，embed_textures=False, path_mode='STRIP'
- **「导出贴图」** → 先保存贴图，再 embed_textures=True
- **「重新导出」** → 用上次设置直接重导，不询问不输出 verbose
