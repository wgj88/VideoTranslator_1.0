# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, threading, queue
import numpy as np
import soundfile as sf
import librosa

# --- 环境资产锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]
sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

class ProductionFactory:
    def __init__(self, batch_size=4):
        print("\n" + "🏗️"*10 + " VideoTranslator 1.0 旗舰版启动 " + "🏗️"*10)
        self.db = VideoCloneDubber()
        self.batch_size = batch_size
        self.task_queue = queue.Queue()
        self.results = []
        self.is_done = False
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\final_stable"
        os.makedirs(self.temp_dir, exist_ok=True)

    def get_smart_steps(self, text):
        count = len(text)
        if count <= 6: return 12
        if count <= 25: return 25
        return 50

    def sentinel_worker(self):
        while not self.is_done or not self.task_queue.empty():
            try:
                task = self.task_queue.get(timeout=1)
                idx, raw_p, start_t = task
                y, sr = sf.read(raw_p)
                intervals = librosa.effects.split(y, top_db=25)
                last_end = intervals[-1][1] / sr if len(intervals) > 0 else len(y)/sr
                final_p = os.path.join(self.temp_dir, f"stable_fixed_{idx}.wav")
                subprocess.run([FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atrim=end={last_end+0.15},asetpts=PTS-STARTPTS,afade=t=out:st={last_end}:d=0.1", final_p], capture_output=True)
                self.results.append((final_p, start_t))
                self.task_queue.task_done()
            except queue.Empty: continue

    def run_production(self, script_path, seed_wav, output_video=None):
        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        t = threading.Thread(target=self.sentinel_worker)
        t.start()
        start_time = time.time()
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i+self.batch_size]
            for sub_idx, item in enumerate(batch):
                global_idx = i + sub_idx
                steps = self.get_smart_steps(item['zh'])
                wav = self.db.model.generate(text=item['zh'].strip()+"。", reference_wav_path=seed_wav, inference_timesteps=steps)
                raw_p = os.path.join(self.temp_dir, f"raw_{global_idx}.wav")
                sf.write(raw_p, wav, self.db.sample_rate)
                self.task_queue.put((global_idx, raw_p, item['start']))
            print(f"  -> [Factory] 进度: {i+len(batch)}/{len(data)} 段生成完毕")
        self.is_done = True
        t.join()
        print(f"✅ 生产圆满完成！")
        return sorted(self.results, key=lambda x: x[1])

if __name__ == "__main__":
    print("VideoTranslator 1.0 Factory Class Loaded.")
