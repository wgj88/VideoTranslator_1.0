# -*- coding: utf-8 -*-
import os, torch, soundfile as sf
from demucs.pretrained import get_model
from demucs.apply import apply_model

def run_ultra_separation():
    # 这一次我们使用被“洗”过的源文件
    input_wav = r"E:\VideoTranslator_Project\unhinged_tech\CLINICAL_CLEAN_SOURCE.wav"
    output_dir = r"E:\VideoTranslator_Project\unhinged_tech\separated_ultra"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n[Ultra-Separator] 正在基于【临床级纯净源】重新剥离人声...")
    model = get_model("htdemucs")
    model.to("cuda")
    model.eval()

    wav, sr = sf.read(input_wav)
    if wav.ndim == 1: wav = wav[:, None]
    wav_tensor = torch.from_numpy(wav.T).to("cuda").float()
    
    with torch.no_grad():
        # 执行 9 分钟深度剥离
        out_sources = apply_model(model, wav_tensor[None], device="cuda", split=True, overlap=0.25)[0]
    
    # 导出
    for idx, name in enumerate(model.sources):
        if name == "vocals": # 我们最在意的核心资产
            out_p = os.path.join(output_dir, f"ULTRA_CLEAN_VOCALS.wav")
            source_data = out_sources[idx].cpu().numpy().T
            sf.write(out_p, source_data, sr)
            print(f"  ✅ 巅峰级人声资产已导出: {out_p}")
        else:
            # 其他伴奏轨道也保存，供混音备用
            out_p = os.path.join(output_dir, f"{name}.wav")
            sf.write(out_p, out_sources[idx].cpu().numpy().T, sr)

if __name__ == "__main__":
    run_ultra_separation()
