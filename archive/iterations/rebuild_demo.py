import sys, os, json
sys.path.append(r'E:\VideoTranslator_Project')
from transcriber import AudioTranscriber
from translator import VideoTranslator

# 1. 定义文件路径
video_file = r'E:\VideoTranslator_Project\raw_videos\8 EASY Faceless YouTube Channel Ideas for 2026 (High RPM + Views).mp4'

print(f"[Rebuild] 正在对目标视频进行重修: {os.path.basename(video_file)}")

# 2. 重新听译 (获取干净的原文)
ts = AudioTranscriber(model_size="base")
raw_json = ts.process(video_file)

if raw_json:
    # 3. 调用修复后的翻译器 (硅基流动)
    vt = VideoTranslator()
    zh_json = vt.translate_json(raw_json)
    
    # 4. 立即展示前 5 句汉化结果
    with open(zh_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print("\n--- 🛠️ 汉化质量核查清单 ---")
        for item in data[:5]:
            zh_text = item.get('translated_text', '翻译失败')
            print(f"原文: {item['text']}")
            print(f"译文: {zh_text}")
            print("-" * 30)
