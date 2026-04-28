# -*- coding: utf-8 -*-
import whisper, json, os
os.environ["PATH"] = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32" + os.pathsep + os.environ["PATH"]
model = whisper.load_model("base.en")
res = model.transcribe(r"E:\VideoTranslator_Project\unhinged_tech\boosted_vocals.wav")
with open(r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json", "w", encoding="utf-8") as f:
    json.dump(res['segments'], f, indent=2)
print(f"✅ 100% 原始剧本已物理归档：RAW_EN_SCRIPT.json")
