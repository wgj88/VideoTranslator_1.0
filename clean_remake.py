# -*- coding: utf-8 -*-
import os, sys, json
sys.path.append(r"E:\VideoTranslator_Project")
from audio_separator import AudioSeparator
from transcriber import AudioTranscriber
from translator import VideoTranslator
from clone_dubber import VideoCloneDubber
from composer import VideoComposer

v = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"

def make_clean_sample():
    print(f"\n[CLEAN_REMAKE] 正在执行全净空重制：彻底剥离英文原音...")
    
    sep = AudioSeparator()
    ts = AudioTranscriber()
    vt = VideoTranslator()
    db = VideoCloneDubber()
    cp = VideoComposer()

    # 1. 剥离人声 (关键步)
    bgm_wav, vocal_wav = sep.separate(v)
    
    if bgm_wav:
        # 2. 听译 (听纯净人声，不会有乱码)
        raw_json = ts.process(vocal_wav)
        zh_json = vt.translate_json(raw_json)
        
        # 3. 克隆配音
        # 我们仍需一个参考音色，直接用刚才分离出的 vocal_wav
        ready_json = db.process_json_cloning(zh_json, vocal_wav, "reference text", limit=10)
        
        # 4. 终极合成：纯背景音 + 中文配音 (不带任何英文)
        final_out = cp.compose(v, ready_json, bgm_wav)
        
        if final_out:
            print(f"\n🏆 重制成功！这次是真的“纯净版”：{final_out}")

if __name__ == "__main__":
    make_clean_sample()
