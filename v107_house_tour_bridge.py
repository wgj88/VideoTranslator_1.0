# -*- coding: utf-8 -*-
"""
V107 Bridge (Official Sub Edition): Official ZH-Hans VTT -> Production
No translation needed - using official creator subtitles.
"""
import os, sys, json, re

# --- Configuration ---
ROOT = r"E:\VideoTranslator_Project"
# 寻找匹配的视频和官方中文字幕
VTT_FILE = os.path.join(ROOT, "raw_videos", "Is This the Best Modern House in the World？ (House Tour).zh-Hans.vtt")
VIDEO_FILE = "house_tour_ready.mp4" # 使用之前合并成功的 mp4 或原始分段

def vtt_time_to_sec(t_str):
    parts = re.split('[:.]', t_str.strip())
    return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2]) + int(parts[3])/1000.0

def clean_text(text):
    return re.sub(r'<.*?>', '', text).replace("\n", " ").strip()

def build_script():
    print(f"[*] 正在提取官方中文简体字幕: {os.path.basename(VTT_FILE)}")
    with open(VTT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配时间轴 (支持带样式标签的 ASR/Official 格式)
    blocks = re.findall(r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3}).*?\n(.*?)\n\n", content, re.DOTALL)
    
    script_data = []
    seen_text = set()
    
    for i, (start_t, end_t, text) in enumerate(blocks):
        pure_zh = clean_text(text)
        if not pure_zh or pure_zh in seen_text: continue
        
        # 针对豪宅视频的快速去重合并逻辑
        if script_data and pure_zh.startswith(script_data[-1]['zh']):
            script_data[-1]['zh'] = pure_zh
            script_data[-1]['end'] = vtt_time_to_sec(end_t)
        else:
            script_data.append({
                "id": len(script_data),
                "start": vtt_time_to_sec(start_t),
                "end": vtt_time_to_sec(end_t),
                "zh": pure_zh
            })
            seen_text.add(pure_zh)

    output_json = os.path.join(ROOT, "unhinged_tech", "V107_HOUSE_SCRIPT.json")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 官方中文脚本已生成，共 {len(script_data)} 段。")
    return output_json

if __name__ == "__main__":
    json_p = build_script()
    
    # 衔接生产线
    import main_production
    # 为了演示，处理前 60 秒的高清豪宅巡礼
    main_production.run_production(
        script_name="V107_HOUSE_SCRIPT.json",
        video_name="house_tour_ready.mp4", # 先用分段测试，确保画面存在
        bgm_name=None,
        srt_name=None,
        limit_seconds=60
    )
