@echo off
chcp 65001 > nul
title 直播商品识别系统 4.1

echo.
echo ========================================
echo        直播商品识别系统 4.1
echo ========================================
echo.

:: 设置工作目录
cd /d "%~dp0"

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    echo.
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查并安装依赖
echo 检查Python依赖...
python -c "import cv2, numpy, yaml" 2>nul
if errorlevel 1 (
    echo 正在安装依赖包，请稍候...
    pip install opencv-python opencv-contrib-python numpy pyyaml pillow mss pyautogui
) else (
    echo 依赖包已安装
)

:: 创建必要的目录
if not exist "data" mkdir data
if not exist "data\images_material" mkdir data\images_material
if not exist "data\videos_material" mkdir data\videos_material
if not exist "outputs" mkdir outputs
if not exist "config" mkdir config

:: 显示菜单
:menu
cls
echo ========================================
echo           请选择启动方式
echo ========================================
echo.
echo  1. 快速启动 (推荐)
echo  2. 系统测试
echo  3. 实时检测演示
echo  4. 图像匹配测试
echo  5. 素材管理
echo  6. 关于系统
echo  7. 退出
echo.
set /p choice="请输入选项 (1-7): "

if "%choice%"=="1" (
    echo 快速启动...
    python quick_start.py
    pause
    goto menu
)

if "%choice%"=="2" (
    echo 运行系统测试...
    python test_all.py
    pause
    goto menu
)

if "%choice%"=="3" (
    echo 启动实时检测演示...
    python -c "
import cv2
import time

print('打开摄像头...')
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print('无法打开摄像头')
    exit()

print('摄像头已打开，按 q 键退出')

frame_count = 0
start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # 计算FPS
    elapsed = time.time() - start_time
    fps = frame_count / elapsed if elapsed > 0 else 0
    
    # 绘制界面
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (0, 255, 0), 2)
    cv2.putText(frame, '实时检测演示', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f'FPS: {fps:.1f}', (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, '按 q 退出', (10, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    cv2.imshow('实时检测演示 - 按 q 退出', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f'演示结束，共处理 {frame_count} 帧')
"
    pause
    goto menu
)

if "%choice%"=="4" (
    echo 启动图像匹配测试...
    python -c "
try:
    from image_matcher import ImageMatcher
    import cv2
    import numpy as np
    
    print('创建图像匹配器...')
    matcher = ImageMatcher()
    
    print('创建测试图像...')
    test_img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.rectangle(test_img, (100, 100), (200, 200), (255, 0, 0), -1)
    cv2.putText(test_img, '测试商品', (110, 150), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    print('添加模板...')
    matcher.add_template('test_product', test_img)
    
    print('进行匹配...')
    matches = matcher.match(test_img)
    
    if matches:
        print(f'找到匹配: {matches[0][\"template_name\"]}')
        result_img = matcher.draw_matches(test_img, matches[0])
        cv2.imshow('匹配结果', result_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print('没有找到匹配')
    
    print('图像匹配测试完成')
    
except Exception as e:
    print(f'测试失败: {e}')
"
    pause
    goto menu
)

if "%choice%"=="5" (
    echo 素材管理...
    python -c "
from pathlib import Path

print('素材目录检查:')
dirs = [
    ('图像素材', 'data/images_material'),
    ('视频素材', 'data/videos_material'),
    ('输出目录', 'outputs'),
    ('配置目录', 'config')
]

for name, path in dirs:
    p = Path(path)
    if p.exists():
        files = list(p.glob('*.*'))
        print(f'  {name}: {len(files)} 个文件')
    else:
        print(f'  {name}: 目录不存在')
        p.mkdir(parents=True, exist_ok=True)
        print(f'   已创建目录')

print('检查完成')
"
    pause
    goto menu
)

if "%choice%"=="6" (
    cls
    echo.
    echo 直播商品识别系统 4.1
    echo ====================
    echo.
    echo 功能特性:
    echo   1. 实时商品检测
    echo   2. 图像特征匹配
    echo   3. 视频流处理
    echo   4. 智能学习功能
    echo.
    echo 系统要求:
    echo   - Python 3.8+
    echo   - 摄像头或视频文件
    echo   - 2GB以上内存
    echo.
    echo 使用方法:
    echo   1. 首次运行建议先进行系统测试
    echo   2. 将商品图片放入 data/images_material/
    echo   3. 选择相应模式运行
    echo.
    pause
    goto menu
)

if "%choice%"=="7" (
    echo 再见!
    timeout /t 1 >nul
    exit /b 0
)

echo 无效选项，请重新输入
timeout /t 2 >nul
goto menu