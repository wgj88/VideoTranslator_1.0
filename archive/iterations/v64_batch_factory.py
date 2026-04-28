# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, threading, queue
import numpy as np
import librosa
import soundfile as sf

# --- 物理环境锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

class FullBatchSentinelFactory:
    def __init__(self, batch_size=4):
        print("\n" + "🔥"*10 + f" V64 满载批处理引擎启动 (Batch: {batch_size}) " + "🔥"*10)
        self.db = VideoCloneDubber()
        self.batch_size = batch_size
        self.task_queue = queue.Queue()
        self.results = []
        self.is_done = False
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\v64_batch_run"
        os.makedirs(self.temp_dir, exist_ok=True)

    def sentinel_worker(self):
        """后台能量审计员"""
        while not self.is_done or not self.task_queue.empty():
            try:
                task = self.task_queue.get(timeout=1)
                idx, raw_p, start_t = task
                y, sr = sf.read(raw_p)
                intervals = librosa.effects.split(y, top_db=25)
                last_speech_end = intervals[-1][1] / sr if len(intervals) > 0 else len(y)/sr
                
                final_p = os.path.join(self.temp_dir, f"v64_fixed_{idx}.wav")
                subprocess.run([
                    FFMPEG_BIN, "-y", "-i", raw_p,
                    "-af", f"atrim=end={last_speech_end + 0.15},asetpts=PTS-STARTPTS,afade=t=out:st={last_speech_end}:d=0.1",
                    final_p
                ], capture_output=True)
                self.results.append((final_p, start_t))
                self.task_queue.task_done()
            except queue.Empty: continue

    def run_production(self, script_path, seed_wav):
        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        t = threading.Thread(target=self.sentinel_worker)
        t.start()
        
        start_time = time.time()
        print(f"\n[V64-Turbo] GPU 正在并行产出批次流...")

        for i in range(0, len(data), self.batch_size):
            batch = data[i:i+self.batch_size]
            print(f"  -> 正在交付 Batch {i//self.batch_size + 1}: {len(batch)} 句")
            
            # 物理并行生成 (VoxCPM2 的模型通常不支持直接 tensor batch，我们通过极速串行+异步审计模拟)
            for sub_idx, item in enumerate(batch):
                global_idx = i + sub_idx
                wav = self.db.model.generate(text=item['zh'].strip()+"。", reference_wav_path=seed_wav, inference_timesteps=20)
                raw_p = os.path.join(self.temp_dir, f"raw_{global_idx}.wav")
                sf.write(raw_p, wav, self.db.sample_rate)
                self.task_queue.put((global_idx, raw_p, item['start']))

        self.is_done = True
        t.join()
        print(f"\n🏆 V64 极速渲染完成！总耗时: {time.time() - start_time:.2f}s")
        return sorted(self.results, key=lambda x: x[1])

if __name__ == "__main__":
    factory = FullBatchSentinelFactory(batch_size=4)
    script = r"E:\VideoTranslator_Project\separated_audio\V51_CALIBRATED_SCRIPT.json"
    role_lib = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(role_lib, "r") as f: seed = json.load(f)['SPEAKER_00']['wav']
    factory.run_production(script, seed)
