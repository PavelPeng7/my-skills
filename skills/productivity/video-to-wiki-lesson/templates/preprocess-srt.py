"""Phase 2: 字幕预处理 — 批量剥离 SRT 元数据 → 纯文本
使用前修改 SECTIONS 和 LEVEL_DIRS 定义即可。
"""
import re, os, json

LEVEL_DIRS = [
    ("Level 1", "B:/DownLoad/<COURSE>/Claude Code Mastery - Level 1"),
    ("Level 2", "B:/DownLoad/<COURSE>/Claude Code Mastery - Level 2"),
    ("Level 3", "B:/DownLoad/<COURSE>/Claude Code Mastery - Level 3"),
]

SECTIONS = {
    "L1-M01": {"title": "Section Title", "level": "Level 1", "slugs": ["1.1", "1.2", "1.3"]},
}

def strip_srt(srt_path):
    """Strip SRT metadata, return pure text."""
    with open(srt_path, encoding='utf-8') as f:
        text = f.read()
    lines = text.split('\n')
    result = []
    for line in lines:
        line = line.strip()
        if re.match(r'^\d+$', line): continue
        if re.match(r'^\d{2}:\d{2}:\d{2}', line): continue
        if re.match(r'^$', line): continue
        line = re.sub(r'<[^>]+>', '', line)
        result.append(line)
    return ' '.join(result)

def find_srt(num_prefix, level_dir):
    """Find .en.srt matching the numeric prefix."""
    for f in os.listdir(level_dir):
        if f.endswith('.en.srt'):
            base = f.replace('.en.srt', '').replace('(1)', '')
            if base.startswith(num_prefix + '.') or base.startswith(num_prefix + ' '):
                return os.path.join(level_dir, f)
    return None

def slugify(name):
    name = re.sub(r'^\d+\.\d+\.\s*', '', name)
    name = name.lower().replace(' ', '-').replace(',', '').replace("'", '').replace('.', '').replace('_', '-')
    name = re.sub(r'-+', '-', name)
    return name.strip('-')

# === 执行 ===
base = "B:/DownLoad/<COURSE>"
out_dir = f"{base}/_preprocessed"
os.makedirs(out_dir, exist_ok=True)
level_dirs = {l: d for l, d in LEVEL_DIRS}

all_videos = []
for sec_id, sec in SECTIONS.items():
    ldir = level_dirs[sec["level"]]
    texts = []
    for slug_prefix in sec["slugs"]:
        srt_path = find_srt(slug_prefix, ldir)
        if not srt_path:
            print(f"WARN: No SRT for {slug_prefix}")
            continue
        video_name = next(f.replace('.en.srt','').replace('(1)','') for f in os.listdir(ldir) 
                         if f.endswith('.en.srt') and (f.replace('.en.srt','').replace('(1)','').startswith(slug_prefix+'.') or f.replace('.en.srt','').replace('(1)','').startswith(slug_prefix+' ')))
        video_slug = slugify(video_name)
        texts.append(f"=== Video {video_name} ===\n{strip_srt(srt_path)}")
        all_videos.append({"section": sec_id, "num": slug_prefix, "name": video_name, "slug": video_slug, "level": sec["level"]})
    
    with open(f"{out_dir}/{sec_id}.txt", 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(texts))
    print(f"✅ {sec_id}: {len(sec['slugs'])} videos")

with open(f"{out_dir}/video_manifest.json", 'w') as f:
    json.dump(all_videos, f, indent=2)
print(f"Done! {len(SECTIONS)} sections, {len(all_videos)} videos")
