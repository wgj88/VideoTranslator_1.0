# -*- coding: utf-8 -*-
import os, torch, numpy as np, subprocess, json
import soundfile as sf
from pyannote.audio import Model, Inference
from sklearn.cluster import KMeans
from pyannote.core import Annotation, Segment

def run():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Model.from_pretrained(r"E:\VideoTranslator_Project\models\pyannote")
    model.to(device)
    inference = Inference(model, device=device)
    v_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    
    wav, sr = sf.read(v_src)
    if len(wav.shape) == 1: wav = np.expand_dims(wav, axis=0)
    else: wav = wav.T
    payload = {"waveform": torch.from_numpy(wav).float(), "sample_rate": sr}
    
    res = inference(payload)
    data = res.data.reshape(-1, res.data.shape[2])
    
    active_mask = np.max(data, axis=1) > 0.2
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    labels = kmeans.fit_predict(data[active_mask])
    
    annotation = Annotation()
    full_labels = np.zeros(len(data), dtype=int) - 1
    full_labels[active_mask] = labels
    
    frame_dur = 147.9 / len(data)
    for i in range(len(full_labels)):
        l = full_labels[i]
        if l != -1:
            if i == 0 or full_labels[i-1] != l: start_f = i
            if i == len(full_labels)-1 or full_labels[i+1] != l:
                annotation[Segment(start_f*frame_dur, i*frame_dur)] = f"SPEAKER_{l:02d}"

    ffmpeg = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    for role in annotation.labels():
        target = max(annotation.label_timeline(role), key=lambda x: x.duration)
        out_wav = f"E:\\VideoTranslator_Project\\separated_audio\\cluster_{role}_final.wav"
        subprocess.run([ffmpeg, "-y", "-i", v_src, "-ss", str(target.start), "-t", "5", out_wav], capture_output=True)
        print(f"DONE: {role} -> {out_wav}")

if __name__ == "__main__":
    run()
