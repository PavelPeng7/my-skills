"""Phase 3: 截图规划 — 预计算全部截图 slug + ffmpeg 命令
使用前修改 level_dirs 和 sections 定义。
"""
import json, os, subprocess, re

base = "B:/DownLoad/<COURSE>"

sections = {
    "L1-M01": {"title": "Section Title", "dir": "section-slug", "level": "Level 1"},
}

level_dirs = {
    "Level 1": f"{base}/Course - Level 1",
}

asset_dir = "B:/GitHub/Obsadian/CourseWiki/assets/<course-slug>"
os.makedirs(asset_dir, exist_ok=True)

# --- helper: get_video_duration via ffmpeg ---
def get_video_duration(video_path):
    try:
        r = subprocess.run(['ffmpeg', '-i', video_path], capture_output=True, text=True, timeout=10)
        m = re.search(r'Duration:\s*(\d+):(\d+):(\d+)\.(\d+)', r.stderr)
        if m: return int(m[1])*3600 + int(m[2])*60 + int(m[3])
    except: pass
    return 60

# --- helper: get_video_path ---
def get_video_path(video_name, level):
    d = level_dirs[level]
    for c in [f"{d}/{video_name}.mp4", f"{d}/{video_name}(1).mp4"]:
        if os.path.exists(c): return c
    for f in os.listdir(d):
        if f.endswith('.mp4'):
            base_n = f.replace('.mp4','').replace('(1)','')
            if base_n == video_name: return os.path.join(d, f)
    return None

# --- helper: plan frames ---
def plan_frames(name, dur, is_intro):
    if is_intro: return []
    if dur < 30:   return [("overview", int(dur*0.3))]
    if dur < 120:  return [("overview", int(dur*0.3)), ("detail", int(dur*0.7))]
    return [("overview", int(dur*0.2)), ("detail", int(dur*0.5)), ("result", int(dur*0.8))]

def sec_to_hms(s):
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}.000"

def is_intro_video(name):
    return name.lower().startswith("intro ") or name.lower().startswith("intro m") or "wrap-up" in name.lower()

def slugify(name):
    name = re.sub(r'^\d+\.\d+\s*', '', name).strip().lstrip('. ')
    name = name.lower().replace(' ', '-').replace(',','').replace("'",'').replace('.','').replace('_','-')
    name = re.sub(r'-+', '-', name).strip('-')
    name = re.sub(r'^\d+-', '', name)
    return name

# --- main ---
with open(f"{base}/_preprocessed/video_manifest.json") as f:
    all_videos = json.load(f)

all_ffmpeg = []
screenshot_plan = []
per_sec = {}

for v in all_videos:
    name, slug, level = v["name"], v["slug"], v["level"]
    intro = is_intro_video(name)
    video_path = get_video_path(name, level)
    if not video_path: continue
    dur = get_video_duration(video_path)
    frames = plan_frames(name, dur, intro)
    for label, ts in frames:
        fn = f"{slug}-{label}.jpg"
        all_ffmpeg.append(f'ffmpeg -ss {sec_to_hms(ts)} -i "{video_path}" -vframes 1 -q:v 3 "{asset_dir}/{fn}" -y')
        screenshot_plan.append({"section": v["section"], "video_name": name, "slug": slug, "label": label, "filename": fn})
    per_sec[v["section"]] = per_sec.get(v["section"], 0) + len(frames)

# Write outputs
script_path = f"{base}/_batch_screenshots.sh"
with open(script_path, 'w') as f:
    f.write("#!/bin/bash\nmkdir -p \"" + asset_dir + "\"\n")
    for c in all_ffmpeg: f.write(c + "\n")
os.chmod(script_path, 0o755)

with open(f"{base}/_screenshot_plan.json", 'w') as f:
    json.dump(screenshot_plan, f, indent=2)

print(f"Total frames: {len(all_ffmpeg)}")
for sid, cnt in sorted(per_sec.items()):
    print(f"  {sid}: {cnt} frames")
print(f"Script: {script_path}")
