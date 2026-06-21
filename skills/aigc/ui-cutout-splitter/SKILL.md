---
name: ui-cutout-splitter
description: Remove chroma-key backgrounds and split UI sheets into reusable sprites for Unity or game UI pipelines. Use this skill whenever the user asks to cut out green-screen or magenta-background assets, split a sprite sheet or UI breakdown board, extract transparent PNGs, rename cut pieces by content, or turn AI-generated UI boards into importable game assets.
---

# UI Cutout Splitter

Use this skill for local raster asset processing workflows such as:

- removing green-screen or magenta chroma backgrounds
- splitting a sprite sheet, UI breakdown board, or asset board into separate PNGs
- renaming extracted sprites by content instead of generic numbering
- preparing AI-generated UI boards for Unity import

This skill is designed for practical local workflows first. Prefer deterministic local processing over asking the model to manually crop assets one by one.

## Reference behavior to preserve

This skill explicitly mirrors the background-removal parameter semantics used in:

`B:\GitHub\Others\game-image-master`

When the user asks for low, medium, or high cutout quality, do not invent a generic percentage scale. Preserve that tool's actual model mapping and option meanings.

## What this skill produces

Typical outputs:

- one transparent full-sheet PNG
- multiple cropped transparent PNG sprites
- one `manifest.json` describing names, bounding boxes, and output files

## Default workflow

1. Inspect the input image and identify:
   - background color: usually `#00FF00` or `#FF00FF`
   - whether the board contains separable non-overlapping elements
   - whether semantic renaming is possible from visible content
2. Choose an output folder inside the project, usually under `Assets/...`.
3. If semantic names are obvious, prepare a names file ordered top-to-bottom, then left-to-right.
4. Run the bundled script:
   - remove chroma background
   - split connected visible regions
   - save transparent crops
   - write `manifest.json`
5. Verify counts, crop quality, and naming.
6. If the project is Unity, keep filenames stable and import as `Sprite (2D and UI)`.

## Processing modes

This skill supports three conceptual cutout modes. Keep them distinct.

### 1. AI cutout

Use when the user wants automatic subject extraction and does not want to hand-pick colors or thresholds.

Presets must map exactly like `game-image-master`:

- `medium` or `standard` -> `isnet`
- `high` -> `isnet_fp16`
- `low` or `light` -> `isnet_quint8`

Reference source:

- `B:\GitHub\Others\game-image-master\app\components\BackgroundRemover.tsx`
- `B:\GitHub\Others\game-image-master\app\lib\background-remover.ts`

UI labels in that project:

- `标准`: balanced precision and speed
- `高性能`: faster, needs better hardware
- `轻量`: suitable for lower-end devices

Additional AI option:

- `edgeShrink`: `0-20` pixels, applied after model inference to pull the foreground edge inward and remove leftover fringe

Important:

- Do not reinterpret `high|medium|low` as output compression quality.
- Do not apply these presets to chroma-key or channel-matting flows.
- If the environment cannot run the browser-oriented AI model locally, say so clearly and fall back to color or channel mode only if that still matches the user's image type.

### 2. Channel matting

Use for green screen, blue screen, white paper with dark ink, or cases where foreground/background separate clearly in a single channel.

Parameters mirrored from `game-image-master`:

- `channel`: `red | green | blue | luminance | saturation`
- `minThreshold`: `0-255`
- `maxThreshold`: `0-255`
- `invert`: boolean
- `feather`: edge softening
- `edgeShrink`: inward edge cleanup

### 3. Color / chroma cutout

Use for flat keyed backgrounds or boards where a known background color should become transparent.

Parameters mirrored from `game-image-master` color mode:

- `tolerance`: `0-100`
- `contiguousOnly`: whether to remove only connected background regions
- `targetColor`: optional explicit key color
- `antiAlias`: default on
- `seedPoints`: optional extra flood-fill starts
- `feather`: `0-20`
- `edgeShrink`: `0-20`

## Bundled script

Use the bundled helper:

`scripts/cutout_and_split.py`

The script:

- loads a source image
- samples or accepts a key color
- removes the chroma background into alpha
- splits visible connected components
- sorts components top-to-bottom, then left-to-right
- saves crops as transparent PNGs
- optionally applies semantic names from a text file
- writes a JSON manifest

The bundled Python script is the deterministic local path for chroma cutout and splitting. It is the default fallback when the browser-oriented AI workflow from `game-image-master` is unavailable in the current environment.

## Command pattern

From the project root:

```powershell
python .codex\skills\ui-cutout-splitter\scripts\cutout_and_split.py `
  --input "Assets\Skyrocket\Textures\UI\raw_plotui.png" `
  --output-dir "Assets\Skyrocket\Textures\UI\PlotSystem" `
  --key-color "#00FF00" `
  --transparent-sheet-name "00_raw_plotui_transparent.png" `
  --min-area 800 `
  --padding 8 `
  --names-file ".codex\skills\ui-cutout-splitter\temp\names.txt"
```

If no names file is provided, the script falls back to:

`01_sprite.png`, `02_sprite.png`, ...

## Naming workflow

When the user asks to rename by content:

1. Inspect the image first.
2. Build a short ordered names list.
3. Save one line per output, in the same order the script will emit crops.
4. Re-run the split using `--names-file`.

The sort order is:

- primary: top edge ascending
- secondary: left edge ascending

Keep names short, stable, lowercase, and underscore-separated.

Good examples:

- `tab_plot_list`
- `tab_visit_messages`
- `panel_main_blue`
- `card_white_slot`
- `button_apply_visit`
- `frame_avatar_ring`

Avoid:

- `final_button_really_good`
- `thing1`
- localized filenames unless the project explicitly prefers them

## Preset restoration rule

If the user says any of the following:

- `高档`
- `中档`
- `低档`
- `高质量抠图`
- `轻量抠图`
- `标准抠图`

map them like this unless the user overrides it explicitly:

- `高档` -> AI mode + `isnet_fp16`
- `中档` -> AI mode + `isnet`
- `低档` -> AI mode + `isnet_quint8`

If the user is clearly asking for green-screen cleanup rather than AI subject extraction, explain that these AI presets do not apply and use chroma or channel mode instead.

## When semantic renaming is unsafe

Do not guess aggressively. If the content is ambiguous:

- use generic names first
- keep the manifest
- note the ambiguity in the response

Examples:

- `11_badge_round_red`
- `12_panel_fragment_blue`

## Unity-specific guidance

When outputs are meant for Unity UI:

- write PNG with transparency
- avoid mipmaps for UI sprites
- prefer stable filenames because Unity `.meta` files bind by filename/path
- if replacing an existing asset, preserve the `.meta` file
- if creating new assets, place them in a feature folder such as `Assets/Skyrocket/Textures/UI/PlotSystem/`

## What to inspect in the reference project

When behavior needs to match `game-image-master`, inspect only the relevant files first:

- `app/lib/background-remover.ts`
- `app/components/BackgroundRemover.tsx`

Do not infer preset semantics from unrelated compression or transform tools in that repository.

## Report structure

When you finish, report:

1. input image path
2. output folder
3. background key used
4. number of extracted sprites
5. whether semantic renaming was applied
6. whether any crops looked merged, noisy, or ambiguous

## Practical rules

- Prefer local scripts over ad-hoc manual cropping.
- Prefer project output folders over temp-only results.
- If the user references an existing local CLI, inspect it first before replacing it.
- If that CLI does not support background removal or connected-component splitting, use the bundled script as fallback instead of blocking.
- Do not overwrite existing outputs unless the user clearly wants replacement.

## Example prompts

Example 1:

`Use this green-screen UI board, remove the background, split every element, and export to Assets/GamePlay/UI/PlotSystem.`

Example 2:

`Take this magenta-background icon sheet, cut it into transparent PNGs, and name them by content.`

Example 3:

`Process raw_plotui.png into separate sprites for Unity and give me a manifest.`
