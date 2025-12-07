#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序入口
作者：张夏灵
班级：网云2302
学号：542307280233
"""

import sys
import os

def main():
    """主函数"""
    print("网络主机存活扫描软件 v1.0")
    print("作者：张夏灵 | 班级：网云2302 | 学号：542307280233")
    print("=" * 50)
    
    # 添加src目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    while True:
        print("\n请选择模式:")
        print("1. 图形界面模式")
        print("2. 命令行模式")
        print("3. 退出")
        
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == '1':
            # 启动图形界面
            try:
                from src.gui import ScannerGUI
                app = ScannerGUI()
                app.run()
            except ImportError as e:
                print(f"导入模块失败: {e}")
                print("请确保所有依赖已安装")
                
        elif choice == '2':
            # 命令行模式
            try:
                from src.cli import main as cli_main
                
                # 简单解析参数
                if len(sys.argv) > 1:
                    cli_main()
                else:
                    print("请在命令行中使用: python main.py cli [参数]")
                    print("或运行: python -m src.cli [参数]")
            except ImportError as e:
                print(f"导入CLI模块失败: {e}")
                
        elif choice == '3':
            print("感谢使用，再见！")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    # 如果没有参数，显示主菜单
    if len(sys.argv) == 1:
        main()
    elif sys.argv[1] == 'gui':
        # 直接启动GUI
        # 添加src目录到Python路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(current_dir, 'src')
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        
        try:
            from src.gui import ScannerGUI
            app = ScannerGUI()
            app.run()
        except ImportError as e:
            print(f"导入模块失败: {e}")
    elif sys.argv[1] == 'cli':
        # 移除第一个参数，然后运行CLI
        sys.argv.pop(0)
        
        # 添加src目录到Python路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(current_dir, 'src')
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        
        try:
            from src.cli import main
            main()
        except ImportError as e:
            print(f"导入模块失败: {e}")
    else:
        print("用法: python main.py [gui|cli]")
        print("  gui - 启动图形界面")
        print("  cli - 启动命令行界面")