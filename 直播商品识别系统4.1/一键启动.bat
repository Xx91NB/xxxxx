# 创建一键启动脚本 start_smart.bat
@echo off
chcp 65001 > nul
title 智能商品识别系统
cd /d "%~dp0"
python smart_main.py
pause