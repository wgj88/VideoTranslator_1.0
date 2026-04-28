# -*- coding: utf-8 -*-
import os, sys, json, requests, re

def rebuild_translation_and_dubbing():
    script_path = r"E:\VideoTranslator_Project\separated_audio\v9_final_script.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    
    # 1. 物理检查输入
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    # 2. 强制补齐 Speaker (防止聚类遗漏)
    for item in data:
        if 'speaker' not in item: item['speaker'] = "SPEAKER_00"

    # 3. 硅基流动 DeepSeek 翻译
    with open(r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env", "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0]
    
    print("\n[Action] 正在对全角色剧本进行地道汉化...")
    batch = data[:10] # 处理前 10 句
    text = "\n".join([f"ID_{i}: [{item['speaker']}] {item['text']}" for i, item in enumerate(batch)])
    
    prompt = f"你是一个汉化主编。请将以下内容翻译成中文解说词。输出JSON数组，格式：[{{'id': 0, 'zh': '...'}}]。\n\n内容：\n{text}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": "deepseek-ai/DeepSeek-V3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
    
    resp = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers).json()
    content = resp['choices'][0]['message']['content']
    
    # 解析译文
    match = re.search(r'\[.*\]', content, re.DOTALL)
    if match:
        trans_results = json.loads(match.group())
        for r in trans_results:
            idx = int(r['id'])
            if idx < len(batch): batch[idx]['zh_final'] = r['zh']
            print(f"  ✨ {batch[idx]['speaker']} -> {r['zh'][:20]}...")

    # 4. 调用 VoxCPM 进行配音
    sys.path.append(r"E:\VideoTranslator_Project")
    from clone_dubber import VideoCloneDubber
    import soundfile as sf
    
    db = VideoCloneDubber()
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v9_rebuild_wavs"
    os.makedirs(audio_dir, exist_ok=True)

    print("\n[Action] 正在启动【分角色】配音渲染...")
    for i, item in enumerate(batch):
        zh_text = item.get('zh_final')
        if not zh_text: continue
        
        seed = role_lib.get(item['speaker'])
        if seed:
            print(f"  -> 正在复刻 {item['speaker']} 说中文...")
            # 使用黄金配方：音频 + 精准台词引导
            wav = db.model.generate(text=zh_text + "。", prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            out_p = os.path.join(audio_dir, f"v9_rebuild_{i}.wav")
            sf.write(out_p, wav, db.sample_rate)
            item['dub_path'] = out_p

    # 保存最终成果 JSON
    final_json = r"E:\VideoTranslator_Project\separated_audio\V9_REBUILD_FINAL.json"
    with open(final_json, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 重修完成！最终 JSON 已生成：{final_json}")

if __name__ == "__main__":
    rebuild_translation_and_dubbing()
