@echo off
chcp 65001 > nul
echo ========================================================
echo   Button Coordinate Getter Tool
echo ========================================================
echo.
echo 📋 Instructions:
echo 1. Make sure WeChat video page is open
echo 2. "Add Product" button is visible on screen
echo.
echo ⚠️ Note: Move mouse to the button, coordinates auto-captured
echo.
set /p ready="Ready to start? (Y/N): "

if /i "%ready%" NEQ "Y" (
    echo Operation cancelled.
    pause
    exit /b
)

echo.
echo 📍 Getting mouse position...
echo Move mouse to the "Add Product" button
echo Waiting 3 seconds...
timeout /t 3 /nobreak > nul

echo Getting coordinates...
python -c "import pyautogui; import time; time.sleep(0.5); x, y = pyautogui.position(); print(f'Mouse Position: X={x}, Y={y}'); open('config/button_coords.txt', 'w').write(f'{x},{y}')"

echo.
echo ✅ Coordinates saved to: config\button_coords.txt
echo 📝 Content: 
type config\button_coords.txt
echo.
pause