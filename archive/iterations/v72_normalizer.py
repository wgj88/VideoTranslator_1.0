# -*- coding: utf-8 -*-
import re, cn2an

class AgileNormalizer:
    def normalize(self, text):
        # 1. 基础物理清洗
        text = text.replace("：", "。").replace(":", "。").replace("——", "，")
        
        # 2. 百分比处理 (17% -> 百分之十七)
        text = re.sub(r'(\d+)%', lambda m: "百分之" + cn2an.an2cn(m.group(1)), text)
        
        # 3. 年份处理 (2026年 -> 二零二六年)
        def fix_year(m):
            year_str = m.group(1)
            return "".join(["零一二三四五六七八九"[int(d)] for d in year_str]) + "年"
        text = re.sub(r'(\d{4})年', fix_year, text)
        
        # 4. 金额与通用数字 (3500$ -> 三千五百美元)
        text = text.replace("$", "美元")
        def replace_general_num(match):
            num = match.group()
            try: return cn2an.an2cn(num)
            except: return num
        text = re.sub(r'\d+', replace_general_num, text)
        
        return text

if __name__ == "__main__":
    an = AgileNormalizer()
    test = "现在是2026年，冰箱值3500$，还有17%的折扣。"
    print(f"最终净化效果: {an.normalize(test)}")
