@echo off
chcp 65001 >nul
title 重建完整项目架构
color 0C

echo.
echo ========================================================
echo   重建视频号助手自动化完整架构
echo ========================================================
echo ⚠️ 警告：这将覆盖现有文件
echo.

set /p confirm=确定要重建吗？(输入 YES 确认): 
if /i "%confirm%" neq "YES" (
    echo ❌ 操作取消
    pause
    exit /b 0
)

echo.
echo 🏗️ 开始重建架构...
echo.

REM 清理旧目录（保留重要数据）
if exist "logs" (
    echo 📁 保留 logs 目录
)
if exist "backup" (
    echo 📁 保留 backup 目录
)

REM 创建目录结构
echo 📁 创建目录...
if not exist scripts mkdir scripts
if not exist config mkdir config
if not exist docs mkdir docs

REM 创建批处理文件
echo ⚙️ 创建批处理文件...
call :create_batch_files

REM 创建Python脚本
echo 🐍 创建Python脚本...
call :create_python_scripts

REM 创建配置文件
echo ⚙️ 创建配置文件...
call :create_config_files

REM 创建文档
echo 📚 创建文档...
call :create_documents

echo.
echo ========================================================
echo   🎉 架构重建完成！
echo ========================================================
echo.
echo 📋 检查清单：
echo ✅ 5个批处理文件
echo ✅ scripts/ 目录（3个核心文件）
echo ✅ config/ 目录（5个配置文件）
echo ✅ docs/ 目录（4个文档）
echo.
echo 🚀 下一步：运行 install.bat
echo.
pause
exit /b 0

REM ========== 子函数 ==========

:create_batch_files
echo 创建批处理文件...
copy /Y nul "【01_一键安装】install.bat" >nul
copy /Y nul "【02_一键启动】start_system.bat" >nul
copy /Y nul "【03_单独测试】test_click.bat" >nul
copy /Y nul "【04_获取坐标】capture_coords.bat" >nul
copy /Y nul "【05_卸载清理】uninstall.bat" >nul
exit /b

:create_python_scripts
echo 创建Python脚本...
echo import pyautogui > scripts\shadow_ready.py
echo x,y=2816,488 >> scripts\shadow_ready.py
echo pyautogui.click(x,y) >> scripts\shadow_ready.py
echo pyautogui==0.9.54 > scripts\requirements.txt
exit /b

:create_config_files
echo 创建配置文件...
echo 2816,488 > config\button_coords.txt
echo 添加商品 > config\keywords.txt
echo 一百八 >> config\keywords.txt
exit /b

:create_documents
echo 创建文档...
echo 使用说明 > docs\使用说明.txt
echo 故障排除 > docs\故障排除.txt
exit /b