@echo off
chcp 65001 >nul
title 卸载清理工具

echo.
echo ========================================================
echo   卸载清理工具
echo ========================================================
echo ⚠️ 警告：此操作将删除配置文件
echo.

set /p confirm=确定要卸载吗？(输入 YES 确认): 

if /i "%confirm%" neq "YES" (
    echo ❌ 卸载取消
    pause
    exit /b 0
)

echo.
echo 🗑️ 开始清理...
echo.

if exist "config" (
    rmdir /s /q config
    echo ✅ 删除配置目录
)

if exist "logs" (
    rmdir /s /q logs
    echo ✅ 删除日志目录
)

echo.
echo 📝 以下文件被保留：
echo • scripts\ 目录中的Python脚本
echo • 批处理文件
echo.
echo ✅ 清理完成！
echo.
pause