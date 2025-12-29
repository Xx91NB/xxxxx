@echo off
chcp 65001 >nul
title 生成安装包
color 0B

echo.
echo ========================================================
echo   生成视频号助手自动化安装包
echo ========================================================
echo.

echo 📋 检查文件...
if not exist "scripts\shadow_ready.py" (
    echo ❌ 错误：缺少核心脚本
    pause
    exit /b 1
)

if not exist "config\button_coords.txt" (
    echo ❌ 错误：缺少坐标文件
    pause
    exit /b 1
)

echo ✅ 所有必要文件存在
echo.

REM 创建时间戳
set "year=%date:~0,4%"
set "month=%date:~5,2%"
set "day=%date:~8,2%"
set "hour=%time:~0,2%"
set "minute=%time:~3,2%"
set "timestamp=%year%%month%%day%_%hour%%minute%"

echo 📦 创建安装包：视频号助手自动化_%timestamp%.zip
echo.

REM 创建临时目录
if exist "_temp_package" rmdir /s /q "_temp_package"
mkdir "_temp_package"

echo 📄 复制文件...
copy "【01_一键安装】install.bat" "_temp_package\"
copy "【02_一键启动】start_system.bat" "_temp_package\"
copy "【03_单独测试】test_click.bat" "_temp_package\"
copy "【04_获取坐标】capture_coords.bat" "_temp_package\"
copy "【05_卸载清理】uninstall.bat" "_temp_package\"

xcopy "scripts" "_temp_package\scripts\" /E /I /Y
xcopy "config" "_temp_package\config\" /E /I /Y

REM 创建说明文件
echo # 视频号助手自动化系统 > "_temp_package\README.txt"
echo ======================== >> "_temp_package\README.txt"
echo. >> "_temp_package\README.txt"
echo 🚀 安装步骤： >> "_temp_package\README.txt"
echo 1. 运行 install.bat 安装依赖 >> "_temp_package\README.txt"
echo 2. 运行 capture_coords.bat 获取按钮坐标 >> "_temp_package\README.txt"
echo 3. 配置影刀RPA（端口5500，路径/trigger） >> "_temp_package\README.txt"
echo 4. 运行 start_system.bat 开始使用 >> "_temp_package\README.txt"
echo. >> "_temp_package\README.txt"
echo 🎤 语音关键词： >> "_temp_package\README.txt"
type config\keywords.txt >> "_temp_package\README.txt"
echo. >> "_temp_package\README.txt"
echo 📍 默认坐标：2816,488 >> "_temp_package\README.txt"
echo 📅 打包时间：%date% %time% >> "_temp_package\README.txt"

echo.
echo 🔧 正在压缩...
powershell -Command "Compress-Archive -Path '_temp_package\*' -DestinationPath '视频号助手自动化_%timestamp%.zip' -Force"

REM 清理
rmdir /s /q "_temp_package"

if exist "视频号助手自动化_%timestamp%.zip" (
    echo.
    echo ✅ 安装包生成成功！
    echo 📂 文件名：视频号助手自动化_%timestamp%.zip
    echo.
    echo 🎯 使用方法：
    echo 1. 将此ZIP文件发给其他人
    echo 2. 对方解压后运行 install.bat
    echo 3. 按照提示完成安装
) else (
    echo ❌ 生成失败
)

echo.
pause