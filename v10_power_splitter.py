# -*- coding: utf-8 -*-
import json, os, re

def run_power_split():
    input_json = r"E:\VideoTranslator_Project\separated_audio\v9_FULL_CHINESE_SCRIPT.json"
    with open(input_json, "r", encoding="utf-8-sig") as f: data = json.load(f)

    new_script = []
    print(f"\n[PowerSplit] 正在执行全方位标点捕捉与切分...")

    for item in data:
        zh = item.get('zh_full', '').strip()
        # 移除 [SPEAKER_00] 这种干扰前缀
        zh = re.sub(r'\[SPEAKER_\d+\]', '', zh).strip()
        if not zh: continue
        
        # 统一标点：将中英文所有逗号句号都视为潜在切分点
        # 尤其针对这种长段落解说，逗号也要切开
        parts = re.split(r'([。！？；.,!?;]+)', zh)
        
        rebuilt_parts = []
        for i in range(0, len(parts)-1, 2):
            rebuilt_parts.append(parts[i] + parts[i+1])
        if len(parts) % 2 == 1 and parts[-1]: rebuilt_parts.append(parts[-1])

        # 线性分配时间
        start_t, end_t = item['start'], item['end']
        duration = end_t - start_t
        total_len = len(zh)
        
        curr_t = start_t
        for p in rebuilt_parts:
            p = p.strip()
            if not p: continue
            p_dur = (len(p) / total_len) * duration
            new_script.append({
                "start": round(curr_t, 2),
                "end": round(curr_t + p_dur, 2),
                "speaker": item.get('speaker', 'SPEAKER_00'),
                "zh": p
            })
            curr_t += p_dur

    out_path = r"E:\VideoTranslator_Project\separated_audio\V10_POWER_SCRIPT.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(new_script, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 强力切分成功！剧本已进化为 {len(new_script)} 个高动态短句。")

if __name__ == "__main__":
    run_power_split()
