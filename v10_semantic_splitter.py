# -*- coding: utf-8 -*-
import json, os, re

def run_semantic_split():
    input_json = r"E:\VideoTranslator_Project\separated_audio\v9_FULL_CHINESE_SCRIPT.json"
    with open(input_json, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    new_script = []
    print(f"\n[Splitter] 正在对全篇进行【语义碎片化】处理...")

    for item in data:
        zh_text = item.get('zh_full', '').strip()
        if not zh_text: continue
        
        # 按照中文结束标点进行分割
        # 匹配 。 ！ ？ 和 换行
        segments = re.split(r'([。！？；]+)', zh_text)
        
        # 将分割出的内容和标点重新组合
        parts = []
        for i in range(0, len(segments)-1, 2):
            parts.append(segments[i] + segments[i+1])
        if len(segments) % 2 == 1 and segments[-1]: # 处理末尾没有标点的残余
            parts.append(segments[-1])

        # 重新分配时间轴 (线性插值算法)
        total_chars = len(zh_text)
        start_t = item['start']
        end_t = item['end']
        duration = end_t - start_t
        
        current_t = start_t
        for p in parts:
            p = p.strip()
            if not p: continue
            
            p_len = len(p)
            p_dur = (p_len / total_chars) * duration
            
            new_script.append({
                "start": round(current_t, 3),
                "end": round(current_t + p_dur, 3),
                "speaker": item.get('speaker', 'SPEAKER_00'),
                "zh": p
            })
            current_t += p_dur

    out_path = r"E:\VideoTranslator_Project\separated_audio\V10_RESEGMENTED_SCRIPT.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(new_script, f, ensure_ascii=False, indent=2)
    
    print(f"\n🏆 切分完成！剧本规模从 19 句进化为 {len(new_script)} 句短句。")
    print(f"数据已固化至: {out_path}")

if __name__ == "__main__":
    run_semantic_split()
