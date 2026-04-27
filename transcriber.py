# -*- coding: utf-8 -*-
import os, json, whisper, torch

class AudioTranscriber:
    def __init__(self, model_size="base"):
        ffmpeg_bin_dir = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32"
        if ffmpeg_bin_dir not in os.environ["PATH"]:
            os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ["PATH"]
        
        print(f"[Transcriber] 正在初始化 Whisper 模型 ({model_size})...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(model_size, device=self.device)

    def process(self, audio_path):
        print(f"\n[Transcriber] 正在分析音频: {audio_path}")
        result = self.model.transcribe(audio_path, task="transcribe", verbose=False)
        segments = result.get("segments", [])
        if not segments: return None

        # --- 核心修复：使用 splitext 确保后缀替换正确 ---
        base_path, _ = os.path.splitext(audio_path)
        json_path = base_path + ".json"
        
        data = [{"start": round(s['start'], 2), "end": round(s['end'], 2), "text": s['text'].strip()} for s in segments]
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return json_path
