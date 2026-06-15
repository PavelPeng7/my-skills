---
name: eagle-library-agent
description: >
  操作 Eagle 素材资源库（.library 格式）。当用户提到 Eagle 资源库、素材库、Eagle 仓库、素材管理，或要在 Eagle 中搜索/查询/统计/整理/归类素材，或说「在 Eagle 中找 X」「统计 Eagle 库」「看 Eagle 文件夹结构」「建 Eagle 文件夹」时使用。
  覆盖文件夹树打印、关键词搜索、按类型过滤、统计概览、导出清单、文件夹管理（建/删/归类）。
  支持小火人共创互利资源库和问尔美术库。
  只要涉及 Eagle 库的读或写，就用这个 skill——不要用通用文件工具直接读 metadata.json。
---

# Eagle 资源库 Agent

## Overview

操作 Eagle 设计素材资源库（`.library` 目录格式）。Eagle 库本质是一个目录，包含：
- `metadata.json` — 文件夹树结构和库元数据
- `images/*.info/metadata.json` — 每个资源的详细信息
- `images/*.info/*_thumbnail.png` — 缩略图
- `images/*.info/` — 实际资源文件（原始文件）
- `tags.json` — 全局标签
- `mtime.json` — 修改时间索引

## 已知 Eagle 库路径

| 名称 | 路径 |
|------|------|
| 小火人共创互利资源库 | `B:\BaiduAsync\BaiduSyncdisk\小火人共创互利资源库.library` |
| 问尔美术库 | `B:\BaiduAsync\BaiduSyncdisk\问尔美术库.library` |

## 关键约束（先读这个）

1. **建文件夹 → 用户重启 Eagle 才能看到**。metadata.json 的文件夹树只在启动时加载，运行时 Eagle 不热加载。
2. **任何写 metadata.json 的操作必须同步更新 mtime.json**。Eagle 通过 mtime.json 检测变更，漏掉它 = 白改。
3. **修改前先备份** metadata.json 和 mtime.json（加 `.bak` 后缀）。格式损坏会导致 Eagle 无法打开库。
4. **不要用 Eagle API 写文件夹**。Eagle 4.0.0 的 `/api/folder/create` 有 bug（parent 参数不生效，文件夹跑到根目录）。
5. **文件夹操作优先让用户手动在 Eagle GUI 中做**。AI 写入 metadata.json 是备选方案，前提是用户理解需要重启。
6. **中文路径** — 务必用 `r"B:\..."` 或 POSIX 风格。小火人库约 1500+ 项，用 `limit` 限制搜索返回数量。
7. **多文件夹归属** — `folders` 是数组，一个资源可属于多个文件夹。

## 核心操作

### 0. 基本加载与目录映射

```python
import json, os, glob

LIBRARY_PATH = r"B:\BaiduAsync\BaiduSyncdisk\小火人共创互利资源库.library"
images_dir = os.path.join(LIBRARY_PATH, 'images')

# 映射文件夹 ID -> 完整路径名
def map_folders(folders, parent=""):
    result = {}
    for f in folders:
        name = f"{parent}/{f['name']}" if parent else f['name']
        result[f['id']] = name
        if f.get('children'):
            result.update(map_folders(f['children'], name))
    return result

with open(os.path.join(LIBRARY_PATH, 'metadata.json'), 'r', encoding='utf-8') as fp:
    meta = json.load(fp)
folder_map = map_folders(meta['folders'])
```

### 1. 搜索素材 (search)

按关键词/文件名/类型/文件夹搜索资源：

```python
def search_items(keyword=None, ext=None, folder_path=None, limit=30):
    results = []
    for d in glob.glob(os.path.join(images_dir, '*.info')):
        meta_path = os.path.join(d, 'metadata.json')
        if not os.path.exists(meta_path):
            continue
        with open(meta_path, 'r', encoding='utf-8') as fp:
            item = json.load(fp)
        if item.get('isDeleted'):
            continue
        if keyword:
            kw = keyword.lower()
            name = item.get('name', '').lower()
            anno = item.get('annotation', '').lower()
            if kw not in name and kw not in anno:
                continue
        if ext and item.get('ext', '').lower() != ext.lower():
            continue
        if folder_path:
            item_folders = [folder_map.get(fid, '') for fid in item.get('folders', [])]
            if not any(folder_path in f for f in item_folders):
                continue
        results.append(item)
        if len(results) >= limit:
            break
    return results
```

### 2. 统计概览 (stats)

```python
def get_stats():
    folder_counts = {}
    type_counts = {}
    total = 0
    for d in glob.glob(os.path.join(images_dir, '*.info')):
        meta_path = os.path.join(d, 'metadata.json')
        if not os.path.exists(meta_path):
            continue
        with open(meta_path, 'r', encoding='utf-8') as fp:
            item = json.load(fp)
        if item.get('isDeleted'):
            continue
        total += 1
        ext = item.get('ext', '?')
        type_counts[ext] = type_counts.get(ext, 0) + 1
        for fid in item.get('folders', []):
            fn = folder_map.get(fid, '未归类')
            folder_counts[fn] = folder_counts.get(fn, 0) + 1
    return {'total': total, 'by_folder': folder_counts, 'by_type': type_counts}
```

### 3. 查询详情 (detail)

```python
def get_item_detail(item_id_or_name):
    for d in glob.glob(os.path.join(images_dir, '*.info')):
        meta_path = os.path.join(d, 'metadata.json')
        if not os.path.exists(meta_path):
            continue
        with open(meta_path, 'r', encoding='utf-8') as fp:
            item = json.load(fp)
        if item['id'] == item_id_or_name or item.get('name', '') == item_id_or_name:
            return item
    return None
```

资源详情包含：`id`, `name`, `ext`, `size`, `url`, `annotation`, `tags`, `folders`, `palettes`, `width`/`height`, `btime`/`mtime`, `fontMetas`, `lastModified`。

### 4. 文件夹树 (tree)

```python
def print_tree(folders=None, indent=0):
    if folders is None:
        folders = meta['folders']
    for folder in folders:
        ts = folder.get('modificationTime', 0)
        dt = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d') if ts else ''
        print(f"{'  ' * indent}📁 {folder['name']}  [{dt}]")
        if folder.get('children'):
            print_tree(folder['children'], indent + 1)
```

### 5. 导出清单 (export)

```python
def export_inventory(folder_path=None, format='text'):
    items = []
    for d in glob.glob(os.path.join(images_dir, '*.info')):
        meta_path = os.path.join(d, 'metadata.json')
        if not os.path.exists(meta_path):
            continue
        with open(meta_path, 'r', encoding='utf-8') as fp:
            item = json.load(fp)
        if item.get('isDeleted'):
            continue
        if folder_path:
            item_folders = [folder_map.get(fid, '') for fid in item.get('folders', [])]
            if not any(folder_path in f for f in item_folders):
                continue
        items.append(item)
    groups = {}
    for item in items:
        fnames = [folder_map.get(fid, '未归类') for fid in item.get('folders', [])]
        for fn in fnames:
            groups.setdefault(fn, []).append(item)
    return groups, items
```

### 6. 本地 Eagle API（只读可靠，写操作有 bug）

Eagle 运行时提供本地 HTTP API（默认 `localhost:41595`）。API Token 从 `/api/application/info` 的 `preferences.developer.apiToken` 获取。

```python
import urllib.request, json

TOKEN = '3c522852-b095-455b-9da4-753c6589687f'
BASE = 'http://localhost:41595'

def eagle_api(endpoint, data=None):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f'{BASE}{endpoint}', data=body, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=10).read())
```

#### 已验证可用的 API 端点

| 端点 | 用途 | 可靠性 |
|------|------|--------|
| `GET /api/application/info` | 获取 Eagle 版本、preferences、apiToken | ✅ |
| `GET /api/library/info` | 获取完整文件夹树（比读 metadata.json 快） | ✅ |
| `GET /api/folder/list` | 获取根目录文件夹列表 | ✅ |

#### 已验证不可靠的 API 端点

`/api/folder/create` 在 Eagle 4.0.0 有 bug：返回 `status: "success"` 但 `parent` 参数**不生效**。**不要用 API 建文件夹**。

### 7. 写操作通用规则

**任何修改 metadata.json 的操作，都必须同步更新 mtime.json**。修改前先备份。

```python
import shutil
shutil.copy(meta_path, meta_path + '.bak')
shutil.copy(mtime_path, mtime_path + '.bak')
```

#### 归类资源 (move_to_folder)

```python
def move_to_folder(item_id, target_folder_id):
    for d in glob.glob(os.path.join(images_dir, '*.info')):
        meta_path = os.path.join(d, 'metadata.json')
        if not os.path.exists(meta_path):
            continue
        with open(meta_path, 'r', encoding='utf-8') as fp:
            item = json.load(fp)
        if item['id'] == item_id:
            item['folders'] = [target_folder_id]
            with open(meta_path, 'w', encoding='utf-8') as fp:
                json.dump(item, fp, ensure_ascii=False)
            mtime[item_id] = int(time.time() * 1000)
            mtime[target_folder_id] = int(time.time() * 1000)
            with open(mtime_path, 'w', encoding='utf-8') as fp:
                json.dump(mtime, fp, ensure_ascii=False, indent=2)
            return True
    return False
```

## 时间戳转换

Eagle 使用毫秒级 Unix 时间戳：
```python
from datetime import datetime
dt = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M')
```

## 补充说明

- **缩略图** — `images/*.info/` 目录下有 `*_thumbnail.png`，实际文件名是 `{id}{ext}` 如 `abc123.png`，不是 metadata 中的 `name`。
- **资源文件路径** — 原始文件位于 `images/{id}.info/` 目录下，文件名由 metadata.json 的 `name` + `.` + `ext` 拼接。
