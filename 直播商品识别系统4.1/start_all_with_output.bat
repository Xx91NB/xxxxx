@echo off
chcp 936 > nul
title 直播商品识别系统 - 完整输出版
cd /d "%~dp0"

echo.
echo ========================================
echo        直播商品识别系统 4.1
echo          带完整TXT输出功能
echo ========================================
echo.

:: 1. 检查Python
echo [1/6] 检查Python安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    echo.
    echo 下载地址: https://www.python.org/downloads/
    echo 安装后请重启系统，或将Python添加到PATH环境变量
    pause
    exit /b 1
)
python --version
echo 正确 Python已安装

:: 2. 检查并安装依赖
echo.
echo [2/6] 检查Python依赖...
echo 正在检查opencv...
python -c "import cv2; print('正确 OpenCV版本:', cv2.__version__)" 2>nul
if errorlevel 1 (
    echo 错误 OpenCV未安装，正在安装...
    pip install opencv-python opencv-contrib-python numpy
    if errorlevel 1 (
        echo [错误] OpenCV安装失败
        echo 请手动运行: pip install opencv-python opencv-contrib-python
        pause
        exit /b 1
    )
)

echo 正在检查其他依赖...
python -c "import yaml, numpy, PIL, mss, pyautogui; print('正确 所有依赖已安装')" 2>nul
if errorlevel 1 (
    echo 正在安装其他依赖...
    pip install pyyaml pillow mss pyautogui
    if errorlevel 1 (
        echo [警告] 部分依赖安装失败，继续运行...
    )
)

:: 3. 创建目录结构
echo.
echo [3/6] 创建必要目录...
if not exist "data" mkdir data
if not exist "data\images_material" mkdir data\images_material
if not exist "data\learned_samples" mkdir data\learned_samples
if not exist "outputs" mkdir outputs
if not exist "config" mkdir config
if not exist "logs" mkdir logs
echo 正确 目录创建完成

:: 4. 检查项目文件
echo.
echo [4/6] 检查项目文件...
if not exist "output_manager.py" (
    echo [错误] 未找到output_manager.py文件
    echo 请确保所有项目文件在同一目录下
    pause
    exit /b 1
)

if not exist "smart_main.py" (
    echo [错误] 未找到smart_main.py文件
    pause
    exit /b 1
)

if not exist "screen_recognition.py" (
    echo [错误] 未找到screen_recognition.py文件
    pause
    exit /b 1
)

echo 正确 项目文件检查完成

:: 5. 初始化输出管理器 - 简化版
echo.
echo [5/6] 初始化输出管理器...

:: 使用简单的单行Python命令测试输出管理器
python -c "import sys; sys.path.append('.'); from output_manager import get_output_manager; mgr = get_output_manager(); print('正确 输出管理器初始化成功'); print('输出文件:'); [print('  -', name, ':', path) for name, path in mgr.output_files.items()]"

if errorlevel 1 (
    echo [错误] 输出管理器初始化失败
    pause
    exit /b 1
)

:: 6. 启动菜单系统
echo.
echo [6/6] 准备启动系统...
echo 正确 所有检查完成
timeout /t 2 /nobreak >nul

:menu
cls
echo ========================================
echo           直播商品识别系统 4.1
echo          请选择运行模式
echo ========================================
echo.
echo  1. 智能实时检测 (带自动学习)
echo  2. 屏幕视频识别 (桌面视频)
echo  3. 输出文件监控
echo  4. 查看当前识别结果
echo  5. 查看所有日志
echo  6. 系统测试
echo  7. 清空所有日志
echo  8. 打开输出目录
echo  9. 退出
echo.
set /p choice="请输入选项 (1-9): "

if "%choice%"=="1" (
    cls
    echo ========================================
    echo          启动智能实时检测
    echo ========================================
    echo.
    echo 注意: 
    echo 1. 确保摄像头已连接
    echo 2. 按 q 退出程序
    echo 3. 按 s 保存截图
    echo 4. 按 l 手动学习
    echo.
    echo 正在启动...
    python smart_main.py
    pause
    goto menu
)

if "%choice%"=="2" (
    cls
    echo ========================================
    echo          启动屏幕视频识别
    echo ========================================
    echo.
    echo 注意:
    echo 1. 请将要识别的视频在桌面上播放
    echo 2. 系统会识别视频中的商品
    echo 3. 按 q 退出程序
    echo.
    echo 正在启动...
    python screen_recognition.py
    pause
    goto menu
)

if "%choice%"=="3" (
    cls
    echo ========================================
    echo          启动输出监控
    echo ========================================
    echo.
    echo 注意:
    echo 1. 监控会实时显示识别结果
    echo 2. 按 Ctrl+C 退出监控
    echo.
    echo 正在启动...
    python monitor_output.py
    pause
    goto menu
)

if "%choice%"=="4" (
    cls
    echo ========================================
    echo          当前识别结果
    echo ========================================
    echo.
    echo [最新识别结果]
    echo ----------------------------------------
    if exist "outputs\current_product.txt" (
        type "outputs\current_product.txt"
    ) else (
        echo (暂无识别记录)
        echo.
        echo 说明: 运行识别程序后，这里会显示最新的识别结果
    )
    echo ----------------------------------------
    echo.
    pause
    goto menu
)

if "%choice%"=="5" (
    cls
    echo ========================================
    echo          查看所有日志文件
    echo ========================================
    echo.
    echo [系统日志]
    echo ----------------------------------------
    if exist "outputs\system_log.txt" (
        echo 最后10行日志:
        python -c "with open('outputs/system_log.txt', 'r', encoding='utf-8') as f: lines = f.readlines(); print(''.join(lines[-10:]))" 2>nul
        if errorlevel 1 (
            echo 无法读取日志文件，可能是编码问题
        )
    ) else (
        echo (暂无系统日志)
    )
    
    echo.
    echo [识别日志]
    echo ----------------------------------------
    if exist "outputs\recognition_log.txt" (
        echo 最后10行日志:
        python -c "with open('outputs/recognition_log.txt', 'r', encoding='utf-8') as f: lines = f.readlines(); print(''.join(lines[-10:]))" 2>nul
        if errorlevel 1 (
            echo 无法读取日志文件，可能是编码问题
        )
    ) else (
        echo (暂无识别日志)
    )
    
    echo.
    echo [学习日志]
    echo ----------------------------------------
    if exist "outputs\learning_log.txt" (
        echo 最后10行日志:
        python -c "with open('outputs/learning_log.txt', 'r', encoding='utf-8') as f: lines = f.readlines(); print(''.join(lines[-10:]))" 2>nul
        if errorlevel 1 (
            echo 无法读取日志文件，可能是编码问题
        )
    ) else (
        echo (暂无学习日志)
    )
    echo ----------------------------------------
    echo.
    pause
    goto menu
)

if "%choice%"=="6" (
    cls
    echo ========================================
    echo          运行系统测试
    echo ========================================
    echo.
    echo 正在运行系统测试...
    python -c "import sys; sys.path.append('.'); from output_manager import get_output_manager; mgr = get_output_manager(); mgr.log_system('Test', '开始系统测试'); mgr.update_current_product('测试商品', 0.95, '系统测试中'); mgr.log_recognition('测试商品', 0.95); mgr.log_learning('测试商品', '测试学习', '系统测试'); mgr.log_system('Test', '系统测试完成'); print('正确 系统测试完成'); print('  已生成测试日志，请查看输出目录')"
    echo.
    pause
    goto menu
)

if "%choice%"=="7" (
    cls
    echo ========================================
    echo          清空所有日志
    echo ========================================
    echo.
    set /p confirm="确认清空所有日志? (y/n): "
    if /i "%confirm%"=="y" (
        python -c "import sys; sys.path.append('.'); from output_manager import get_output_manager; mgr = get_output_manager(); result = mgr.clear_logs('all'); print('正确 所有日志已清空')"
    )
    echo.
    pause
    goto menu
)

if "%choice%"=="8" (
    cls
    echo ========================================
    echo          打开输出目录
    echo ========================================
    echo.
    echo 正在打开输出目录...
    if exist "outputs" (
        explorer "%~dp0outputs"
        echo 正确 输出目录已打开
    ) else (
        echo 错误 输出目录不存在，请先运行一次程序
    )
    echo.
    pause
    goto menu
)

if "%choice%"=="9" (
    cls
    echo ========================================
    echo           感谢使用
    echo       直播商品识别系统 4.1
    echo ========================================
    echo.
    echo 再见!
    timeout /t 2 >nul
    exit /b 0
)

echo.
echo [错误] 无效选项: %choice%
echo 请按任意键返回菜单...
pause >nul
goto menu