@echo off
chcp 65001 >nul
title 创建配置文件目录
color 0A

echo.
echo ========================================================
echo   创建配置文件目录
echo ========================================================
echo.

REM 创建目录
echo 📁 创建目录结构...
if exist config (
    echo ⚠️ config目录已存在，备份旧文件...
    if not exist config_backup mkdir config_backup
    copy config\* config_backup\ >nul 2>&1
    rmdir /s /q config
)

mkdir config
echo ✅ 创建 config 目录

REM 创建坐标文件
echo 📍 创建坐标文件...
echo 2816,488 > config\button_coords.txt
echo ✅ 坐标文件创建完成
echo   内容：2816,488

REM 创建关键词文件
echo 🎤 创建关键词文件...
(
echo 添加商品
echo 一百八
echo 上链接
echo 讲解
echo 上架
) > config\keywords.txt
echo ✅ 关键词文件创建完成
echo   关键词：添加商品、一百八、上链接、讲解、上架

REM 创建语音配置文件
echo ⚙️ 创建语音配置文件...
(
echo [语音设置]
echo 模型路径 = vosk-model-small-cn-0.22
echo 采样率 = 16000
echo 触发URL = http://127.0.0.1:5500/trigger
echo 灵敏度 = 0.8
echo 静音阈值 = 500
) > config\voice_config.ini
echo ✅ 语音配置文件创建完成

REM 创建影刀配置文件
echo 🤖 创建影刀配置文件...
(
echo [影刀设置]
echo 点击脚本 = scripts\shadow_ready.py
echo 等待时间 = 2
echo 重试次数 = 3
echo 超时时间 = 10
) > config\shadow_config.ini
echo ✅ 影刀配置文件创建完成

REM 创建系统配置文件
echo ⚙️ 创建系统配置文件...
(
echo [系统设置]
echo 版本 = 1.0.0
echo 创建时间 = %date% %time%
echo 作者 = 视频号助手自动化
echo.
echo [屏幕设置]
echo 分辨率 = 1920x1080
echo 缩放比例 = 100%%
echo 主显示器 = 1
echo.
echo [浏览器设置]
echo 浏览器 = Microsoft Edge
echo 版本 = 143.0.3650.96
echo 调试端口 = 9222
) > config\system_config.ini
echo ✅ 系统配置文件创建完成

echo.
echo ========================================================
echo   ✅ 配置文件创建完成！
echo ========================================================
echo.
echo 📁 创建的配置文件：
echo • config\button_coords.txt    - 按钮坐标
echo • config\keywords.txt         - 语音关键词
echo • config\voice_config.ini     - 语音设置
echo • config\shadow_config.ini    - 影刀设置
echo • config\system_config.ini    - 系统设置
echo.
echo 🔧 使用方法：
echo 1. 如果需要修改坐标，编辑 button_coords.txt
echo 2. 如果需要添加关键词，编辑 keywords.txt
echo 3. 其他配置一般不需要修改
echo.
pause