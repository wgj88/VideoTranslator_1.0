# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, requests, whisper, librosa
import numpy as np
import soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

class OrthoMasterClient:
    def __init__(self, server_url="http://127.0.0.1:8000"):
        print("\n" + "🎓"*10 + " V72 工业正典流水线启动 " + "🎓"*10)
        self.server_url = server_url
        self.auditor = whisper.load_model("tiny")
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\v72_ortho_run"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.results = []

    def ortho_clean(self, text):
        """执行比官方更严苛的标点阉割"""
        text = text.replace("：", "。").replace(":", "。")
        text = text.replace("——", "，").replace("“", "").replace("”", "")
        # 处理数字和单位 (虽然服务器开启了 normalize，我们这里再做一层语义保护)
        text = text.replace("$", "美元").replace("%", "百分之")
        return text

    def run_production(self, script_path, seed_wav):
        print("[Client] 正在侦听服务器上线...")
        while True:
            try:
                requests.get(self.server_url.replace("/generate", "/"), timeout=1)
                break
            except: time.sleep(2)

        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        
        for i, item in enumerate(data):
            # 1. 物理清洗
            text = self.ortho_clean(item['zh'].strip())
            if not text: continue
            save_path = os.path.join(self.temp_dir, f"raw_{i}.wav")
            
            # 2. 生产 (服务器已开启 normalize=True)
            requests.post(f"{self.server_url}/generate", json={"text": text+"。", "ref_wav": seed_wav, "save_path": save_path}, timeout=100)
            
            # 3. 极速审计 (ASR)
            asr_res = self.auditor.transcribe(save_path, verbose=False)
            spoken = asr_res['text'].lower()
            bad = ["呃", "啊", "呢", "oh", "uh", "um"]
            purity = "100%" if not any(w in spoken for w in bad) else "⚠️ 有瑕疵"
            
            # 4. 弹性调速
            y, sr = sf.read(save_path)
            tempo = max(0.95, min(1.4, (len(y)/sr)/(item['end'] - item['start'])))
            final_p = os.path.join(self.temp_dir, f"v72_fixed_{i}.wav")
            subprocess.run([FFMPEG_BIN, "-y", "-i", save_path, "-af", f"atempo={tempo},afade=t=out:st={(len(y)/sr)/tempo-0.1}:d=0.1", final_p], capture_output=True)
            
            self.results.append((final_p, item['start']))
            print(f"  -> [{i+1}/{len(data)}] 纯净度: {purity} | 语速: {tempo:.2f}x | 文字: {text[:12]}...")

        print("\n🏆 V72 正典样片已生成！正在封装终极 MP4...")

if __name__ == "__main__":
    client = OrthoMasterClient()
    client.run_production(
        r"E:\VideoTranslator_Project\unhinged_tech\V69_2MIN_ELASTIC_SCRIPT.json",
        r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    )
