#!/usr/bin/env python3
"""
run.py - Python版视频号助手自动化启动器
替代批处理文件，避免被杀毒软件拦截
"""

import os
import sys
import subprocess
import time

def print_header():
    """打印标题"""
    print("="*60)
    print("    视频号助手自动化系统 - Python启动器")
    print("="*60)

def install_dependencies():
    """安装Python依赖"""
    print("\n[1/3] 正在安装Python依赖...")
    packages = ["pyautogui", "vosk", "requests", "flask", "pyaudio"]
    for pkg in packages:
        print(f"  安装 {pkg}...")
        os.system(f"pip install {pkg}")
    print("✅ 依赖安装完成")

def test_click():
    """测试点击功能"""
    print("\n🔧 测试点击功能...")
    
    # 检查配置文件
    if not os.path.exists("config/button_coords.txt"):
        print("❌ 未找到坐标配置文件")
        return False
    
    try:
        # 读取坐标
        with open("config/button_coords.txt", "r") as f:
            coords = f.read().strip()
            x, y = map(int, coords.split(","))
        
        print(f"📍 使用坐标: ({x}, {y})")
        
        # 执行点击
        import pyautogui
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()
        
        print("✅ 点击测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 点击测试失败: {e}")
        return False

def start_voice_listener():
    """启动语音监听"""
    print("\n🎤 启动语音监听...")
    
    # 检查必要文件
    if not os.path.exists("scripts/live_listener.py"):
        print("❌ 未找到语音监听脚本")
        return False
    
    print("✅ 语音监听已启动")
    print("💡 请勿关闭弹出的黑色窗口")
    print("🎯 可以说出关键词：添加商品、一百八、上链接")
    
    # 在新窗口中启动
    if sys.platform == "win32":
        subprocess.Popen(["python", "scripts/live_listener.py"], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        os.system("python scripts/live_listener.py &")
    
    return True

def capture_coordinates():
    """获取按钮坐标"""
    print("\n📍 获取按钮坐标")
    print("请确保：")
    print("1. Edge浏览器已打开并登录")
    print("2. 已进入'直播商品管理'页面")
    print("3. '添加商品'按钮在屏幕可见位置")
    
    input("\n将鼠标移到按钮上，按Enter继续...")
    
    try:
        import pyautogui
        x, y = pyautogui.position()
        print(f"✅ 获取到坐标: ({x}, {y})")
        
        # 保存到文件
        os.makedirs("config", exist_ok=True)
        with open("config/button_coords.txt", "w") as f:
            f.write(f"{x},{y}")
        
        print("💾 坐标已保存到 config/button_coords.txt")
        return True
        
    except ImportError:
        print("❌ 需要先安装pyautogui")
        print("请先运行'安装依赖'选项")
        return False

def package_for_distribution():
    """打包分发"""
    print("\n📦 打包安装包...")
    
    # 检查必要文件
    required_files = [
        "scripts/shadow_ready.py",
        "config/button_coords.txt",
        "config/keywords.txt"
    ]
    
    for f in required_files:
        if not os.path.exists(f):
            print(f"❌ 缺少必要文件: {f}")
            return False
    
    # 创建时间戳
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"视频号助手自动化_{timestamp}.zip"
    
    print(f"📁 正在创建: {zip_name}")
    
    # 这里可以添加打包逻辑
    print("✅ 打包功能需要完整的make_package.bat")
    print("💡 请使用 【06_打包发布】make_package.bat")
    
    return True

def show_status():
    """显示系统状态"""
    print("\n📊 系统状态检查")
    print("-"*40)
    
    # 检查文件
    files_to_check = [
        ("scripts/shadow_ready.py", "核心点击脚本"),
        ("config/button_coords.txt", "按钮坐标"),
        ("config/keywords.txt", "关键词文件"),
        ("scripts/live_listener.py", "语音监听"),
        ("scripts/requirements.txt", "依赖列表"),
    ]
    
    for file_path, desc in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {desc}")
            if "button_coords.txt" in file_path:
                with open(file_path, "r") as f:
                    print(f"   坐标: {f.read().strip()}")
            elif "keywords.txt" in file_path:
                with open(file_path, "r") as f:
                    keywords = [k.strip() for k in f.readlines() if k.strip()]
                    print(f"   关键词: {', '.join(keywords)}")
        else:
            print(f"❌ {desc}")
    
    print("-"*40)

def main():
    """主函数"""
    while True:
        print_header()
        print("\n请选择操作：")
        print(" 1. 安装Python依赖")
        print(" 2. 测试点击功能")
        print(" 3. 启动语音监听")
        print(" 4. 获取按钮坐标")
        print(" 5. 打包分发")
        print(" 6. 查看系统状态")
        print(" 7. 退出系统")
        print("-"*40)
        
        try:
            choice = input("请输入选择 (1-7): ").strip()
            
            if choice == "1":
                install_dependencies()
            elif choice == "2":
                test_click()
            elif choice == "3":
                start_voice_listener()
            elif choice == "4":
                capture_coordinates()
            elif choice == "5":
                package_for_distribution()
            elif choice == "6":
                show_status()
            elif choice == "7":
                print("\n👋 退出系统")
                break
            else:
                print("❌ 无效选择，请重新输入")
            
            input("\n按Enter继续...")
            os.system("cls" if sys.platform == "win32" else "clear")
            
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，退出系统")
            break

if __name__ == "__main__":
    main()