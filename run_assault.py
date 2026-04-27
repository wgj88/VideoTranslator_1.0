# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np, time
import librosa, torch, soundfile as sf

# --- 1. 物理环境加固 ---
PROJECT_ROOT = r"E:\VideoTranslator_Project"
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
YTDLP_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Scripts\yt-dlp.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [FFMPEG_BIN, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(PROJECT_ROOT)
from audio_separator import AudioSeparator
from transcriber import AudioTranscriber
from translator import VideoTranslator
from clone_dubber import VideoCloneDubber

def run_assault():
    print("\n" + "🔥"*10 + " 全自动猎手：黄金配方实战 " + "🔥"*10)
    
    # --- 阶段 A: 猎取新视频 (换一个超火的主题：AI Inventions 2026) ---
    query = "ytsearch1:cool gadgets for home 2026"
    print(f"[Search] 正在搜寻最新热门素材...")
    proxy = "http://127.0.0.1:7890"
    raw_dir = os.path.join(PROJECT_ROOT, "raw_videos")
    
    # 搜索并捕获 ID
    cmd_search = [YTDLP_BIN, '--proxy', proxy, '--get-id', '--match-filter', "duration > 40 & duration < 300", query]
    vid = subprocess.run(cmd_search, capture_output=True, text=True).stdout.strip()
    if not vid:
        print("❌ 搜索超时或未发现符合条件的视频。")
        return
    url = f"https://www.youtube.com/watch?v={vid}"
    print(f"🎯 捕获新猎物: {url}")

    # 下载 (使用合并模式)
    cmd_dl = [YTDLP_BIN, '--proxy', proxy, '-f', 'bestvideo+bestaudio/best', '--merge-output-format', 'mp4', '-o', f'{raw_dir}/%(title)s.%(ext)s', url]
    subprocess.run(cmd_dl, check=True)
    
    # 定位刚下载的文件 (寻找 2 分钟内创建的 MP4)
    v_mp4 = None
    for f in os.listdir(raw_dir):
        p = os.path.join(raw_dir, f)
        if (time.time() - os.path.getmtime(p)) < 120 and f.endswith(".mp4"):
            v_mp4 = p
            break
    if not v_mp4: 
        print("❌ 无法定位新下载的素材。")
        return
    print(f"🎬 物理素材已入库: {os.path.basename(v_mp4)}")

    # --- 阶段 B: 黄金配方处理 ---
    sep = AudioSeparator()
    # 1. 物理剥离
    bgm_wav, vocal_wav = sep.separate(v_mp4)
    
    # 2. 种子提取与识别
    ts = AudioTranscriber()
    db = VideoCloneDubber()
    seed_wav = os.path.join(PROJECT_ROOT, "separated_audio", "assault_seed.wav")
    subprocess.run([FFMPEG_BIN, "-y", "-i", vocal_wav, "-ss", "10", "-t", "3", seed_wav], check=True)
    ref_text = ts.model.transcribe(seed_wav)['text'].strip()
    print(f"🎤 音色种子识别成功: {ref_text}")

    # 3. 听译全篇并翻译
    raw_json = ts.process(vocal_wav)
    vt = VideoTranslator()
    zh_json = vt.translate_json(raw_json)

    # 4. 精准克隆配音 (前 8 句演示)
    with open(zh_json, "r", encoding="utf-8") as f: data = json.load(f)
    dub_folder = os.path.join(raw_dir, "assault_dubs_new")
    os.makedirs(dub_folder, exist_ok=True)
    
    valid_dubs = []
    for i in range(min(8, len(data))):
        item = data[i]
        text = re.sub(r'\(.*?\)|\[.*?\]', '', item.get('translated_text', '')).strip()
        if not text: continue
        print(f"  -> 正在克隆第 {i} 句...")
        wav = db.model.generate(text=text, prompt_wav_path=seed_wav, prompt_text=ref_text)
        out_p = os.path.join(dub_folder, f"dub_{i}.wav")
        sf.write(out_p, wav, db.sample_rate)
        item['dub_path'] = out_p
        valid_dubs.append(item)

    # 5. 终极合成
    final_out = os.path.join(PROJECT_ROOT, "output_final", "NEW_VIDEO_V5_STRIKE.mp4")
    input_args = []
    filter_parts = []
    for idx, item in enumerate(valid_dubs):
        input_args.extend(["-i", item['dub_path']])
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{idx+1}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_str = ";".join(filter_parts) + ";" + "".join([f"[a{k}]" for k in range(len(valid_dubs))]) + f"amix=inputs={len(valid_dubs)}[dub]"
    # 彻底静默原视频音轨，只合并纯 BGM + 中文配音
    final_filter = f"{mix_str};[0:a]volume=0[orig_silent];[dub]volume=1.0[v];[dub]amix=inputs=1[out_audio]" # 演示简化
    
    # 运行物理合成
    cmd = [FFMPEG_BIN, "-y", "-i", v_mp4] + input_args + ["-filter_complex", filter_str + f";[a0][a1][a2][a3][a4][a5][a6][a7]amix=8,volume=8[out]", "-map", "0:v", "-map", "[out]", "-c:v", "copy", final_out]
    subprocess.run(cmd, check=True)
    print(f"\n🏆 全自动实战大捷！作品已产出：{final_out}")

if __name__ == "__main__":
    run_assault()
