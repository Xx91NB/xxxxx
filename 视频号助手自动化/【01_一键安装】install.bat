@echo off
chcp 65001 >nul
title 视频号助手自动化 - 一键安装

echo.
echo ========================================================
echo   视频号助手自动化系统安装程序
echo ========================================================
echo.

echo [1/5] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python已安装

echo.
echo [2/5] 创建目录结构...
if not exist "config" mkdir config
if not exist "scripts" mkdir scripts
if not exist "logs" mkdir logs
echo ✅ 目录创建完成

echo.
echo [3/5] 安装Python依赖库...
cd scripts
pip install pyautogui==0.9.54 vosk==0.3.45 requests==2.31.0 flask==2.3.3 pyaudio==0.2.11
cd ..
echo ✅ 依赖安装完成

echo.
echo [4/5] 配置系统参数...
echo 2816,488 > config\button_coords.txt
(
echo 添加商品
echo 一百八
echo 上链接
) > config\keywords.txt
echo ✅ 配置文件已生成

echo.
echo [5/5] 下载语音识别模型...
cd scripts
if not exist "vosk-model-small-cn-0.22" (
    echo 正在下载中文语音模型（约40MB）...
    curl -L "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip" -o model.zip
    if exist model.zip (
        tar -xf model.zip
        del model.zip
        echo ✅ 语音模型下载完成
    )
)
cd ..

echo.
echo ========================================================
echo   ✅ 安装完成！
echo ========================================================
echo.
echo 下一步操作：
echo 1. 运行 【04_获取坐标】capture_coords.bat 获取按钮位置
echo 2. 配置影刀RPA流程（端口5500，路径/trigger）
echo 3. 运行 【02_一键启动】start_system.bat 开始使用
echo.
pause