from __future__ import annotations

import argparse
import json
import math
from collections import deque
from pathlib import Path
from typing import Iterable

from PIL import Image


def parse_hex_color(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Expected 6-digit hex color, got: {value}")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def sample_key_color(image: Image.Image) -> tuple[int, int, int]:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    points = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
    ]
    samples = [rgba.getpixel(point)[:3] for point in points]
    return tuple(sum(channel) // len(samples) for channel in zip(*samples))


def color_distance_sq(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return sum((x - y) * (x - y) for x, y in zip(a, b))


def remove_chroma(
    image: Image.Image,
    key_color: tuple[int, int, int],
    tolerance: int,
    despill: bool,
) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    tolerance_sq = tolerance * tolerance

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            if color_distance_sq((r, g, b), key_color) <= tolerance_sq:
                pixels[x, y] = (r, g, b, 0)
                continue
            if despill and g > r and g > b:
                g = max(r, b)
                pixels[x, y] = (r, g, b, a)
    return rgba


def build_mask(image: Image.Image, alpha_threshold: int) -> list[list[bool]]:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    return [[pixels[x, y][3] > alpha_threshold for x in range(width)] for y in range(height)]


def connected_components(mask: list[list[bool]], min_area: int) -> list[dict]:
    height = len(mask)
    width = len(mask[0]) if height else 0
    visited = [[False for _ in range(width)] for _ in range(height)]
    components: list[dict] = []

    for y in range(height):
        for x in range(width):
            if not mask[y][x] or visited[y][x]:
                continue

            queue = deque([(x, y)])
            visited[y][x] = True
            area = 0
            min_x = max_x = x
            min_y = max_y = y

            while queue:
                cx, cy = queue.popleft()
                area += 1
                min_x = min(min_x, cx)
                min_y = min(min_y, cy)
                max_x = max(max_x, cx)
                max_y = max(max_y, cy)

                for nx, ny in (
                    (cx - 1, cy),
                    (cx + 1, cy),
                    (cx, cy - 1),
                    (cx, cy + 1),
                ):
                    if nx < 0 or ny < 0 or nx >= width or ny >= height:
                        continue
                    if visited[ny][nx] or not mask[ny][nx]:
                        continue
                    visited[ny][nx] = True
                    queue.append((nx, ny))

            if area >= min_area:
                components.append(
                    {
                        "bbox": [min_x, min_y, max_x + 1, max_y + 1],
                        "area": area,
                    }
                )

    components.sort(key=lambda item: (item["bbox"][1], item["bbox"][0]))
    return components


def apply_padding(bbox: list[int], width: int, height: int, padding: int) -> list[int]:
    left, top, right, bottom = bbox
    return [
        clamp(left - padding, 0, width),
        clamp(top - padding, 0, height),
        clamp(right + padding, 0, width),
        clamp(bottom + padding, 0, height),
    ]


def read_names(path: Path | None) -> list[str]:
    if path is None:
        return []
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line]


def unique_name(name: str, used: set[str]) -> str:
    candidate = name
    index = 2
    while candidate in used:
        candidate = f"{name}_{index}"
        index += 1
    used.add(candidate)
    return candidate


def save_manifest(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


# ── 9-slice (九宫格) splitting ──────────────────────────────────────────

REGION_NAMES = [
    ("tl", "top-left"),
    ("tc", "top-center"),
    ("tr", "top-right"),
    ("ml", "middle-left"),
    ("mc", "middle-center"),
    ("mr", "middle-right"),
    ("bl", "bottom-left"),
    ("bc", "bottom-center"),
    ("br", "bottom-right"),
]


def nine_slice_split(
    image: Image.Image,
    border_top: int,
    border_bottom: int,
    border_left: int,
    border_right: int,
    output_dir: Path,
    prefix: str = "",
) -> dict:
    """Split image into 9 regions by border insets (九宫格).

    border_* values are pixel distances from the respective edges.
    Returns a dict with border values and per-region metadata suitable for Unity Sprite Editor.
    """
    width, height = image.size

    if border_top + border_bottom >= height:
        raise ValueError(
            f"border_top({border_top}) + border_bottom({border_bottom}) >= height({height})"
        )
    if border_left + border_right >= width:
        raise ValueError(
            f"border_left({border_left}) + border_right({border_right}) >= width({width})"
        )

    xs = [0, border_left, width - border_right, width]
    ys = [0, border_top, height - border_bottom, height]

    regions: dict[str, list[int]] = {}
    stem_prefix = f"{prefix}_" if prefix else ""

    for row in range(3):
        for col in range(3):
            key, _label = REGION_NAMES[row * 3 + col]
            bbox = (xs[col], ys[row], xs[col + 1], ys[row + 1])
            if bbox[2] > bbox[0] and bbox[3] > bbox[1]:
                crop = image.crop(bbox)
                filename = f"{stem_prefix}{key}.png"
                crop.save(output_dir / filename)
                regions[key] = list(bbox)

    return {
        "border": {"l": border_left, "r": border_right, "t": border_top, "b": border_bottom},
        "regions": regions,
    }


def nine_slice_main(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image = Image.open(input_path).convert("RGBA")

    result = nine_slice_split(
        image,
        border_top=args.border_top,
        border_bottom=args.border_bottom,
        border_left=args.border_left,
        border_right=args.border_right,
        output_dir=output_dir,
        prefix=args.prefix or "",
    )

    # Unity-compatible manifest
    manifest = {
        "input": str(input_path),
        "output_dir": str(output_dir),
        "mode": "9slice",
        "source_size": {"w": image.size[0], "h": image.size[1]},
        "border": result["border"],
        "sprite_count": len(result["regions"]),
        "sprites": sorted(
            [
                {"name": f"{args.prefix}_{name}" if args.prefix else name, "bbox": bbox}
                for name, bbox in result["regions"].items()
            ],
            key=lambda s: s["name"],
        ),
    }
    save_manifest(output_dir / args.manifest_name, manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


# ── Grid (宫格) splitting ────────────────────────────────────────────────

def grid_split(
    image: Image.Image,
    rows: int,
    cols: int,
    output_dir: Path,
    prefix: str = "",
) -> dict:
    """Split image into a uniform rows×cols grid (四宫格/九宫格/custom)."""
    width, height = image.size
    cell_w = width // cols
    cell_h = height // rows

    sprites = []
    i = 1
    for r in range(rows):
        for c in range(cols):
            x1 = c * cell_w
            y1 = r * cell_h
            x2 = x1 + cell_w
            y2 = y1 + cell_h
            crop = image.crop((x1, y1, x2, y2))
            stem = f"{prefix}_{i:02d}" if prefix else f"{i:02d}"
            fname = f"{stem}.png"
            crop.save(output_dir / fname)
            sprites.append({
                "name": stem,
                "file": fname,
                "bbox": [x1, y1, x2, y2],
                "grid_pos": {"row": r, "col": c},
            })
            i += 1

    return {
        "grid": {"rows": rows, "cols": cols, "cell_w": cell_w, "cell_h": cell_h},
        "sprites": sprites,
    }


def grid_main(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image = Image.open(input_path).convert("RGBA")
    result = grid_split(image, args.grid_rows, args.grid_cols, output_dir, args.prefix or "")

    manifest = {
        "input": str(input_path),
        "output_dir": str(output_dir),
        "mode": "grid",
        "source_size": {"w": image.size[0], "h": image.size[1]},
        "grid": result["grid"],
        "sprite_count": len(result["sprites"]),
        "sprites": result["sprites"],
    }
    save_manifest(output_dir / args.manifest_name, manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


# ── Main ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Remove chroma key background and split sprites / 9-slice / grid split.")
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument(
        "--mode",
        choices=["chroma", "9slice", "grid"],
        default="chroma",
        help="Processing mode: chroma (default), 9slice, or grid (uniform rows×cols)",
    )

    # ── chroma mode args ──
    parser.add_argument("--key-color", default="", help="[chroma] Hex color, e.g. #00FF00. If omitted, sample corners.")
    parser.add_argument("--tolerance", type=int, default=70, help="[chroma] Chroma match tolerance")
    parser.add_argument("--alpha-threshold", type=int, default=8, help="[chroma] Alpha threshold used for splitting")
    parser.add_argument("--min-area", type=int, default=400, help="[chroma] Minimum connected area to keep")
    parser.add_argument("--padding", type=int, default=8, help="[chroma] Padding around crops")
    parser.add_argument("--names-file", default="", help="[chroma] Optional one-name-per-line file")
    parser.add_argument("--transparent-sheet-name", default="00_transparent_sheet.png", help="[chroma] Full-sheet filename")
    parser.add_argument("--despill", action="store_true", help="[chroma] Reduce green spill on preserved pixels")

    # ── 9slice mode args ──
    parser.add_argument("--border-top", type=int, default=0, help="[9slice] Border inset from top edge (pixels)")
    parser.add_argument("--border-bottom", type=int, default=0, help="[9slice] Border inset from bottom edge (pixels)")
    parser.add_argument("--border-left", type=int, default=0, help="[9slice] Border inset from left edge (pixels)")
    parser.add_argument("--border-right", type=int, default=0, help="[9slice] Border inset from right edge (pixels)")

    # ── grid mode args ──
    parser.add_argument("--grid-rows", type=int, default=2, help="[grid] Number of rows (default: 2)")
    parser.add_argument("--grid-cols", type=int, default=2, help="[grid] Number of columns (default: 2)")

    # ── shared ──
    parser.add_argument("--prefix", default="", help="Optional filename prefix for output sprites")
    parser.add_argument("--manifest-name", default="manifest.json")

    args = parser.parse_args()

    if args.mode == "9slice":
        if not any([args.border_top, args.border_bottom, args.border_left, args.border_right]):
            parser.error("9slice mode requires at least one --border-* value > 0")
        nine_slice_main(args)
        return

    if args.mode == "grid":
        grid_main(args)
        return

    # ── chroma mode (default) ──
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image = Image.open(input_path).convert("RGBA")
    key_color = parse_hex_color(args.key_color) if args.key_color else sample_key_color(image)
    transparent = remove_chroma(image, key_color, args.tolerance, args.despill)

    transparent_path = output_dir / args.transparent_sheet_name
    transparent.save(transparent_path)

    names = read_names(Path(args.names_file)) if args.names_file else []
    mask = build_mask(transparent, args.alpha_threshold)
    components = connected_components(mask, args.min_area)

    width, height = transparent.size
    used_names: set[str] = set()
    manifest_items = []

    for index, component in enumerate(components, start=1):
        bbox = apply_padding(component["bbox"], width, height, args.padding)
        crop = transparent.crop(tuple(bbox))

        if index <= len(names):
            stem = names[index - 1]
        else:
            stem = f"{index:02d}_sprite"
        stem = unique_name(stem, used_names)

        filename = f"{stem}.png"
        output_path = output_dir / filename
        crop.save(output_path)

        manifest_items.append(
            {
                "index": index,
                "name": stem,
                "file": filename,
                "bbox": bbox,
                "area": component["area"],
            }
        )

    manifest = {
        "input": str(input_path),
        "output_dir": str(output_dir),
        "mode": "chroma",
        "key_color": "#{:02X}{:02X}{:02X}".format(*key_color),
        "transparent_sheet": transparent_path.name,
        "sprite_count": len(manifest_items),
        "sprites": manifest_items,
    }
    save_manifest(output_dir / args.manifest_name, manifest)

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

