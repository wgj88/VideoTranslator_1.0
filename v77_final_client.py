# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, requests, whisper, librosa
import numpy as np
import soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]
os.environ["HTTP_PROXY"] = ""; os.environ["HTTPS_PROXY"] = ""

class FinalGodClient:
    def __init__(self):
        print("\n" + "⚔️"*10 + " V77.1 终极大决战流水线启动 " + "⚔️"*10)
        self.auditor = whisper.load_model("tiny")
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\v77_final"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.results = []
        self.seed_text = "It's the year 2026. Your $3,500 smart fridge has a GPU and it's showing you ads."

    def run_production(self, script_path, seed_wav):
        print("[Client] 等待核心就绪...")
        while True:
            try: requests.get("http://127.0.0.1:8000/", timeout=1); break
            except: time.sleep(2)

        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        
        for i, item in enumerate(data):
            text = item['zh'].strip()
            save_path = os.path.join(self.temp_dir, f"raw_{i}.wav")
            
            # --- 这一行代码价值一万美金：Dual-Guide Generation ---
            requests.post("http://127.0.0.1:8000/generate", json={
                "text": text, 
                "ref_wav": seed_wav,
                "prompt_text": self.seed_text,
                "save_path": save_path
            }, timeout=100, proxies={"http": None, "https": None})
            
            # ASR 监测 (此时幻觉应该极少)
            res = self.auditor.transcribe(save_path, verbose=False)
            spoken = res['text'].lower()
            status = "纯净" if not any(w in spoken for w in ["呃", "啊", "呢"]) else "⚠️ 拦截"

            # 弹性胀缩
            y, sr = sf.read(save_path)
            intervals = librosa.effects.split(y, top_db=28)
            last_end = intervals[-1][1]/sr if len(intervals)>0 else len(y)/sr
            expected = item['end'] - item['start']
            tempo = max(0.95, min(1.4, last_end/expected))
            
            final_p = os.path.join(self.temp_dir, f"fixed_{i}.wav")
            subprocess.run([FFMPEG_BIN, "-y", "-i", save_path, "-af", f"atrim=end={last_end+0.05},asetpts=PTS-STARTPTS,atempo={tempo},afade=t=out:st={last_end/tempo-0.05}:d=0.05", final_p], capture_output=True)
            
            self.results.append((final_p, item['start']))
            print(f"  -> [{i+1}/25] {status} | 语速: {tempo:.2f}x | {text[:10]}...")

        # 后续压制逻辑同 V73...
        print("\n🏆 V77.1 终极版样片已合成！")

if __name__ == "__main__":
    FinalGodClient().run_production(
        r"E:\VideoTranslator_Project\unhinged_tech\V77_BALANCED_SCRIPT.json",
        r"E:\VideoTranslator_Project\unhinged_tech\seeds\V73_SURGICAL_SEED.wav"
    )
