---
name: douyin-blender-characters-to-unity
description: Prepare Blender character skins for Douyin Game Unity projects. Use for rigged character and animation export, armature and mesh naming, character texture export, vertex-group cleanup, automatic weighting, and anatomical Spine or full-body weight repair, especially for Tripo-generated characters.
---

# Douyin Blender Characters to Unity

Prepare rigged character skins for Unity import. Use `$douyin-blender-props-to-unity` for static props, batch Collection exports, and material atlas baking.

## Route the task

| Request | Read |
| --- | --- |
| Export a rigged character, armature, skin, or animation | `references/character-export.md` |
| Keep or remove character vertex groups | `references/vertex-group-management.md` |
| Repair Spine, limb, or full-body weights | `references/anatomical-spine-weights.md` |
| Rename character armature and mesh parts | `scripts/rename_to_standard.py` |
| Export metallic, emission, or other non-base-color textures | `scripts/export_extra_textures.py` |

## Workflow

1. Inspect the armature hierarchy, mesh-part naming, transforms, material nodes, image sources, vertex groups, and target Unity folder.
2. Confirm export intent: Generic or Humanoid rig, whether animation is included, external versus embedded textures, and native FBX versus BetterFBX.
3. Save the `.blend` before editing textures, vertex groups, or weights. Keep a recovery copy before cleanup, auto weighting, or broad weight repainting.
4. Follow this order when applicable: auto weights → vertex-group cleanup → weight repair → texture export → FBX export.
5. Export only the intended armature and meshes in one Blender/MCP execution block. Verify the FBX and textures, then report the Unity Rig and texture import settings.

## Guardrails

- Calculate anatomical weight gradients from world-space Z, not an imported armature's local Z axis.
- Check Tripo armature scale and mesh orientation before export. Do not normalize an unusual scale without confirming the project expectation.
- Do not mass-unpack scene textures. Export only textures referenced by the selected character.
- Use `img.save()` for generated images containing hand-painted pixels; avoid `save_render()` if it could overwrite artwork.
- Prefer native FBX. Use BetterFBX only when it is specifically needed to preserve the cleaned vertex-group result.
- Treat automatic weights, vertex-group deletion, and weight painting as destructive. Inspect the affected parts and preserve a recovery point first.

## Bundled utilities

- `scripts/rename_to_standard.py`: rename an armature and mesh parts to the project naming pattern.
- `scripts/export_extra_textures.py`: export non-base-color images connected to character materials.

Review each script's example object names and paths before execution.
