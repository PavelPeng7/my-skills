# 角色模型导出到 Unity

> 来源: `blender-character-export-to-unity` (v1.5.0)

## 模型命名规范

导出前按 SamplePet01 风格重命名：

| 旧名称 | 新名称 | 示例 |
|--------|--------|------|
| Armature（通用名） | `{模型名}_Armature` | `paopao_Armature` |
| 子网格（body.002 等） | `{模型名}_{部位英文}` | `paopao_body` |

部位英文：body（身体）、limbs（四肢）、hands（手）、foots（脚）、eye（眼睛）、mouth（嘴巴）、tail（尾巴）

## 贴图命名规范

`T_类型_模型名[_序号]`：T_C_（Color）、T_M_（Metallic）、T_S_（Smoothness）、T_AO_（AO）、T_E_（Emission）、T_SAM_（Mask）

## 项目路径约定

| 项目 | 路径 |
|------|------|
| XiaoHuoRen 皮肤 | `XiaoHuoRen/Assets/SkyRocketSkin2/{模型名}/` |
| DouyingGameTemplate | `DouyingGameTemplate/Assets/{模型名}/` |
| SoccerGame 静态模型 | `BounsSoccer/Meshes/{模型名}.fbx` |

## 导出方式选择

| 方式 | 顶点组保留 | 贴图处理 |
|------|-----------|---------|
| 原生 FBX（默认） | use_mesh_modifiers=True → 可能触发 Auto Weights 再生 | path_mode='COPY' 复制 | 
| 原生 FBX 无贴图 | 同上 | path_mode='STRIP' 不碰贴图 |
| BetterFBX | ✅ 保留清理结果 | use_copy_texture=False |

## 完整导出脚本

见 `templates/export_to_unity.py`。

## XiaoHuoRen 皮肤导出（简化版）

仅导出 FBX 到 `SkyRocketSkin2/{模型名}/`，绝对禁止操作贴图像素数据。用 `img.save()` 而非 `save_render()`。

## Tripo 导入角色特征

- Armature scale 常为 0.01
- 子物体不一定齐全（body + hands 缺 foots 常见）
- 贴图 packed + 原始文件在临时路径
- 材质名 tripo_mat_{hash}，贴图名带描述性英文
- 金属度/粗糙度贴图常为 source='GENERATED'

## 关键陷阱

1. MCP 选择状态跨调用不持久 — 同一代码块内选择+导出
2. 贴图解包要限定目标角色材质，不要遍历全场景
3. source='GENERATED' 含手绘时用 img.save()，不用 save_render()
4. `save_render()` 从节点树重新计算覆盖手绘像素
5. 顶点组清理后原生 FBX 导出可能再生 → 优先 BetterFBX
6. 贴图操作前必须先保存 .blend
7. path_mode='COPY' 在临时文件不存在时静默失败

## 贴图安全准则

- 永远不直接修改原始贴图 .pixels
- 操作前保存 .blend
- 用 `img.copy()` 创建副本，对副本操作
- 需要 numpy 操作时，copy() 后再用
