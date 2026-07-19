"""
导出角色材质中所有连接到 Principled BSDF 金属度/自发光等输入的贴图。
适用于 GENERATED / packed / 外部文件 三种贴图类型。

用法：
1. 修改 MODEL_NAME 和 ARMATURE_NAME
2. 在 Blender MCP 中用 exec(compile(open(path).read(), ...)) 执行
"""
import bpy, os

MODEL_NAME = "manman"
ARMATURE_NAME = "manman"
UNITY_ROOT = "G:\\AllInOne\\002_Processing\\022_Projects\\Unity\\XiaoHuoRen"
tex_dir = os.path.join(UNITY_ROOT, "Assets", "SkyRocketSkin2", MODEL_NAME)
os.makedirs(tex_dir, exist_ok=True)

arm = bpy.data.objects.get(ARMATURE_NAME)
exported = 0

for c in arm.children:
    if c.type == 'MESH':
        for slot in c.material_slots:
            if slot.material and slot.material.node_tree:
                mat = slot.material
                for node in mat.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        for inp in node.inputs:
                            if inp.is_linked:
                                link = inp.links[0]
                                src = link.from_node
                                if src.type == 'TEX_IMAGE' and src.image:
                                    img = src.image
                                    img.reload()
                                    dst = os.path.join(tex_dir, img.name)
                                    
                                    if img.packed_file:
                                        raw = img.packed_file.data
                                        if raw[0] == 255 and raw[1] == 216:
                                            dst += ".jpeg"
                                        elif raw[1] == 80 and raw[2] == 78:
                                            dst += ".png"
                                        else:
                                            dst += ".png"
                                        with open(dst, 'wb') as f:
                                            f.write(raw)
                                    elif img.source == 'GENERATED':
                                        dst += ".png"
                                        # 优先 save() 保留手绘像素，回退 save_render()
                                        try:
                                            img.filepath_raw = dst
                                            img.save()
                                        except:
                                            img.save_render(dst)
                                    else:
                                        src_path = bpy.path.abspath(img.filepath_raw)
                                        if src_path and os.path.exists(src_path):
                                            _, ext = os.path.splitext(src_path)
                                            dst += ext
                                            import shutil
                                            shutil.copy2(src_path, dst)
                                        else:
                                            dst += ".png"
                                            # 优先 save() 保留手绘像素，回退 save_render()
                                            try:
                                                img.filepath_raw = dst
                                                img.save()
                                            except:
                                                img.save_render(dst)
                                    
                                    size = os.path.getsize(dst) / 1024 if os.path.exists(dst) else 0
                                    print(f"Exported {inp.name} -> {os.path.basename(dst)} ({size:.1f} KB)")
                                    exported += 1

print(f"\nTotal exported: {exported}")
