@echo off
chcp 65001 >nul
title 安全补充缺失文件

echo.
echo ========================================================
echo   安全补充缺失文件（不覆盖已有文件）
echo ========================================================
echo.

echo 📋 检查并创建缺失文件...
echo.

REM 检查并创建run.py
if not exist "run.py" (
    echo 创建 run.py...
    echo # Python启动器 > run.py
    echo import os >> run.py
    echo print("视频号助手自动化") >> run.py
    echo print("运行 python scripts\live_listener.py 启动语音监听") >> run.py
    echo input("按Enter退出...") >> run.py
    echo ✅ run.py 已创建
) else (
    echo ✅ run.py 已存在（保留原文件）
)

REM 检查并创建使用说明.txt
if not exist "使用说明.txt" (
    echo 创建 使用说明.txt...
    echo 视频号助手自动化系统使用说明 > 使用说明.txt
    echo ============================ >> 使用说明.txt
    echo. >> 使用说明.txt
    echo 1. 运行 install.bat 安装依赖 >> 使用说明.txt
    echo 2. 运行 start_system.bat 启动系统 >> 使用说明.txt
    echo ✅ 使用说明.txt 已创建
) else (
    echo ✅ 使用说明.txt 已存在（保留原文件）
)

REM 检查批处理文件内容是否完整
echo.
echo 🔍 检查批处理文件内容...
for %%f in (
    "【01_一键安装】install.bat"
    "【02_一键启动】start_system.bat"
    "【03_单独测试】test_click.bat"
    "【04_获取坐标】capture_coords.bat"
    "【05_卸载清理】uninstall.bat"
    "【06_打包发布】make_package.bat"
) do (
    if exist %%f (
        for /f %%s in ("%%f") do (
            if %%~zs LSS 100 (
                echo ⚠️ %%f 文件过小（可能内容被清空）
                echo   当前大小：%%~zs 字节
            ) else (
                echo ✅ %%f 大小正常
            )
        )
    ) else (
        echo ❌ %%f 文件缺失
    )
)

echo.
echo 📁 当前项目结构：
dir /B
echo.
echo 📁 scripts目录：
if exist scripts dir scripts /B
echo.
echo 📁 config目录：
if exist config dir config /B

echo.
echo ========================================================
echo   ✅ 检查完成！
echo ========================================================
echo.
echo 🔧 建议操作：
echo 1. 如果批处理文件被清空，请手动复制完整代码
echo 2. 使用 python run.py 可避免杀毒软件拦截
echo 3. 运行 final_check.bat 验证系统完整性
echo.
pause