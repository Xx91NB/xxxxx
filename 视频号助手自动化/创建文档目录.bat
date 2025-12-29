@echo off
chcp 65001 >nul
title 创建文档目录
echo.
echo 创建文档目录...
if not exist docs mkdir docs

echo # 视频号助手自动化使用说明 > docs\使用说明.txt
echo ============================ >> docs\使用说明.txt
echo. >> docs\使用说明.txt
echo 🎯 功能：语音控制自动点击"添加商品"按钮 >> docs\使用说明.txt
echo. >> docs\使用说明.txt
echo 📋 安装步骤： >> docs\使用说明.txt
echo 1. 运行 install.bat 安装依赖 >> docs\使用说明.txt
echo 2. 运行 capture_coords.bat 获取按钮坐标 >> docs\使用说明.txt
echo 3. 配置影刀RPA流程 >> docs\使用说明.txt
echo 4. 运行 start_system.bat 开始使用 >> docs\使用说明.txt
echo. >> docs\使用说明.txt
echo 🎤 语音关键词： >> docs\使用说明.txt
type config\keywords.txt >> docs\使用说明.txt
echo. >> docs\使用说明.txt
echo 📍 按钮坐标： >> docs\使用说明.txt
type config\button_coords.txt >> docs\使用说明.txt

echo # 故障排除指南 > docs\故障排除.txt
echo ==================== >> docs\故障排除.txt
echo. >> docs\故障排除.txt
echo ❓ 问题1：点击位置不准 >> docs\故障排除.txt
echo 💡 解决：运行 capture_coords.bat 重新获取坐标 >> docs\故障排除.txt
echo. >> docs\故障排除.txt
echo ❓ 问题2：语音不识别 >> docs\故障排除.txt
echo 💡 解决：检查VB-Cable虚拟音频线配置 >> docs\故障排除.txt
echo. >> docs\故障排除.txt
echo ❓ 问题3：影刀无响应 >> docs\故障排除.txt
echo 💡 解决：检查端口5500是否被占用 >> docs\故障排除.txt

echo ✅ 文档创建完成！
pause