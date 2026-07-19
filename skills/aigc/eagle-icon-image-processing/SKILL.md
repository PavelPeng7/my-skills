---
name: eagle-icon-image-processing
description: >-
  Process game and Unity UI image assets with a repeatable local pipeline. Use when
  removing a flat chroma-key background, splitting a sprite sheet into transparent
  PNGs, exporting a 9-slice panel, slicing a regular grid, preserving stable asset
  names for Unity, or importing processed assets into an Eagle library. Trigger for
  requests involving green/magenta screen cleanup, UI sprite extraction, grid or
  9-slice slicing, sprite manifests, and Eagle asset-library organization.
---

# Asset Image Processing

Use the bundled Pillow script for deterministic chroma-key cleanup and slicing.
Read [the processing reference](references/cutout-and-split.md) before tuning
parameters. Read [the Eagle reference](references/eagle-library-management.md)
only for Eagle operations.

## Workflow

1. Inspect the source image: dimensions, background colour, transparency, intended
   sprite boundaries, and desired output names.
2. Choose one mode: `chroma`, `9slice`, or `grid`.
3. Export to a new output directory. Never overwrite source art.
4. Inspect the transparent sheet and several output sprites at full resolution.
5. Keep output names stable when replacing Unity assets so their `.meta` bindings
   remain valid. Configure Unity UI sprites without mipmaps unless the asset needs
   them.
6. Import the verified output into Eagle through its local API when requested.

## Commands

Run from this skill directory, or use absolute paths to the script and files.

### Remove a flat background and split connected sprites

```bash
python scripts/cutout_and_split.py --mode chroma \
  --input "raw.png" --output-dir "out" \
  --key-color "#00FF00" --despill
```

Omit `--key-color` to sample the image corners. For semitransparent art, use
`--alpha-threshold 2`; use the default `8` for crisp UI shapes. Adjust
`--tolerance`, `--min-area`, and `--padding` only after inspecting the result.
Provide `--names-file names.txt` when semantic names are known; use one name per
line in reading order.

### Export a 9-slice panel

```bash
python scripts/cutout_and_split.py --mode 9slice \
  --input "panel.png" --output-dir "out" \
  --border-top 32 --border-bottom 32 --border-left 24 --border-right 24
```

Measure each inset from the source edge. Ensure opposing borders leave a non-negative
centre region.

### Split a regular grid

```bash
python scripts/cutout_and_split.py --mode grid \
  --input "sheet.png" --output-dir "out" --grid-rows 2 --grid-cols 3
```

Use grid mode only when cells are equal-sized. Use chroma mode for irregularly spaced
sprites.

## Validation

Check that the output contains PNGs and `manifest.json`, verify no background remains
on the transparent sheet, and confirm every sprite has the expected padding and name.
For 9-slice exports, check every corner and edge at the intended UI scale. Do not
claim AI subject extraction or channel-based mattes are available through this skill;
they are not implemented by the bundled script.

## Eagle Safety

Prefer Eagle's `addFromPath` or `addFromPaths` local API for imports. Treat direct
`.library` edits as a last resort: back up `metadata.json` and `mtime.json`, update
both consistently, and have the user restart Eagle before verifying folder changes.

