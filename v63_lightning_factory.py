# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, threading, queue
import numpy as np
import soundfile as sf
import torch

# --- 路径注入 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber
# 使用官方加载器
from whisperx.vads.vad import load_vad_model

class LightningFactory:
    def __init__(self):
        print("\n" + "⚡"*10 + " V63 闪电对齐引擎启动 " + "⚡"*10)
        self.db = VideoCloneDubber()
        # 利用官方接口一键加载
        self.vad = load_vad_model("cuda", vad_onset=0.5, vad_offset=0.363)
        self.task_queue = queue.Queue()
        self.results = []
        self.is_done = False
        self.temp_dir = r"E:\VideoTranslator_Project\temp_factory\lightning_run"
        os.makedirs(self.temp_dir, exist_ok=True)

    def vad_worker(self):
        while not self.is_done or not self.task_queue.empty():
            try:
                task = self.task_queue.get(timeout=1)
                idx, raw_p, start_t, total_dur = task
                audio_data, sr = sf.read(raw_p)
                
                # 核心审计：直接调用 vad 实例
                # 返回格式通常是包含 segments 的列表
                segments = self.vad({"waveform": torch.from_numpy(audio_data).float().unsqueeze(0), "sample_rate": sr})
                
                last_speech_end = segments[-1].end if segments else total_dur
                
                final_p = os.path.join(self.temp_dir, f"v63_fixed_{idx}.wav")
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
        t = threading.Thread(target=self.vad_worker)
        t.start()
        start_time = time.time()
        for i, item in enumerate(data):
            wav = self.db.model.generate(text=item['zh'].strip() + "。", reference_wav_path=seed_wav, inference_timesteps=20)
            raw_p = os.path.join(self.temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, self.db.sample_rate)
            self.task_queue.put((i, raw_p, item['start'], len(wav)/self.db.sample_rate))
            if (i+1) % 10 == 0: print(f"  -> 进度: {i+1}/{len(data)} 段生成完毕")
        self.is_done = True
        audit_thread_result = t.join()
        print(f"\n🏆 闪电量产达成！总耗时: {time.time() - start_time:.2f}s")
        return sorted(self.results, key=lambda x: x[1])

if __name__ == "__main__":
    lf = LightningFactory()
    script = r"E:\VideoTranslator_Project\separated_audio\V51_CALIBRATED_SCRIPT.json"
    role_lib = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(role_lib, "r") as f: seed = json.load(f)['SPEAKER_00']['wav']
    lf.run_production(script, seed)
