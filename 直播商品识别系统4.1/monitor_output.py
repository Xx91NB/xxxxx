#!/usr/bin/env python3
"""
输出监控脚本
实时监控系统输出文件
"""
import time
import os
from pathlib import Path
from output_manager import get_output_manager
import threading

class OutputMonitor:
    def __init__(self):
        """初始化输出监控器"""
        self.output_mgr = get_output_manager()
        self.monitoring = False
        self.last_contents = {}
        
    def start_monitoring(self, interval=2):
        """
        开始监控输出文件
        
        参数:
            interval: 检查间隔(秒)
        """
        self.monitoring = True
        print("开始监控输出文件...")
        print("按 Ctrl+C 停止监控")
        print()
        
        # 初始化上次内容
        for name, file_path in self.output_mgr.output_files.items():
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.last_contents[name] = f.read()
        
        try:
            while self.monitoring:
                self.check_updates()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n监控已停止")
        finally:
            self.monitoring = False
    
    def check_updates(self):
        """检查文件更新"""
        updates = []
        
        for name, file_path in self.output_mgr.output_files.items():
            if not file_path.exists():
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            if name not in self.last_contents or self.last_contents[name] != current_content:
                updates.append(name)
                self.last_contents[name] = current_content
        
        if updates:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] 检测到更新: {', '.join(updates)}")
            
            # 显示重要文件内容
            if 'current_product' in updates:
                self.display_current_product()
    
    def display_current_product(self):
        """显示当前商品"""
        product_info = self.output_mgr.get_current_product()
        
        if "当前识别商品:" in product_info:
            # 提取商品名
            lines = product_info.split('\n')
            for line in lines:
                if line.startswith('当前识别商品:'):
                    product_line = line
                    break
            else:
                product_line = lines[0]
            
            print(f"  当前商品: {product_line}")
    
    def realtime_display(self):
        """实时显示输出内容"""
        print("实时输出监控")
        print("=" * 60)
        
        def display_loop():
            last_product = ""
            
            while self.monitoring:
                # 读取当前商品文件
                current_product = self.output_mgr.get_current_product()
                
                if current_product != last_product:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("实时输出监控")
                    print("=" * 60)
                    print("\n📦 当前识别商品:")
                    print("-" * 40)
                    print(current_product)
                    print("-" * 40)
                    
                    # 显示最近识别记录
                    print("\n📋 最近识别记录:")
                    print("-" * 40)
                    recent = self.output_mgr.get_recent_recognitions(5)
                    for line in recent[-5:]:
                        print(line.strip())
                    print("-" * 40)
                    
                    # 显示学习摘要
                    print("\n📊 学习统计:")
                    print("-" * 40)
                    summary = self.output_mgr.get_learning_summary()
                    print(f"总学习次数: {summary['total_learned']}")
                    print(f"自动学习: {summary['auto_learned']}")
                    print(f"手动学习: {summary['manual_learned']}")
                    print(f"最后学习: {summary['last_learning'].strip() if '无学习记录' not in summary['last_learning'] else '无'}")
                    print("-" * 40)
                    
                    last_product = current_product
                
                time.sleep(1)
        
        self.monitoring = True
        display_thread = threading.Thread(target=display_loop)
        display_thread.daemon = True
        display_thread.start()
        
        input("\n按Enter键停止监控...\n")
        self.monitoring = False
    
    def show_file_contents(self, file_type="current_product"):
        """
        显示文件内容
        
        参数:
            file_type: 文件类型
        """
        if file_type in self.output_mgr.output_files:
            file_path = self.output_mgr.output_files[file_type]
            
            if file_path.exists():
                print(f"\n{file_type.replace('_', ' ').title()} 内容:")
                print("=" * 60)
                with open(file_path, 'r', encoding='utf-8') as f:
                    print(f.read())
                print("=" * 60)
            else:
                print(f"文件不存在: {file_path}")
        else:
            print(f"未知的文件类型: {file_type}")

def main():
    """主函数"""
    monitor = OutputMonitor()
    
    print("输出文件监控系统")
    print("=" * 60)
    
    while True:
        print("\n请选择监控模式:")
        print("1. 实时显示模式 (推荐)")
        print("2. 更新提醒模式")
        print("3. 查看特定文件")
        print("4. 清空所有日志")
        print("5. 退出")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == "1":
            monitor.realtime_display()
        elif choice == "2":
            interval = input("请输入检查间隔(秒，默认2): ").strip()
            interval = int(interval) if interval.isdigit() else 2
            monitor.start_monitoring(interval)
        elif choice == "3":
            print("\n选择要查看的文件:")
            print("1. current_product.txt - 当前商品")
            print("2. recognition_log.txt - 识别日志")
            print("3. learning_log.txt - 学习日志")
            print("4. system_log.txt - 系统日志")
            print("5. statistics.txt - 统计信息")
            
            file_choice = input("\n请输入选项 (1-5): ").strip()
            file_map = {
                '1': 'current_product',
                '2': 'recognition_log',
                '3': 'learning_log',
                '4': 'system_log',
                '5': 'statistics'
            }
            
            if file_choice in file_map:
                monitor.show_file_contents(file_map[file_choice])
            else:
                print("无效选项")
        elif choice == "4":
            confirm = input("确认清空所有日志? (y/n): ").lower()
            if confirm == 'y':
                get_output_manager().clear_logs("all")
                print("所有日志已清空")
        elif choice == "5":
            print("再见！")
            break
        else:
            print("无效选项")

if __name__ == "__main__":
    main()