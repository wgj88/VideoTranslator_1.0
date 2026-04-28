# -*- coding: utf-8 -*-
import os, sys, json, requests, re, subprocess
import numpy as np

# --- 环境补丁 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]
PROJECT_ROOT = r"E:\VideoTranslator_Project"
sys.path.append(PROJECT_ROOT)

def run_v50_director_cut():
    input_json = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")

    with open(input_json, "r", encoding="utf-8") as f: data = json.load(f)

    print(f"\n[V50-Director] 正在执行【配额感知】导演级重译...")

    final_script = []
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for i, item in enumerate(data):
        dur = item['end'] - item['start']
        # 标准商业语速：3.8 字/秒
        quota = max(3, int(dur * 3.8))
        
        prompt = f"""你是一个电影汉化导演。请将以下内容翻译成中文。
要求：
1. 【死命令】物理配额：{dur:.1f} 秒。你必须控制在约 {quota} 个汉字左右（绝对不能超过 {quota+1} 字）。
2. 字数不够就补虚词，字数超了就砍细节。
3. 标注情感标签：[excited/calm/serious]。

内容：{item['text']}
返回格式：{{"zh": "...", "mood": "..."}}
"""
        payload = {"model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1, "response_format": {"type": "json_object"}}

        try:
            r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers, timeout=20).json()
            content = json.loads(r['choices'][0]['message']['content'])
            item['zh'] = content['zh']
            item['mood'] = content['mood']
            final_script.append(item)
            print(f"  -> [{i+1}/{len(data)}] 配额 {quota} | 实际 {len(item['zh'])} | 标签: {item['mood']}: {item['zh']}")
        except:
            print(f"  ⚠️ 跳过 {i}")

    # 保存剧本
    script_v50 = os.path.join(PROJECT_ROOT, "temp_factory", "V50_DIRECTOR_SCRIPT.json")
    with open(script_v50, "w", encoding="utf-8") as f: json.dump(final_script, f, ensure_ascii=False, indent=2)

    # 调用 Factory 2.0
    print("\n[V50-Production] 剧本已锁定，启动智慧量产线...")
    from factory_v2_0_auto import IntelligentFactory
    factory = IntelligentFactory()
    
    video = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    bgm = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    role_lib = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    
    factory.run_production(script_v50, video, bgm, role_lib)
    
    # 物理重命名
    final_output = r"E:\VideoTranslator_Project\output_final\V50_ULTIMATE_DIRECTOR_CUT.mp4"
    import shutil
    shutil.copy(r"E:\VideoTranslator_Project\output_final\V48_SMART_AUTOMATED_MASTER.mp4", final_output)
    print(f"\n🏆 V50 导演剪辑版已诞生：{final_output}")

if __name__ == "__main__":
    run_v50_director_cut()
