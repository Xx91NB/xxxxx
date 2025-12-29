@echo off
chcp 65001 > nul
title 屏幕视频识别系统
cd /d "%~dp0"

echo.
echo ========================================
echo        屏幕视频识别系统
echo         识别电脑桌面播放的视频
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    echo.
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查并安装依赖
echo 检查依赖...
python -c "import mss" 2>nul
if errorlevel 1 (
    echo 安装屏幕捕获依赖...
    pip install mss pyautogui pillow
)

:: 创建必要目录
if not exist "data\images_material" mkdir data\images_material
if not exist "outputs\screen_matches" mkdir outputs\screen_matches
if not exist "config" mkdir config

:: 运行屏幕识别系统
echo 启动屏幕识别系统...
python screen_recognition.py

pause