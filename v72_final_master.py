# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, requests, whisper, librosa
import numpy as np
import soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]
os.environ["HTTP_PROXY"] = ""; os.environ["HTTPS_PROXY"] = ""

class UltimatePurityMaster:
    def __init__(self):
        print("\n" + "🏁"*10 + " V72.1 终极净化流水线：正在封测 " + "🏁"*10)
        self.server_url = "http://127.0.0.1:8000"
        self.auditor = whisper.load_model("tiny")
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\v72_final"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.results = []

    def run_production(self, script_path, seed_wav, raw_video, bgm_wav):
        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        
        # 1. 物理补全与清洗
        fixes = {3: "现在，是时候开启我车库里的年度传统了。", 7: "别担心，硅谷总能给我们整出点儿新花样。", 
                 12: "这回可不是闹着玩的，开发已经成了正经行当。", 13: "回想二零二三年的黄金时代，真是一去不返。", 
                 17: "这消息对你来说，可能是喜讯，也可能是噩梦。"}
        
        print(f"\n[Master] 正在处理全量 25 段音频...")
        for i, item in enumerate(data):
            text = fixes.get(i, item['zh']).strip()
            text = text.replace("：", "。").replace(":", "。") # 去冒号
            save_path = os.path.join(self.temp_dir, f"raw_{i}.wav")
            
            # --- 0 容忍审计循环 ---
            for attempt in range(5): 
                requests.post(f"{self.server_url}/generate", json={"text": text+"。", "ref_wav": seed_wav, "save_path": save_path}, timeout=100)
                res = self.auditor.transcribe(save_path, verbose=False)
                spoken = res['text'].lower()
                bad = ["呃", "啊", "呢", "那个", "这个", "嗯", "oh", "uh", "um"]
                if not any(w in spoken for w in bad): break
                print(f"  ⚠️ [抓捕成功] 片段 {i+1} 发现杂音，正在重录 ({attempt+1}/5)...")

            # --- 弹性调速与对齐 ---
            y, sr = sf.read(save_path)
            dur = len(y)/sr
            expected = item['end'] - item['start']
            tempo = max(0.95, min(1.4, dur/expected))
            final_p = os.path.join(self.temp_dir, f"fixed_{i}.wav")
            subprocess.run([FFMPEG_BIN, "-y", "-i", save_path, "-af", f"atempo={tempo},afade=t=out:st={dur/tempo-0.1}:d=0.1", final_p], capture_output=True)
            self.results.append((final_p, item['start']))
            print(f"  -> [{i+1}/25] 语速: {tempo:.2f}x | 文字: {text[:10]}...")

        # 2. 合成母带
        print("\n[Master] 正在压制最终成品...")
        temp_zh = os.path.join(self.temp_dir, "master_zh.wav")
        input_args = []
        filter_parts = []
        for idx, (p, st) in enumerate(self.results):
            input_args.extend(["-i", p])
            filter_parts.append(f"[{idx}:a]adelay={int(st*1000)}|{int(st*1000)}[a{idx}]")
        mix_str = "".join([f"[a{k}]" for k in range(len(self.results))]) + f"amix=inputs={len(self.results)}:duration=longest,volume={len(self.results)}"
        with open(os.path.join(self.temp_dir, "mix.txt"), "w") as f: f.write(";".join(filter_parts)+";"+mix_str)
        subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex_script", os.path.join(self.temp_dir, "mix.txt"), temp_zh], check=True)

        srt_p = os.path.join(self.temp_dir, "master.srt")
        with open(srt_p, "w", encoding="utf-8") as f:
            for i, item in enumerate(data):
                f.write(f"{i+1}\n{int(item['start']//3600):02d}:{int((item['start']%3600)//60):02d}:{int(item['start']%60):02d},000 --> {int(item['end']//3600):02d}:{int((item['end']%3600)//60):02d}:{int(item['end']%60):02d},000\n{item['zh']}\n\n")

        output_mp4 = r"E:\VideoTranslator_Project\output_final\V72_MASTER_FINAL_2MIN.mp4"
        escaped_srt = srt_p.replace("\\", "/").replace(":", "\\:")
        subprocess.run([FFMPEG_BIN, "-y", "-ss", "0", "-t", "120", "-i", raw_video, "-i", temp_zh, "-ss", "0", "-t", "120", "-i", bgm_wav,
            "-filter_complex", f"[1:a]volume=1.5[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out];[0:v]subtitles='{escaped_srt}':force_style='FontSize=20,PrimaryColour=&H00FFFF,Alignment=2'[v_sub]",
            "-map", "[v_sub]", "-map", "[out]", "-c:v", "h264_nvenc", "-preset", "p4", "-cq", "22", output_mp4], check=True)
        print(f"\n🏆 巅峰样片已产出：{output_mp4}")

if __name__ == "__main__":
    UltimatePurityMaster().run_production(
        r"E:\VideoTranslator_Project\unhinged_tech\V69_2MIN_ELASTIC_SCRIPT.json",
        r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav",
        r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4",
        r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    )
