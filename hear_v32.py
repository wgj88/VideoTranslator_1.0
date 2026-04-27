# -*- coding: utf-8 -*-
import whisper, os
os.environ["PATH"] = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32" + os.pathsep + os.environ["PATH"]
model = whisper.load_model("base")
res = model.transcribe(r"E:\VideoTranslator_Project\output_final\V32_OFFICIAL_PARAMS_AUDIT.wav")
print(f"TRANSCRIPT: {res['text']}")
