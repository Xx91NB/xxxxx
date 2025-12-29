#!/usr/bin/env python3
"""
shadow_ready.py - 最简点击脚本
功能：读取坐标文件，移动鼠标并点击
"""

import pyautogui
import time

# 读取坐标文件
with open(r"C:\Users\A\Desktop\视频号助手自动化\config\button_coords.txt", 'r') as f:
    content = f.read().strip()

# 解析坐标
x_str, y_str = content.split(',')
x = int(x_str.strip())
y = int(y_str.strip())

print(f"坐标: ({x}, {y})")

# 移动并点击
pyautogui.moveTo(x, y, duration=0.5)
time.sleep(0.3)
pyautogui.click()

print("点击完成！")