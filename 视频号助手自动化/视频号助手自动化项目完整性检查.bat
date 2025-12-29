@echo off
chcp 65001 >nul
title 项目完整性检查
color 0E

echo.
echo ========================================================
echo   视频号助手自动化项目完整性检查
echo ========================================================
echo.

echo 📋 文件检查清单：
echo.

REM 检查批处理文件
set score=0
set total=5

echo 【批处理文件】：
if exist "【01_一键安装】install.bat" (echo ✅ install.bat 存在 & set /a score+=1) else (echo ❌ install.bat 缺失)
if exist "【02_一键启动】start_system.bat" (echo ✅ start_system.bat 存在 & set /a score+=1) else (echo ❌ start_system.bat 缺失)
if exist "【03_单独测试】test_click.bat" (echo ✅ test_click.bat 存在 & set /a score+=1) else (echo ❌ test_click.bat 缺失)
if exist "【04_获取坐标】capture_coords.bat" (echo ✅ capture_coords.bat 存在 & set /a score+=1) else (echo ❌ capture_coords.bat 缺失)
if exist "【05_卸载清理】uninstall.bat" (echo ✅ uninstall.bat 存在 & set /a score+=1) else (echo ⚠️ uninstall.bat 缺失)

echo.
echo 【Python脚本】：
if exist "scripts\shadow_ready.py" (echo ✅ shadow_ready.py 存在 & set /a score+=1) else (echo ❌ shadow_ready.py 缺失 - 必须修复！)
if exist "scripts\requirements.txt" (echo ✅ requirements.txt 存在 & set /a score+=1) else (echo ❌ requirements.txt 缺失 - 必须修复！)
if exist "scripts\live_listener.py" (echo ✅ live_listener.py 存在 & set /a score+=1) else (echo ⚠️ live_listener.py 缺失 - 可选)

echo.
echo 【配置文件】：
if exist "config" (echo ✅ config目录存在) else (echo ❌ config目录缺失 - 必须创建！)
if exist "config\button_coords.txt" (echo ✅ button_coords.txt 存在 & set /a score+=1) else (echo ❌ button_coords.txt 缺失 - 必须创建！)
if exist "config\keywords.txt" (echo ✅ keywords.txt 存在 & set /a score+=1) else (echo ⚠️ keywords.txt 缺失 - 推荐创建)

echo.
set /a total=8
set /a percent=score*100/total

echo ========================================================
echo 📊 检查结果：%score%/%total% (%percent%%%)
echo.

if %percent% geq 90 (
    echo 🎉 项目完整度优秀！
) else if %percent% geq 70 (
    echo 👍 项目基本完整
) else if %percent% geq 50 (
    echo ⚠️ 项目缺失重要文件
) else (
    echo ❌ 项目不完整，需要修复
)

echo.
echo 🔧 建议：
if not exist "scripts\shadow_ready.py" echo 1. 必须创建 scripts\shadow_ready.py
if not exist "config\button_coords.txt" echo 2. 必须创建 config\button_coords.txt
if not exist "【01_一键安装】install.bat" echo 3. 必须创建 install.bat

echo.
pause