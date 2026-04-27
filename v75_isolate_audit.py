# -*- coding: utf-8 -*-
import os, sys, shutil

def isolate_segments():
    print("\n--- 🎧 正在单独提取 03 和 04 段音频供您审计 ---")
    
    # 指向 V74 生成的缓存目录
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v74_batch_run"
    output_dir = r"E:\VideoTranslator_Project\output_final"
    
    # 片段 03 对应索引 2 (raw_2.wav)
    # 片段 04 对应索引 3 (raw_3.wav)
    src_03 = os.path.join(temp_dir, "raw_2.wav")
    src_04 = os.path.join(temp_dir, "raw_3.wav")
    
    dst_03 = os.path.join(output_dir, "V75_AUDIT_SEG_03.wav")
    dst_04 = os.path.join(output_dir, "V75_AUDIT_SEG_04.wav")
    
    if os.path.exists(src_03):
        shutil.copy(src_03, dst_03)
        print(f"✅ 03 段（量子科技）已提取：{dst_03}")
    else:
        print("❌ 未找到 03 段原始文件")
        
    if os.path.exists(src_04):
        shutil.copy(src_04, dst_04)
        print(f"✅ 04 段（一年一度）已提取：{dst_04}")
    else:
        print("❌ 未找到 04 段原始文件")

if __name__ == "__main__":
    isolate_segments()
