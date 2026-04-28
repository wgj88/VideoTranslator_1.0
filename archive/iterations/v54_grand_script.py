# -*- coding: utf-8 -*-
import os, sys, json, requests, re, time, whisper

# --- 环境硬路径锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_unhinged_grand_script():
    boosted_wav = r"E:\VideoTranslator_Project\unhinged_tech\boosted_vocals.wav"
    output_script = r"E:\VideoTranslator_Project\unhinged_tech\V54_FINAL_GRAND_SCRIPT.json"
    dotenv_p = r"C:\Users\Administrator\Desktop\HorrorAgent_Project\.env"
    
    with open(dotenv_p, "r") as f:
        api_key = [l for l in f if "SILICONFLOW_API_KEY" in l][0].split("=")[1].strip().split()[0].replace('"', '').replace("'", "")

    print(f"\n" + "🎧"*10 + " 正在执行 9 分钟全量剧本提取 " + "🎧"*10)

    # 1. 全量听译
    model = whisper.load_model("base.en")
    res = model.transcribe(boosted_wav, verbose=False)
    raw_segments = res['segments']
    print(f"  ✅ 英文剧本抓取成功：共 {len(raw_segments)} 段。")

    # 2. 导演级分批汉化 (DeepSeek-V3)
    print(f"\n[Translator] 正在对 9 分钟台词进行“失控风格”重译...")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    final_localized_script = []
    batch_size = 12
    
    for i in range(0, len(raw_segments), batch_size):
        batch = raw_segments[i:i+batch_size]
        payload_text = "\n".join([f"ID_{j}: {item['text']}" for j, item in enumerate(batch)])
        
        prompt = f"你是一个硬核、幽默、吐槽风格的科技博主。请将以下内容翻译成专业、爽快、没有任何语气词的中文。返回格式:[{{\"zh\": \"...\"}}]\n内容:\n{payload_text}"
        
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        for retry in range(2):
            try:
                r = requests.post("https://api.siliconflow.cn/v1/chat/completions", json=payload, headers=headers, timeout=40).json()
                content = r['choices'][0]['message']['content']
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    trans_list = json.loads(match.group())
                    for idx_res, res_item in enumerate(trans_list):
                        if idx_res < len(batch):
                            orig = batch[idx_res]
                            final_localized_script.append({
                                "start": round(orig['start'], 3),
                                "end": round(orig['end'], 3),
                                "speaker": "SPEAKER_00", # 全篇统一单人
                                "en": orig['text'].strip(),
                                "zh": res_item['zh'].strip()
                            })
                    print(f"  -> 进度: {min(i+batch_size, len(raw_segments))}/{len(raw_segments)}")
                    break
            except:
                time.sleep(2)

    with open(output_script, "w", encoding="utf-8") as f:
        json.dump(final_localized_script, f, ensure_ascii=False, indent=2)
    
    # 3. 锁定种子 (取前 5 秒)
    role_lib = {
        "SPEAKER_00": {
            "wav": r"E:\VideoTranslator_Project\unhinged_tech\seeds\main_seed.wav",
            "text": final_localized_script[0]['en']
        }
    }
    os.makedirs(r"E:\VideoTranslator_Project\unhinged_tech\seeds", exist_ok=True)
    subprocess.run([FFMPEG_BIN, "-y", "-i", boosted_wav, "-ss", "0", "-t", "5", "-ac", "1", role_lib['SPEAKER_00']['wav']], capture_output=True)
    
    with open(r"E:\VideoTranslator_Project\unhinged_tech\V54_ROLE_LIB.json", "w", encoding="utf-8") as f:
        json.dump(role_lib, f, indent=2)

    print(f"\n🏆 蓝图已铸就！汉化剧本：{output_script}")
    print(f"📂 角色基因库已就绪：V54_ROLE_LIB.json")

if __name__ == "__main__":
    run_unhinged_grand_script()
