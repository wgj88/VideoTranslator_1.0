# -*- coding: utf-8 -*-
import json, os, numpy as np
from sklearn.cluster import AgglomerativeClustering

def run_merge():
    json_path = r"E:\VideoTranslator_Project\unhinged_tech\offline_diarization.json"
    with open(json_path, "r", encoding="utf-8") as f: data = json.load(f)

    # 1. 搜集所有 Speaker 的统计数据
    spk_stats = {}
    for item in data:
        s = item.get('speaker', 'UNKNOWN')
        dur = item['end'] - item['start']
        spk_stats[s] = spk_stats.get(s, 0) + dur
    
    print("\n--- 📊 原始声纹分布统计 ---")
    sorted_spks = sorted(spk_stats.items(), key=lambda x: x[1], reverse=True)
    for s, d in sorted_spks[:10]:
        print(f"  {s}: 累计时长 {d:.2f}s")

    # 2. 暴力归并：强行聚类为 3 个主要角色 (主讲人, 备用角色A, 备用角色B)
    print("\n[Merge] 正在执行【暴力归并】手术，强行收缩为 3 角色方案...")
    # 注意：由于我们之前没存 embedding，我们直接根据时序和 ID 进行逻辑映射
    # 主讲人通常是 SPEAKER_00 或时长最长的那个
    top_3_spks = [s[0] for s in sorted_spks[:3]]
    
    for item in data:
        if item['speaker'] in top_3_spks:
            pass # 保持原样
        else:
            # 将所有“杂鱼”角色全部归并给时长最长的 SPEAKER_00 (通常是主持人)
            item['speaker'] = top_3_spks[0]
            
    # 3. 输出前 10 句台词供人工验收
    print("\n--- 📝 剧本预览 (前 10 句) ---")
    for i, item in enumerate(data[:10]):
        print(f"[{i:02d}] {item['speaker']} ({item['start']:.1f}s): {item['text']}")

    out_p = r"E:\VideoTranslator_Project\unhinged_tech\V48_MERGED_SCRIPT.json"
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 归并版剧本已产出：{out_p}")

if __name__ == "__main__":
    run_merge()
