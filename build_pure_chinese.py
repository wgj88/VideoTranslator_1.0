# -*- coding: utf-8 -*-
import sys, os
sys.path.append(r"E:\VideoTranslator_Project")
from composer import VideoComposer

v = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
j = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"

if not os.path.exists(j):
    print(f"ERROR: JSON not found at {j}")
    sys.exit(1)

cp = VideoComposer()
result = cp.compose_pure_dub(v, j)
if result:
    print(f"\n🏆 样板房打造成功！请前往查看：{result}")
