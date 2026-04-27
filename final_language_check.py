# -*- coding: utf-8 -*-
import os, whisper, json

# 注入路径
os.environ["PATH"] = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32" + os.pathsep + os.environ["PATH"]

def check_language():
    audit_file = r"E:\VideoTranslator_Project\output_final\PURE_DUB_AUDIT.wav"
    if not os.path.exists(audit_file):
        print("❌ 文件不存在")
        return

    print(f"--- 正在鉴定语种: {audit_file} ---")
    model = whisper.load_model("base")
    # 只听前 30 秒
    result = model.transcribe(audit_file)
    
    print(f"DETECTED_LANG: {result['language']}")
    print(f"CONTENT_PREVIEW: {result['text'][:100]}")

    # 查阅目录
    files = os.listdir(r"E:\VideoTranslator_Project\FINAL_DUB_TEMP")
    print(f"DIRECTORY_CONTENT: {files}")

if __name__ == "__main__":
    check_language()
