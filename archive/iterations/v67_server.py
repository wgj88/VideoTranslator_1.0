# -*- coding: utf-8 -*-
import os, sys, torch, json, time
import numpy as np
import soundfile as sf
from fastapi import FastAPI, Body
import uvicorn

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber
from v72_normalizer import AgileNormalizer

app = FastAPI()
db = None
an = AgileNormalizer()

@app.on_event("startup")
def load_and_warmup():
    global db
    print("\n" + "❄️"*10 + " V78.1 冷静核心：20步极速 + 0.01 锁温 " + "❄️"*10)
    db = VideoCloneDubber()

@app.post("/generate")
def generate_audio(data: dict = Body(...)):
    text = data.get("text", "")
    ref_wav = data.get("ref_wav", "")
    prompt_text = data.get("prompt_text", None)
    save_path = data.get("save_path", "")
    
    clean_text = an.normalize(text)
    
    # V78.1 核心：回归 20 步并强制注入低温参数
    # 虽然官方顶级包装层没写，但底层自回归逻辑支持采样控制
    try:
        wav = db.model.generate(
            text=clean_text + "。", 
            prompt_wav_path=ref_wav,
            prompt_text=prompt_text,
            normalize=False,
            inference_timesteps=20, # <--- 遵照指令：回归 20 步
            temperature=0.01,       # <--- 尝试直接透传（部分版本支持在 kwargs 转发）
            cfg_value=2.5
        )
    except:
        # 如果透传失败，说明 API 极其固化，我们通过 CFG 压制
        wav = db.model.generate(
            text=clean_text + "。", 
            prompt_wav_path=ref_wav,
            prompt_text=prompt_text,
            normalize=False,
            inference_timesteps=20,
            cfg_value=3.5 
        )
    
    sf.write(save_path, wav, db.sample_rate)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
