# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, threading, queue
import numpy as np
import soundfile as sf
import whisper

# --- 环境资产锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

class AustereFactory:
    def __init__(self):
        print("\n" + "🍃"*10 + " V80 舒缓脱水版引擎启动 " + "🍃"*10)
        self.db = VideoCloneDubber()
        self.auditor = whisper.load_model("base") # 用于 V77 纳米熔断
        self.task_queue = queue.Queue()
        self.results = []
        self.is_done = False
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\v80_run"
        os.makedirs(self.temp_dir, exist_ok=True)

    def surgical_worker(self):
        """执行 V77 级纳米熔断审计"""
        while not self.is_done or not self.task_queue.empty():
            try:
                task = self.task_queue.get(timeout=1)
                idx, raw_p, item = task
                
                # 1. 精准定位单词边界
                res = self.auditor.transcribe(raw_p, word_timestamps=True)
                # 找最后一个汉字结束的时间点
                semantic_end = res['segments'][-1]['end'] if res['segments'] else 0
                
                # 2. 物理熔断（留出 50ms 极窄呼吸区）
                final_p = os.path.join(self.temp_dir, f"v80_fixed_{idx}.wav")
                cmd = [
                    FFMPEG_BIN, "-y", "-i", raw_p,
                    "-af", f"atrim=end={semantic_end + 0.05},asetpts=PTS-STARTPTS,afade=t=out:st={semantic_end}:d=0.05",
                    final_p
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                self.results.append((final_p, item['start']))
                self.task_queue.task_done()
            except queue.Empty: continue

    def run_production(self, script_p, seed_wav):
        with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
        
        t = threading.Thread(target=self.surgical_worker)
        t.start()
        
        start_time = time.time()
        for i, item in enumerate(data):
            # GPU 推理 (回归 20 步极速 + 脱水文本)
            wav = self.db.model.generate(text=item['zh']+"。", reference_wav_path=seed_wav, inference_timesteps=20)
            raw_p = os.path.join(self.temp_dir, f"v80_raw_{i}.wav")
            sf.write(raw_p, wav, self.db.sample_rate)
            self.task_queue.put((i, raw_p, item))
            print(f"  -> [Generator] 第 {i+1} 段已产出。")

        self.is_done = True
        t.join()
        
        # 终极混音
        output_wav = r"E:\VideoTranslator_Project\output_final\V80_AUSTERE_FINAL_SAMPLE.wav"
        input_args = []
        filter_parts = []
        for idx, (p, start_t) in enumerate(sorted(self.results, key=lambda x: x[1])):
            input_args.extend(["-i", p])
            delay = int(start_t * 1000)
            filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
        
        mix_str = "".join([f"[a{k}]" for k in range(len(self.results))]) + f"amix=inputs={len(self.results)}"
        subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, output_wav], check=True)
        
        print(f"\n🏆 V80 终极舒缓版已就绪：{output_wav}")
        print(f"⏰ 总耗时: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    factory = AustereFactory()
    script = r"E:\VideoTranslator_Project\unhinged_tech\V79_SLIM_SCRIPT.json"
    seed = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    factory.run_production(script, seed)
