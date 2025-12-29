@echo off
chcp 65001 >nul
title 视频号助手自动化 - 一键完成所有
color 0E

echo.
echo ========================================================
echo   视频号助手自动化 - 完整流程
echo ========================================================
echo.

:menu
echo 请选择操作：
echo.
echo [1] 运行最终系统验证
echo [2] 生成安装包（用于分享）
echo [3] 测试当前系统功能
echo [4] 重新获取按钮坐标
echo [5] 查看项目文件清单
echo [6] 退出
echo.

set /p choice=请输入选择 (1-6): 

if "%choice%"=="1" goto verify
if "%choice%"=="2" goto package
if "%choice%"=="3" goto test
if "%choice%"=="4" goto capture
if "%choice%"=="5" goto list
if "%choice%"=="6" exit /b 0

echo ❌ 无效选择
goto menu

:verify
echo.
echo 🔍 运行系统验证...
call final_check.bat
goto menu

:package
echo.
echo 📦 生成安装包...
if not exist "【06_打包发布】make_package.bat" (
    echo ❌ 未找到打包脚本
    echo 请先创建 【06_打包发布】make_package.bat
    pause
) else (
    call "【06_打包发布】make_package.bat"
)
goto menu

:test
echo.
echo 🧪 测试系统功能...
call "【03_单独测试】test_click.bat"
goto menu

:capture
echo.
echo 📍 重新获取坐标...
call "【04_获取坐标】capture_coords.bat"
goto menu

:list
echo.
echo 📁 项目文件清单：
echo.
dir /B
echo.
echo 📁 scripts\ 目录：
dir scripts /B
echo.
echo 📁 config\ 目录：
dir config /B
echo.
pause
goto menu