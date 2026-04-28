# -*- coding: utf-8 -*-
import os, torch, numpy as np, subprocess
from demucs.apply import apply_model
from demucs.pretrained import get_model
import soundfile as sf

class AudioSeparator:
    def __init__(self, output_dir="separated_audio"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = get_model("htdemucs")
        self.model.to(self.device)

    def separate(self, media_path):
        print(f"\n[Separator] 正在执行【FFmpeg 鲁棒模式】剥离...")
        
        temp_input = os.path.join(self.output_dir, "temp_in.wav")
        ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
        
        subprocess.run([ffmpeg_bin, "-y", "-i", media_path, "-ac", "2", "-ar", "44100", temp_input], check=True, capture_output=True)
        
        wav_data, sr = sf.read(temp_input)
        wav_tensor = torch.from_numpy(wav_data.T).float().to(self.device)
        
        with torch.no_grad():
            sources = apply_model(self.model, wav_tensor[None], device=self.device)[0]
        
        bgm_wav = (sources[0] + sources[1] + sources[2]).cpu().numpy().T
        vocal_wav = sources[3].cpu().numpy().T

        # --- 核心改进：使用 FFmpeg 物理保存，不依赖 Python WAV 库 ---
        bgm_raw = os.path.join(self.output_dir, "bgm.raw")
        vocal_raw = os.path.join(self.output_dir, "vocal.raw")
        
        # 将 numpy 数组转为 raw pcm 并通过 ffmpeg 封装为 wav
        bgm_wav.astype(np.float32).tofile(bgm_raw)
        vocal_wav.astype(np.float32).tofile(vocal_raw)
        
        bgm_wav_path = os.path.join(self.output_dir, "pure_bgm.wav")
        vocal_wav_path = os.path.join(self.output_dir, "pure_vocals.wav")
        
        # 用 FFmpeg 强行封装，这种 WAV 绝对不可能读不出
        subprocess.run([ffmpeg_bin, "-y", "-f", "f32le", "-ar", "44100", "-ac", "2", "-i", bgm_raw, bgm_wav_path], check=True)
        subprocess.run([ffmpeg_bin, "-y", "-f", "f32le", "-ar", "44100", "-ac", "2", "-i", vocal_raw, vocal_wav_path], check=True)

        return bgm_wav_path, vocal_wav_path

if __name__ == "__main__":
    print("FFmpeg Robust Separator Ready.")
