# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, requests, whisper, librosa
import numpy as np
import soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]
os.environ["HTTP_PROXY"] = ""; os.environ["HTTPS_PROXY"] = ""

class ZeroHallucinationClient:
    def __init__(self):
        print("\n" + "☢️"*10 + " V73 绝对零噪流水线启动 " + "☢️"*10)
        self.auditor = whisper.load_model("tiny")
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\v73_run"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.results = []

    def run_production(self, script_path, seed_wav):
        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        
        for i, item in enumerate(data):
            text = item['zh'].strip().replace("。", "") # 移除自带句号，由逻辑统一补强
            save_path = os.path.join(self.temp_dir, f"raw_{i}.wav")
            
            # --- 0.01 极地采样 ---
            for attempt in range(4):
                requests.post("http://127.0.0.1:8000/generate", json={
                    "text": text + "。", 
                    "ref_wav": seed_wav,
                    "save_path": save_path
                }, timeout=100)
                
                # ASR 严打语气词
                res = self.auditor.transcribe(save_path, verbose=False)
                spoken = res['text'].lower()
                if not any(w in spoken for w in ["啊", "呃", "呢", "oh", "uh"]):
                    break
                print(f"  ⚠️ [拦截] 片段 {i+1} 检出疑似幻觉词 '{spoken}'，正在重录...")

            # --- 核心改进：50ms 硬熔断 ---
            y, sr = sf.read(save_path)
            intervals = librosa.effects.split(y, top_db=28) # 提高能量门槛至 28dB
            last_end = intervals[-1][1]/sr if len(intervals)>0 else len(y)/sr
            
            # 缩减缓冲区至 0.05s (极致利落)
            final_p = os.path.join(self.temp_dir, f"fixed_{i}.wav")
            subprocess.run([
                FFMPEG_BIN, "-y", "-i", save_path,
                "-af", f"atrim=end={last_end + 0.05},asetpts=PTS-STARTPTS,afade=t=out:st={last_end}:d=0.05",
                final_p
            ], capture_output=True)
            
            self.results.append((final_p, item['start']))
            print(f"  -> [{i+1}/25] 熔断完成 | 边缘: {last_end:.3f}s")

        print("\n🏆 V73 绝对零噪母带压制中...")
        # ... 后续压制逻辑同前 ...

if __name__ == "__main__":
    client = ZeroHallucinationClient()
    client.run_production(
        r"E:\VideoTranslator_Project\unhinged_tech\V69_2MIN_ELASTIC_SCRIPT.json",
        r"E:\VideoTranslator_Project\unhinged_tech\seeds\V73_SURGICAL_SEED.wav"
    )
