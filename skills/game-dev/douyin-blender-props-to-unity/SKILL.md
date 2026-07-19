---
name: douyin-blender-props-to-unity
description: Prepare and export Blender static game assets for Douyin Game Unity projects. Use for props, weapons, furniture, unrigged meshes, Collection batch exports, texture packing/export, material atlas baking, and Tripo model orientation or transform cleanup.
---

# Douyin Blender Props to Unity

Prepare static Blender assets for consistent Unity import. Do not use this skill for rigged characters, vertex-group cleanup, or skin weights; use `$douyin-blender-characters-to-unity` instead.

## Route the task

| Request | Read |
| --- | --- |
| Export one unrigged mesh, prop, weapon, or furniture item | `references/small-object-export.md` |
| Export multiple independent meshes from a Collection | `references/batch-collection-export.md` |
| Combine materials into one atlas and shared material | `references/material-atlas.md` |
| Convert a metallic texture into a roughness texture | `templates/tm_to_ts_copy.py` |

## Workflow

1. Inspect selected objects, object transforms, orientation, material nodes, image sources, and the target Unity folder.
2. Confirm whether textures should be embedded in the FBX or exported as external files, and whether a batch should preserve names or receive ordered names.
3. Save the `.blend`, then apply only the transform and texture changes needed for the selected export.
4. Export only intended objects. Keep selection and export in the same Blender/MCP execution block because selection state may not persist.
5. Verify the FBX and required texture files exist, then report Unity-side texture import settings.

## Guardrails

- Check imported Tripo meshes for non-zero Z rotation and non-unit scale before export. Apply or restore transforms only as directed by the selected reference.
- Limit texture saving or unpacking to the target asset; never rewrite every texture in the scene.
- Use `img.save()` for generated images that contain hand-painted pixels. Do not use `save_render()` where it could overwrite artwork.
- Treat transform application and atlas baking as destructive operations. Preserve a recovery point before running them.
- Use native Blender FBX export unless a project-specific requirement says otherwise.

## Bundled utility

`templates/tm_to_ts_copy.py` creates or updates a roughness texture from a metallic texture. Review and replace its material and node-name constants before executing it in Blender.
