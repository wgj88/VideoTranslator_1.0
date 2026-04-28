# -*- coding: utf-8 -*-
import os, torch, soundfile as sf
from demucs.pretrained import get_model
from demucs.apply import apply_model

def run_v2():
    input_wav = r"E:\VideoTranslator_Project\unhinged_tech\aligned_input.wav"
    output_dir = r"E:\VideoTranslator_Project\unhinged_tech\separated"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n[Separator-V2] 正在手动加载 htdemucs 模型 (Cuda:0)...")
    model = get_model("htdemucs")
    model.to("cuda")
    model.eval()

    # 1. 读取音频 (soundfile 绝对稳健)
    wav, sr = sf.read(input_wav)
    if wav.ndim == 1: wav = wav[:, None]
    
    # 转为 [channels, samples]
    wav_tensor = torch.from_numpy(wav.T).to("cuda").float()
    
    # 物理分块处理（防止显存 OOM，因为视频有 9 分钟）
    print("  -> 正在启动流式物理剥离...")
    # apply_model 内部已经包含了复杂的重对齐逻辑
    with torch.no_grad():
        # 我们一次处理 10 秒
        out_sources = apply_model(model, wav_tensor[None], device="cuda", split=True, overlap=0.25)[0]
    
    # 2. 导出
    # model.sources 通常是 ['drums', 'bass', 'other', 'vocals']
    for idx, name in enumerate(model.sources):
        out_p = os.path.join(output_dir, f"{name}.wav")
        source_data = out_sources[idx].cpu().numpy().T
        sf.write(out_p, source_data, sr)
        print(f"  ✅ 导出资产: {out_p}")

if __name__ == "__main__":
    run_v2()
