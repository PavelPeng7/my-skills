#!/usr/bin/env python3
"""
字幕预处理脚本：批量剥离SRT元数据，按Section输出纯文本。
用法：修改下方 SECTIONS 和 LEVEL_DIRS 定义后运行。
输出：_preprocessed/section-{slug}.txt
"""

import os, re

# ============ 配置区域 ============

COURSE_DIR = "<COURSE_DIR>"
LEVEL_DIRS = {
    "L1": os.path.join(COURSE_DIR, "<Level 1>"),
    "L2": os.path.join(COURSE_DIR, "<Level 2>"),
}

SECTIONS = {
    "section-01": {"level": "L1", "videos": [(1, "Video Name")]},
}

# ============ 核心函数 ============

def strip_srt(srt_path):
    with open(srt_path, encoding='utf-8') as f:
        text = f.read()
    lines = text.split('\n')
    result = []
    for line in lines:
        line = line.strip()
        if re.match(r'^\d+$', line): continue
        if re.match(r'^\d{2}:\d{2}:\d{2}', line): continue
        if not line: continue
        result.append(line)
    return ' '.join(result)

def find_srt(level_dir, video_num):
    for f in sorted(os.listdir(level_dir)):
        if not f.endswith(('.srt', '.vtt')): continue
        base = os.path.splitext(f)[0]
        base_clean = re.sub(r'\.(en|zh|cn|en-US|zh-CN)$', '', base)
        if base_clean.startswith(f"{video_num}. ") or base_clean.startswith(f"{video_num} "):
            return os.path.join(level_dir, f)
    return None

def slugify(name):
    name = re.sub(r'[^\w\s-]', '', name.lower())
    return re.sub(r'[-\s]+', '-', name).strip('-')

# ============ 主逻辑 ============

def main():
    output_dir = os.path.join(COURSE_DIR, '_preprocessed')
    os.makedirs(output_dir, exist_ok=True)

    for sec_key, sec_info in SECTIONS.items():
        level_dir = LEVEL_DIRS[sec_info['level']]
        texts = []

        for vid_num, vid_name in sec_info['videos']:
            srt_path = find_srt(level_dir, vid_num)
            if not srt_path:
                print(f"WARNING: No SRT for video {vid_num} in {level_dir}")
                continue
            pure_text = strip_srt(srt_path)
            texts.append(f"== Video {vid_num}: {vid_name} ==\n{pure_text}")
            print(f"  OK: {vid_num}. {vid_name} ({len(pure_text)} chars)")

        slug = slugify(sec_key)
        output_path = os.path.join(output_dir, f"{slug}.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(texts))
        print(f"Section: {output_path} ({len(texts)} videos)")

if __name__ == '__main__':
    main()
