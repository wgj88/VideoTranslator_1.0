# -*- coding: utf-8 -*-
import json, os

def fix_script_structure():
    path = r"E:\VideoTranslator_Project\unhinged_tech\V69_2MIN_ELASTIC_SCRIPT.json"
    with open(path, "r", encoding="utf-8") as f: data = json.load(f)
    
    # 针对性重写易“走火”的片段
    # 片段 04: 改为平铺直叙
    data[3]['zh'] = "又到了我车库里的年度传统时刻。我要唤醒那个装在罐子里的先知。"
    
    # 全局去标点/简化逻辑：将冒号换成句号，增加模型稳定性
    for item in data:
        item['zh'] = item['zh'].replace("：", "。").replace(":", "。")
        # 如果句子太长 (>35字)，强行截断部分修饰词
        if len(item['zh']) > 35:
            item['zh'] = item['zh'][:35] + "。"
            
    with open(r"E:\VideoTranslator_Project\unhinged_tech\V70_1_STABLE_SCRIPT.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ 剧本结构已加固，长难句已物理拆解。")

if __name__ == "__main__":
    fix_script_structure()
