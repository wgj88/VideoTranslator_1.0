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

class GrandFinaleFactory:
    def __init__(self):
        print("\n" + "💎"*10 + " V78 旗舰版量产引擎启动 " + "💎"*10)
        self.db = VideoCloneDubber()
        # V78 核心：载入审计模型用于单词级熔断
        self.auditor = whisper.load_model("base")
        self.task_queue = queue.Queue()
        self.results = []
        self.is_done = False
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\v78_run"
        os.makedirs(self.temp_dir, exist_ok=True)

    def surgical_worker(self):
        """V78 核心：单词级熔断审计员"""
        while not self.is_done or not self.task_queue.empty():
            try:
                task = self.task_queue.get(timeout=1)
                idx, raw_p, item = task
                
                # 1. 纳米级审计：寻找最后一个字的物理终点
                res = self.auditor.transcribe(raw_p, word_timestamps=True)
                
                # 策略：找到剧本里最后一个有效词的结束点
                target_end = res['segments'][-1]['end'] if res['segments'] else 0
                
                # 2. 执行死亡切除
                final_p = os.path.join(self.temp_dir, f"v78_fixed_{idx}.wav")
                # 强制在字音结束 50ms 处封死，并做 50ms 极短淡出
                cmd = [
                    FFMPEG_BIN, "-y", "-i", raw_p,
                    "-af", f"atrim=end={target_end + 0.05},asetpts=PTS-STARTPTS,afade=t=out:st={target_end}:d=0.05",
                    final_p
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                self.results.append((final_p, item['start']))
                self.task_queue.task_done()
            except queue.Empty: continue

    def run_1min_production(self, script_p, seed_wav):
        with open(script_p, "r", encoding="utf-8") as f: all_data = json.load(f)
        data = [it for it in all_data if it['start'] < 60]
        
        t = threading.Thread(target=self.surgical_worker)
        t.start()
        
        start_time = time.time()
        for i, item in enumerate(data):
            # GPU 推理 (45步高精)
            wav = self.db.model.generate(text=item['zh']+"。", reference_wav_path=seed_wav, inference_timesteps=45)
            raw_p = os.path.join(self.temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, self.db.sample_rate)
            self.task_queue.put((i, raw_p, item))
            print(f"  -> [Generator] {i+1}/{len(data)} 已完成")

        self.is_done = True
        t.join()
        print(f"\n🏆 V78 旗舰渲染完成！总耗时: {time.time() - start_time:.2f}s")
        return sorted(self.results, key=lambda x: x[1])

if __name__ == "__main__":
    factory = GrandFinaleFactory()
    # 使用 V70 正典剧本
    script = r"E:\VideoTranslator_Project\unhinged_tech\V70_FORMAL_SCRIPT.json"
    seed = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    results = factory.run_1min_production(script, seed)

    # 混音封装
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V78_UNHINGED_1MIN_FLAGSHIP.mp4"
    temp_zh = r"E:\VideoTranslator_Project\unhinged_tech\v78_zh_full.wav"
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(results):
        input_args.extend(["-i", p])
        filter_parts.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    mix_zh = "".join([f"[a{k}]" for k in range(len(results))]) + f"amix=inputs={len(results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh], check=True)

    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    cmd_pack = [
        FFMPEG_BIN, "-y", "-ss", "0", "-t", "60", "-i", raw_v, "-i", temp_zh, "-ss", "0", "-t", "60", "-i", bgm,
        "-filter_complex", "[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out];[0:v]subtitles='E\\:/VideoTranslator_Project/unhinged_tech/1min_subtitles.srt':force_style='FontSize=20,PrimaryColour=&H00FFFF'[v_sub]",
        "-map", "[v_sub]", "-map", "[out]", "-c:v", "libx264", "-c:a", "aac", output_mp4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏁 V78 旗舰样片已诞生：{output_mp4}")
