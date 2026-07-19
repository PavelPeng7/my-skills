# Eagle Library Reference

Use Eagle's local API for normal imports. Its base URL is normally
`http://localhost:41595`; obtain the token from `GET /api/application/info` and
authenticate as Eagle requires.

| Endpoint | Purpose |
|---|---|
| `GET /api/application/info` | Read the Eagle version and API token |
| `GET /api/library/info` | Read the library and folder tree |
| `POST /api/item/addFromPath` | Import one local asset |
| `POST /api/item/addFromPaths` | Import multiple local assets |

## Direct library edits

Avoid direct changes to a `.library` directory unless no suitable API operation exists.
The library includes `metadata.json`, `tags.json`, `mtime.json`, and per-item
`images/*.info/metadata.json` files.

Before writing, back up `metadata.json` and `mtime.json`. After writing, update the
mtime entries for every affected item and folder. `mtime.json` is a flat mapping:
newer versions usually store objects such as `{ "mtime": 1783240685743 }`, while
older libraries may store integer timestamps. Preserve the existing format and write
JSON with `ensure_ascii=False` and no forced indentation. Restart Eagle before
checking changes made directly on disk.

