# -*- coding: utf-8 -*-
import os, json, torch, soundfile as sf
from voxcpm import VoxCPM

class VideoDubber:
    def __init__(self, model_path=r"E:\VideoTranslator_Project\model_weights"):
        print(f"[Dubber] 正在初始化本地 VoxCPM 核心 (RTX 5060 Ti 模式)...")
        # load_denoiser=False 加快加载速度
        self.model = VoxCPM.from_pretrained(model_path, load_denoiser=False)
        self.sample_rate = self.model.tts_model.sample_rate

    def process_json(self, json_path, limit=None):
        print(f"\n[Dubber] 正在为 JSON 生成高保真配音: {json_path}")
        with open(json_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        audio_folder = json_path.replace(".json", "_vox_audio")
        os.makedirs(audio_folder, exist_ok=True)

        count = 0
        for i, item in enumerate(data):
            if limit and i >= limit: break
            
            text = item.get('translated_text', item['text'])
            segment_path = os.path.join(audio_folder, f"seg_{i}.wav")
            
            print(f"  -> 正在渲染第 {i} 句: {text[:40]}...")
            
            try:
                # 执行 VoxCPM 推理
                wav = self.model.generate(text=text)
                # 保存 48kHz 音频
                sf.write(segment_path, wav, self.sample_rate)
                item['dub_path'] = segment_path
                count += 1
            except Exception as e:
                print(f"  ⚠️ 渲染失败: {e}")

        # 写回更新后的 JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ 配音节点执行完毕！共生成 {count} 个高保真片段，保存至: {audio_folder}")
        return json_path

if __name__ == "__main__":
    print("VoxCPM 配音模块就绪。")
