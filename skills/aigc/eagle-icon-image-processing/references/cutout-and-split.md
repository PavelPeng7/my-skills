# Processing Reference

The bundled `scripts/cutout_and_split.py` uses Pillow and has three modes:
`chroma`, `9slice`, and `grid`.

## Chroma mode

Remove pixels close to a flat key colour, optionally reduce green spill, then split
the remaining opaque regions into separate PNGs. Output ordering is top-to-bottom,
then left-to-right.

| Option | Default | Use |
|---|---:|---|
| `--key-color` | Corner sample | Hex key colour, such as `#00FF00` |
| `--tolerance` | `70` | Colour-distance threshold; raise carefully for uneven keys |
| `--alpha-threshold` | `8` | Split threshold; use `2` for soft or semitransparent art |
| `--min-area` | `400` | Ignore smaller connected regions |
| `--padding` | `8` | Transparent pixels retained around each crop |
| `--names-file` | — | One output name per line, in output order |
| `--transparent-sheet-name` | `00_transparent_sheet.png` | Full cleaned sheet name |
| `--despill` | off | Reduce green spill on retained pixels |

Use a lower tolerance if foreground edges disappear. Use a higher tolerance only if
the background remains visible; it can erase similarly coloured foreground pixels.

## 9-slice mode

Provide one or more pixel insets: `--border-top`, `--border-bottom`,
`--border-left`, and `--border-right`. The script exports the populated regions and
a manifest. Ensure horizontal and vertical border pairs do not exceed the image size.

## Grid mode

Set `--grid-rows` and `--grid-cols` (both default to `2`). Use only when the source
can be divided into equal cells; inspect results when its dimensions do not divide
cleanly. Use `--prefix` to namespace filenames and `--manifest-name` to change the
manifest filename.

## Unity notes

Use PNG output with alpha. For UI sprites, disable mipmaps unless they are needed.
Keep filenames stable when replacing existing Unity assets because Unity associates
import settings and references through `.meta` files.

