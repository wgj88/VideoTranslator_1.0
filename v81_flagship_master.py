# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, threading, queue
import numpy as np
import soundfile as sf
import whisper

# --- 物理资产配置 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

class FlagshipFactory:
    def __init__(self):
        print("\n" + "💎"*10 + " V81 旗舰版量产引擎启动 " + "💎"*10)
        self.db = VideoCloneDubber()
        self.auditor = whisper.load_model("base") # 开启纳米熔断审计
        self.task_queue = queue.Queue()
        self.results = []
        self.is_done = False
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\v81_run"
        os.makedirs(self.temp_dir, exist_ok=True)

    def surgical_worker(self):
        """执行 V77 纳米熔断：物理蒸发末尾幻觉"""
        while not self.is_done or not self.task_queue.empty():
            try:
                task = self.task_queue.get(timeout=1)
                idx, raw_p, start_t = task
                # 1. 精准定位
                res = self.auditor.transcribe(raw_p, word_timestamps=True)
                semantic_end = res['segments'][-1]['end'] if res['segments'] else 0
                # 2. 硬切割
                final_p = os.path.join(self.temp_dir, f"v81_fixed_{idx}.wav")
                cmd = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atrim=end={semantic_end+0.05},asetpts=PTS-STARTPTS,afade=t=out:st={semantic_end}:d=0.05", final_p]
                subprocess.run(cmd, check=True, capture_output=True)
                self.results.append((final_p, start_t))
                self.task_queue.task_done()
            except queue.Empty: continue

    def run_production(self, script_p, seed_wav):
        with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
        t = threading.Thread(target=self.surgical_worker)
        t.start()
        start_time = time.time()
        for i, item in enumerate(data):
            # GPU 推理
            wav = self.db.model.generate(text=item['zh'], reference_wav_path=seed_wav, inference_timesteps=20)
            raw_p = os.path.join(self.temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, self.db.sample_rate)
            self.task_queue.put((i, raw_p, item['start']))
            print(f"  -> [Generator] {i+1}/{len(data)} 段已就绪")
        self.is_done = True
        t.join()
        print(f"\n🏆 V81 核心生成完成！耗时: {time.time() - start_time:.2f}s")
        return sorted(self.results, key=lambda x: x[1])

if __name__ == "__main__":
    f = FlagshipFactory()
    script = r"E:\VideoTranslator_Project\unhinged_tech\V81_60S_FIXED.json"
    seed = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    results = f.run_production(script, seed)

    # 封装
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V81_FLAGSHIP_1MIN.mp4"
    temp_zh = r"E:\VideoTranslator_Project\unhinged_tech\v81_zh_master.wav"
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(results):
        input_args.extend(["-i", p])
        filter_parts.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    mix_zh = "".join([f"[a{k}]" for k in range(len(results))]) + f"amix=inputs={len(results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh], check=True)

    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    # 生成配套 SRT
    temp_srt = r"E:\VideoTranslator_Project\unhinged_tech\v81_final.srt"
    def ft(s): return f"{int(s//3600):02d}:{int((s%3600)//60):02d}:{int(s%60):02d},{int((s%1)*1000):03d}"
    with open(script, "r", encoding="utf-8") as fs: data = json.load(f.script if hasattr(f, 'script') else fs)
    with open(temp_srt, "w", encoding="utf-8") as f_srt:
        for i, it in enumerate(data): f_srt.write(f"{i+1}\n{ft(it['start'])} --> {ft(it['end'])}\n{it['zh']}\n\n")

    print("\n[Master] 正在压制 1080P 旗舰成片...")
    cmd_pack = [
        FFMPEG_BIN, "-y", "-ss", "0", "-t", "60", "-i", raw_v, "-i", temp_zh, "-ss", "0", "-t", "60", "-i", bgm,
        "-filter_complex", f"[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out];[0:v]subtitles='{temp_srt.replace('\\','/').replace(':','\\:')}':force_style='FontSize=20,PrimaryColour=&H00FFFF,BorderStyle=1,Outline=1,Alignment=2'[v_sub]",
        "-map", "[v_sub]", "-map", "[out]", "-c:v", "libx264", "-crf", "22", "-c:a", "aac", output_mp4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏁 V81 旗舰成片已诞生：{output_mp4}")
