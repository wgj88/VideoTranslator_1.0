# -*- coding: utf-8 -*-
import sys, os, json, subprocess
sys.path.append(r"E:\VideoTranslator_Project")
from speaker_diarizer import SpeakerDiarizer
from translator import VideoTranslator
from clone_dubber import VideoCloneDubber
from composer import VideoComposer

v = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
vocal_src = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"

def run_multi_speaker_factory():
    print("\n" + "🎭"*10 + " 自动化工厂 V4.0：多角色同步复刻版 " + "🎭"*10)
    
    sd = SpeakerDiarizer()
    vt = VideoTranslator()
    db = VideoCloneDubber()
    cp = VideoComposer()
    
    # 1. 深度识别：谁在说话？
    json_with_speakers = sd.process_with_speakers(vocal_src)
    
    # 2. 为每个角色提取“黄金声纹”
    with open(json_with_speakers, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    speakers = set(item['speaker'] for item in data if item['speaker'] != "UNKNOWN")
    speaker_seeds = {}
    
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    
    print("\n[V4.0] 正在为每个角色提取黄金声纹样本...")
    for spk in speakers:
        # 寻找该角色说话最长的一段作为样本
        best_seg = max([d for d in data if d['speaker'] == spk], key=lambda x: x['end'] - x['start'])
        ref_path = f"E:\\VideoTranslator_Project\\separated_audio\\{spk}_seed.wav"
        
        start = best_seg['start']
        dur = min(5, best_seg['end'] - best_seg['start']) # 截取前 5 秒
        subprocess.run([ffmpeg_bin, "-y", "-i", vocal_src, "-ss", str(start), "-t", str(dur), ref_path], check=True, capture_output=True)
        speaker_seeds[spk] = ref_path
        print(f"  ✨ {spk} 样本已锁定: {ref_path}")

    # 3. 翻译 (带上角色属性)
    zh_json = vt.translate_json(json_with_speakers)

    # 4. 执行多音色并行克隆
    print("\n[V4.0] 正在按照角色身份执行并行克隆...")
    # 我们处理前 10 句
    with open(zh_json, "r", encoding="utf-8") as f:
        final_data = json.load(f)

    # 改造：根据 Speaker ID 动态切换 ref_wav
    audio_folder = zh_json.replace(".json", "_multi_cloned")
    os.makedirs(audio_folder, exist_ok=True); os.makedirs(r"E:\VideoTranslator_Project\separated_audio", exist_ok=True)
    
    for i in range(min(10, len(final_data))):
        item = final_data[i]
        spk = item['speaker']
        ref_wav = speaker_seeds.get(spk)
        
        if ref_wav:
            print(f"  -> 正在复刻 {spk} 的中文语音: {item['text'][:15]}...")
            # 调用克隆
            wav = db.model.generate(text=item['translated_text'], prompt_wav_path=ref_wav)
            out_p = os.path.join(audio_folder, f"seg_{i}.wav")
            import soundfile as sf
            sf.write(out_p, wav, db.sample_rate)
            item['dub_path'] = out_p

    # 保存最终 JSON 并合成
    with open(zh_json, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    cp.compose_pure_dub(v, zh_json)
    print(f"\n🏆 V4.0 全角色大捷！作品已生成。")

if __name__ == "__main__":
    run_multi_speaker_factory()
