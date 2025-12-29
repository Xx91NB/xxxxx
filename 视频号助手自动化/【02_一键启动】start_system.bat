@echo off
chcp 65001 >nul
title 视频号助手自动化系统 - 一键启动

echo.
echo ========================================================
echo   视频号助手自动化系统
echo ========================================================
echo.

echo 📋 请确保：
echo 1. Edge浏览器已打开并登录
echo 2. 已进入"直播商品管理"页面
echo 3. "添加商品"按钮在屏幕可见位置
echo 4. 影刀RPA流程已启动（端口5500）
echo.

echo 请选择操作：
echo.
echo [1] 完整启动（语音监听 + 点击测试）
echo [2] 仅启动语音监听
echo [3] 仅测试点击功能
echo [4] 退出
echo.

set /p choice=请输入选择 (1-4): 

if "%choice%"=="1" goto full_start
if "%choice%"=="2" goto voice_only
if "%choice%"=="3" goto test_click
if "%choice%"=="4" exit /b 0

echo ❌ 无效选择
pause
exit /b 1

:full_start
echo.
echo 🚀 完整启动模式...
echo.
echo [1] 测试点击功能...
cd scripts
python shadow_ready.py
if errorlevel 1 (
    echo ❌ 点击测试失败
    pause
    exit /b 1
)
echo ✅ 点击测试成功
cd ..
echo.
echo [2] 启动语音监听服务...
start cmd /k "cd /d %~dp0scripts && python live_listener.py"
echo.
echo ✅ 系统启动完成！
echo 📝 语音监听窗口已打开，请不要关闭
echo 🎤 可以说出关键词："添加商品"、"一百八"、"上链接"
echo.
pause
exit /b 0

:voice_only
echo.
echo 🎤 仅启动语音监听...
start cmd /k "cd /d %~dp0scripts && python live_listener.py"
echo ✅ 语音监听已启动
pause
exit /b 0

:test_click
echo.
echo 🧪 测试点击功能...
cd scripts
python shadow_ready.py
cd ..
if errorlevel 0 (
    echo ✅ 点击测试成功
) else (
    echo ❌ 点击测试失败
)
pause
exit /b 0