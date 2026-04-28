# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, threading, queue
import numpy as np
import librosa
import soundfile as sf

# --- 物理路径锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

class LibrosaSentinelFactory:
    def __init__(self):
        print("\n" + "⚔️"*10 + " V63.1 利落版引擎启动 (Librosa 能量审计) " + "⚔️"*10)
        self.db = VideoCloneDubber()
        self.task_queue = queue.Queue()
        self.results = []
        self.is_done = False
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\librosa_run"
        os.makedirs(self.temp_dir, exist_ok=True)

    def sentinel_worker(self):
        """利用 librosa 执行物理级边缘探测"""
        while not self.is_done or not self.task_queue.empty():
            try:
                task = self.task_queue.get(timeout=1)
                idx, raw_p, start_t = task
                
                # 1. 加载音频 (f32)
                y, sr = sf.read(raw_p)
                
                # 2. 能量审计：探测非静默区间 (top_db=25 是拦截 呃、呢 的黄金阈值)
                intervals = librosa.effects.split(y, top_db=25)
                
                if len(intervals) > 0:
                    # 找到最后一个有意义的声团结束点
                    last_speech_end = intervals[-1][1] / sr
                else:
                    last_speech_end = len(y) / sr

                # 3. 执行柔和对齐
                final_p = os.path.join(self.temp_dir, f"v63_1_fixed_{idx}.wav")
                protected_end = last_speech_end + 0.15
                subprocess.run([
                    FFMPEG_BIN, "-y", "-i", raw_p,
                    "-af", f"atrim=end={protected_end},asetpts=PTS-STARTPTS,afade=t=out:st={last_speech_end}:d=0.1",
                    final_p
                ], capture_output=True)
                
                self.results.append((final_p, start_t))
                self.task_queue.task_done()
            except queue.Empty:
                continue

    def run_production(self, script_path, seed_wav):
        with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
        t = threading.Thread(target=self.sentinel_worker)
        t.start()
        start_time = time.time()
        for i, item in enumerate(data):
            # GPU 专注生成
            wav = self.db.model.generate(text=item['zh'].strip() + "。", reference_wav_path=seed_wav, inference_timesteps=20)
            raw_p = os.path.join(self.temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, self.db.sample_rate)
            self.task_queue.put((i, raw_p, item['start']))
            if (i+1) % 10 == 0: print(f"  -> [Generator] 进度: {i+1}/{len(data)}")

        self.is_done = True
        t.join()
        print(f"\n🏆 利落渲染完成！耗时: {time.time() - start_time:.2f}s")
        return sorted(self.results, key=lambda x: x[1])

if __name__ == "__main__":
    factory = LibrosaSentinelFactory()
    script = r"E:\VideoTranslator_Project\separated_audio\V51_CALIBRATED_SCRIPT.json"
    role_lib = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(role_lib, "r") as f: seed = json.load(f)['SPEAKER_00']['wav']
    factory.run_production(script, seed)
