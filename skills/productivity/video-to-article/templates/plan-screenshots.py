#!/usr/bin/env python3
"""
截图规划脚本：根据字幕+视频时长确定所有截图点，生成 ffmpeg 命令。
用法：修改下方 SECTIONS 和 LEVEL_DIRS 定义后运行。
输出：_screenshot_plan.json + _batch_screenshots.sh
"""

import os, json, subprocess, re

# ============ 配置区域 ============

COURSE_DIR = "<COURSE_DIR>"
LEVEL_DIRS = {
    "L1": os.path.join(COURSE_DIR, "<Level 1 dir>"),
    "L2": os.path.join(COURSE_DIR, "<Level 2 dir>"),
}

SECTIONS = {
    "S01": {
        "title": "<Section Title>",
        "level": "L1",
        "videos": [(1, "Video Name")],
    },
}

ASSET_DIR = "assets/<course-slug>/"

# ============ 截图策略 ============

def frames_for_duration(seconds, video_name=""):
    name_lower = video_name.lower()
    if any(kw in name_lower for kw in ['intro', 'overview', 'wrap-up', 'summary', 'recap']):
        return 0
    if seconds < 30: return 1
    elif seconds < 120: return 2
    else: return 3

def interpolate_timestamps(duration, frame_count):
    if frame_count == 0: return []
    if frame_count == 1: return [duration * 0.3]
    step = duration / (frame_count + 1)
    return [step * (i + 1) for i in range(frame_count)]

def get_video_duration(video_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
           '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def slugify(name):
    name = re.sub(r'[^\w\s-]', '', name.lower())
    return re.sub(r'[-\s]+', '-', name).strip('-')

# ============ 主逻辑 ============

def main():
    plan = {}
    ffmpeg_commands = []

    for sec_id, sec_info in SECTIONS.items():
        level_dir = LEVEL_DIRS[sec_info['level']]
        sec_plan = []

        for vid_num, vid_name in sec_info['videos']:
            video_path = None
            for f in os.listdir(level_dir):
                if f.endswith('.mp4') and (f.startswith(f"{vid_num}. ") or f.startswith(f"{vid_num}.")):
                    video_path = os.path.join(level_dir, f)
                    break

            if not video_path:
                print(f"WARNING: Video {vid_num} not found in {level_dir}")
                continue

            duration = get_video_duration(video_path)
            frame_count = frames_for_duration(duration, vid_name)
            timestamps = interpolate_timestamps(duration, frame_count)
            slug = slugify(vid_name)
            labels = ['overview', 'detail', 'result'][:frame_count]

            shots = []
            for ts, label in zip(timestamps, labels):
                filename = f"{slug}-{label}.jpg"
                shots.append({"timestamp": ts, "label": label, "filename": filename})
                ffmpeg_commands.append(
                    f'ffmpeg -y -ss {ts:.1f} -i "{video_path}" -frames:v 1 "{ASSET_DIR}{filename}"'
                )

            sec_plan.append({
                "video_num": vid_num, "video_name": vid_name,
                "duration": duration, "slug": slug,
                "frame_count": frame_count, "shots": shots
            })

        plan[sec_id] = {"title": sec_info['title'], "videos": sec_plan}

    with open(os.path.join(COURSE_DIR, '_screenshot_plan.json'), 'w') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    with open(os.path.join(COURSE_DIR, '_batch_screenshots.sh'), 'w') as f:
        f.write("#!/bin/bash\nset -e\n\n" + "\n".join(ffmpeg_commands) + "\n")

    total = sum(s['frame_count'] for sec in plan.values() for s in sec['videos'])
    print(f"Plan: {total} total screenshots")

if __name__ == '__main__':
    main()
