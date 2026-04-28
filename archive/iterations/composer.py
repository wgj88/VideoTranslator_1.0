# -*- coding: utf-8 -*-
import ffmpeg, json, os

class VideoComposer:
    def __init__(self, output_dir=r"E:\VideoTranslator_Project\output_final"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        from static_ffmpeg import add_paths
        add_paths()

    def compose_pure_dub(self, video_path, json_path):
        file_name = os.path.basename(video_path).replace(".mp4", "")
        output_path = os.path.join(self.output_dir, f"{file_name}_REFIXED.mp4")
        
        print(f"\n[Composer] 正在重构时间轴，修复“堆叠”问题...")
        
        with open(json_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        v_stream = ffmpeg.input(video_path).video

        # --- 核心修复：构建真正带有时间延迟的音频流列表 ---
        delayed_streams = []
        for i, item in enumerate(data):
            if 'dub_path' in item and os.path.exists(item['dub_path']):
                delay_ms = int(item['start'] * 1000)
                # 每一句配音都先套一个 adelay 滤镜，将其推到对应的 start 秒
                audio_stream = ffmpeg.input(item['dub_path']).audio.filter('adelay', f"{delay_ms}|{delay_ms}")
                delayed_streams.append(audio_stream)
            if i >= 14: break # 测试期只处理前 15 句

        if not delayed_streams:
            print("❌ 错误：没有可用的配音片段")
            return None

        # 将这些带延迟的流“物理混合”在一起
        mixed_audio = ffmpeg.filter(delayed_streams, 'amix', inputs=len(delayed_streams), duration='longest')

        # 执行压制
        try:
            (
                ffmpeg
                .output(v_stream, mixed_audio, output_path, vcodec='h264_nvenc', acodec='aac')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            print(f"✅ 修复成功！请查看 REFIXED 版本：{output_path}")
            return output_path
        except ffmpeg.Error as e:
            print(f"❌ 合成失败: {e.stderr.decode()}")
            return None

if __name__ == "__main__":
    print("Fixed Composer Ready.")
