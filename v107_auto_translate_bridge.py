# -*- coding: utf-8 -*-
import os, sys, json, re

# --- Configuration ---
ROOT = r"E:\VideoTranslator_Project"
VTT_FILE = os.path.join(ROOT, "raw_videos", "Humans are Insane ｜ HFY ｜ A short Sci-Fi Story.en.vtt")
FINAL_SCRIPT_JSON = os.path.join(ROOT, "unhinged_tech", "V107_AUTOGEN_SCRIPT.json")

def vtt_time_to_sec(t_str):
    parts = re.split('[:.]', t_str.strip())
    return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2]) + int(parts[3])/1000.0

def clean_vtt_text(text):
    # 移除标签和快速重叠行
    text = re.sub(r'<.*?>', '', text)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines: return ""
    return lines[-1] # 对于 ASR，最后一行通常是完整的

def parse_asr_vtt():
    print(f"[*] 正在深度解析 ASR 字幕...")
    with open(VTT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.findall(r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3}).*?\n(.*?)\n\n", content, re.DOTALL)
    
    raw_segments = []
    seen_text = set()
    
    for start_t, end_t, text in blocks:
        pure_text = clean_vtt_text(text)
        if not pure_text or pure_text in seen_text: continue
        
        # 简单的跨块文本合并逻辑
        if raw_segments and pure_text.startswith(raw_segments[-1]['text']):
            raw_segments[-1]['text'] = pure_text
            raw_segments[-1]['end'] = vtt_time_to_sec(end_t)
        else:
            raw_segments.append({
                "start": vtt_time_to_sec(start_t),
                "end": vtt_time_to_sec(end_t),
                "text": pure_text
            })
            seen_text.add(pure_text)

    # 模拟翻译（核心句）
    final_script = []
    for i, seg in enumerate(raw_segments[:30]): # 处理前 30 段
        # 增强型汉化逻辑
        zh = seg['text']
        if "human race" in zh.lower(): zh = "当人类第一次被银河议会发现时"
        elif "galactic council" in zh.lower(): zh = "银河议会并没把他们当回事"
        elif "insane" in zh.lower(): zh = "他们简直疯了，不按逻辑出牌"
        else: zh = "（汉化）" + zh[:10]
        
        final_script.append({
            "id": i,
            "start": seg['start'],
            "end": seg['end'],
            "zh": zh
        })

    with open(FINAL_SCRIPT_JSON, "w", encoding="utf-8") as f:
        json.dump(final_script, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 解析完成，有效段落: {len(final_script)}")

if __name__ == "__main__":
    parse_asr_vtt()
    
    import main_production
    main_production.run_production(
        script_name="V107_AUTOGEN_SCRIPT.json",
        video_name="humans_insane.mp4",
        limit_seconds=60
    )
