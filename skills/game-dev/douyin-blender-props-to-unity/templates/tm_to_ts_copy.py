"""
从 T_M_*（金属度）复制到 T_S_*（粗糙度），反转逻辑：
  Roughness = 1 - Metallic
  高金属 → 光滑（低粗糙），低金属 → 粗糙（高粗糙）

用法：
1. 修改 MAT_NAME（材质名），TM_IMAGE_NODE 和 TS_IMAGE_NODE
2. 在 Blender MCP 中用 exec(compile(open(path).read(), ...)) 执行
"""
import bpy, numpy as np

MAT_NAME = "tripo_mat_33fb9eee.001"
TM_NODE_NAME = "图像纹理.002"  # 连接的 Principled BSDF Metallic 输入的节点
TS_NODE_NAME = "图像纹理.003"  # 目标粗糙度贴图的节点

mat = bpy.data.materials.get(MAT_NAME)
if not mat:
    print(f"Material '{MAT_NAME}' not found")
else:
    nodes = mat.node_tree.nodes
    img_tm = nodes[TM_NODE_NAME].image if TM_NODE_NAME in nodes else None
    img_ts = nodes[TS_NODE_NAME].image if TS_NODE_NAME in nodes else None
    
    if not img_tm:
        print(f"T_M image not found via node '{TM_NODE_NAME}'")
    else:
        print(f"Source: {img_tm.name} ({img_tm.size[0]}x{img_tm.size[1]})")
        
        # 加载源像素
        tm_pixels = np.array(img_tm.pixels[:], dtype=np.float32)
        tm_pixels = tm_pixels.reshape(img_tm.size[0], img_tm.size[1], 4)
        
        if not img_ts:
            print("Creating T_S image...")
            img_ts = bpy.data.images.new("T_S_body", width=img_tm.size[0], height=img_tm.size[1], alpha=True)
        else:
            print(f"Target: {img_ts.name} ({img_ts.size[0]}x{img_ts.size[1]}) - overwriting")
        
        # 反转：Metallic R 通道 → Roughness
        metallic_r = tm_pixels[:, :, 0]
        roughness = 1.0 - metallic_r
        ts_data = np.zeros_like(tm_pixels)
        ts_data[:, :, 0] = roughness
        ts_data[:, :, 1] = roughness
        ts_data[:, :, 2] = roughness
        ts_data[:, :, 3] = 1.0
        
        img_ts.pixels = ts_data.flatten()
        img_ts.update()
        img_ts.colorspace_settings.name = 'Non-Color'
        
        # 验证采样点
        h, w = ts_data.shape[:2]
        for sy, sx in [(h // 4, w // 4), (h // 2, w // 2), (3 * h // 4, 3 * w // 4)]:
            print(f"  Sample ({sy},{sx}): M={tm_pixels[sy, sx, 0]:.4f} -> R={ts_data[sy, sx, 0]:.4f}")
        
        print("Done!")
