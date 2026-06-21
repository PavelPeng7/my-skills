# game-image-master Background Remover Reference

This note captures the parameter semantics that must be preserved when this skill says it matches:

`B:\GitHub\Others\game-image-master`

## Source files

- `app/components/BackgroundRemover.tsx`
- `app/lib/background-remover.ts`

## Supported cutout modes in that project

### AI mode

Model type:

```ts
export type AIModel = "isnet" | "isnet_fp16" | "isnet_quint8";
```

Preset mapping used by the UI:

- `标准` -> `isnet`
- `高性能` -> `isnet_fp16`
- `轻量` -> `isnet_quint8`

Meaning:

- `isnet`: balanced precision and speed
- `isnet_fp16`: faster, better for stronger devices
- `isnet_quint8`: lighter, better for weaker devices

Extra parameter:

- `edgeShrink?: number // 0-20 pixels`

The project applies `edgeShrink` after AI inference, not before.

### Color mode

Options:

```ts
interface RemoveBackgroundOptions {
  tolerance: number;        // 0-100
  contiguousOnly: boolean;
  targetColor?: { r: number; g: number; b: number };
  feather?: number;         // 0-20 pixels
  antiAlias?: boolean;
  seedPoints?: { x: number; y: number }[];
  edgeShrink?: number;      // 0-20 pixels
}
```

Behavior:

- default background color comes from the top-left pixel unless `targetColor` is provided
- `contiguousOnly` uses border flood fill
- `antiAlias` softens boundary transitions and blurs alpha slightly
- `edgeShrink` pulls the foreground edge inward
- `feather` softens the transparency falloff

### Channel mode

Options:

```ts
interface ChannelMattingOptions {
  channel: "red" | "green" | "blue" | "luminance" | "saturation";
  minThreshold: number;     // 0-255
  maxThreshold: number;     // 0-255
  invert: boolean;
  feather?: number;
  edgeShrink?: number;
}
```

Behavior:

- keeps pixels inside the selected threshold range
- applies a soft transition around threshold edges
- preserves existing alpha
- optionally applies `edgeShrink` and `feather` afterward

## Practical consequence for this skill

Do not collapse all of the above into a single fake `quality` number.

Instead:

- use AI preset names only for AI mode
- use thresholds and edge controls for channel mode
- use tolerance and flood-fill rules for color mode
