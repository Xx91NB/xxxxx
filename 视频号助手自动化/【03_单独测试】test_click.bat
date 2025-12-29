@echo off
chcp 65001 >nul
title 点击功能测试

echo.
echo ========================================================
echo   点击功能测试
echo ========================================================
echo.

if not exist "config\button_coords.txt" (
    echo ❌ 未找到坐标配置文件
    echo 请先运行 【04_获取坐标】capture_coords.bat
    pause
    exit /b 1
)

echo 📍 读取坐标配置...
set /p coords=<config\button_coords.txt
echo ✅ 坐标: %coords%

echo.
echo ⚠️ 测试前请确认：
echo 1. Edge浏览器窗口已打开
echo 2. 视频号助手页面已加载
echo 3. "添加商品"按钮在屏幕可见位置
echo.

set /p confirm=是否开始测试？(Y/N): 

if /i "%confirm%" neq "Y" (
    echo ❌ 测试取消
    pause
    exit /b 0
)

echo.
echo 🎯 开始测试点击...
cd scripts
python shadow_ready.py
set exit_code=%errorlevel%
cd ..

echo.
if %exit_code% equ 0 (
    echo ✅ 测试成功！按钮应已被点击
) else (
    echo ❌ 测试失败，请检查
)

echo.
pause
exit /b %exit_code%