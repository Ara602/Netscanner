#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序入口 - 打包优化版
作者：张夏灵
班级：网云2302
学号：542307280233
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def resource_path(relative_path):
    """获取资源文件的绝对路径（用于PyInstaller打包）"""
    try:
        # PyInstaller创建的临时文件夹
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def check_dependencies():
    """检查必要的依赖"""
    missing_deps = []
    
    # 检查tkinter（GUI必需）
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    # 检查pandas（Excel导出需要，但不是必需的）
    try:
        import pandas
    except ImportError:
        pass  # pandas不是必需的
    
    if missing_deps:
        messagebox.showerror(
            "缺少依赖",
            f"缺少必要的依赖包:\n{', '.join(missing_deps)}\n\n"
            f"请运行: pip install -r requirements.txt"
        )
        return False
    return True

def run_gui():
    """运行图形界面"""
    try:
        # 添加src目录到Python路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(current_dir, 'src')
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        
        from src.gui import ScannerGUI
        app = ScannerGUI()
        app.run()
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保所有依赖已安装")
        print("运行: pip install -r requirements.txt")
        input("按Enter键退出...")
    except Exception as e:
        print(f"运行GUI时出错: {e}")
        input("按Enter键退出...")

def run_cli():
    """运行命令行界面"""
    try:
        # 添加src目录到Python路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(current_dir, 'src')
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        
        from src.cli import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"导入CLI模块失败: {e}")
        input("按Enter键退出...")
    except Exception as e:
        print(f"运行CLI时出错: {e}")
        input("按Enter键退出...")

def show_about():
    """显示关于信息"""
    about_text = """
网络主机扫描软件 v1.0

功能特点:
• 扫描局域网内主机存活状态
• 支持多种目标格式(IP/IP范围/CIDR)
• 多线程并发扫描
• 图形化界面和命令行界面
• 结果导出(CSV/JSON/TXT/Excel)

作者: 张夏灵
班级: 网云2302
学号: 542307280233

使用说明:
1. 图形界面: 双击运行程序或运行 python main.py gui
2. 命令行: python main.py cli [目标] [选项]
3. 示例: python main.py cli 192.168.1.1-254 -t 100
    """
    print(about_text)

def main_menu():
    """显示主菜单"""
    print("网络主机存活扫描软件 v1.0")
    print("作者：张夏灵 | 班级：网云2302 | 学号：542307280233")
    print("=" * 50)
    
    while True:
        print("\n请选择模式:")
        print("1. 图形界面模式 (推荐)")
        print("2. 命令行模式")
        print("3. 查看软件信息")
        print("4. 退出程序")
        
        try:
            choice = input("请输入选择 (1-4): ").strip()
            
            if choice == '1':
                if not check_dependencies():
                    continue
                run_gui()
                break  # GUI退出后不再显示菜单
                
            elif choice == '2':
                # 获取命令行参数
                target = input("请输入扫描目标 (如: 192.168.1.1-254): ").strip()
                if not target:
                    print("未输入目标，使用默认值: 192.168.1.1-254")
                    target = "192.168.1.1-254"
                
                threads = input("线程数 (默认100): ").strip()
                threads = int(threads) if threads.isdigit() else 100
                
                timeout = input("超时时间秒 (默认2): ").strip()
                timeout = int(timeout) if timeout.isdigit() else 2
                
                # 模拟命令行参数
                sys.argv = ['main.py', target, '-t', str(threads), '--timeout', str(timeout)]
                run_cli()
                
            elif choice == '3':
                show_about()
                
            elif choice == '4':
                print("感谢使用，再见！")
                sys.exit(0)
                
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n程序被用户中断")
            sys.exit(0)
        except Exception as e:
            print(f"发生错误: {e}")
            input("按Enter键继续...")

def main():
    """主函数 - 根据参数选择运行模式"""
    
    # 检查是否被打包
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        print("正在启动网络主机扫描软件...")
    
    # 处理命令行参数
    if len(sys.argv) == 1:
        # 如果是打包后的程序（且无控制台），直接启动GUI
        if is_frozen:
            if not check_dependencies():
                return
            run_gui()
        else:
            # 开发环境或有控制台时 - 显示主菜单
            main_menu()
    
    elif len(sys.argv) == 2 and sys.argv[1] in ['gui', '--gui', '-g']:
        # 直接启动GUI模式
        if not check_dependencies():
            return
        run_gui()
    
    elif len(sys.argv) == 2 and sys.argv[1] in ['cli', '--cli', '-c']:
        # CLI模式但没有目标 - 提示
        print("命令行模式需要指定扫描目标")
        print("示例: python main.py cli 192.168.1.1-254")
        print("       python main.py cli 192.168.1.0/24 -t 100 --timeout 2")
        print("\n输入目标:")
        target = input("> ").strip()
        if target:
            sys.argv = ['main.py', target]
            run_cli()
        else:
            print("未输入目标，退出...")
    
    elif len(sys.argv) >= 2 and sys.argv[1] in ['help', '--help', '-h']:
        # 显示帮助
        show_help()
    
    elif len(sys.argv) >= 2 and sys.argv[1] in ['version', '--version', '-v']:
        # 显示版本
        print("网络主机扫描软件 v1.0")
        print("作者：张夏灵 | 班级：网云2302 | 学号：542307280233")
    
    elif len(sys.argv) >= 2:
        # 直接运行CLI模式
        # 确保第一个参数是目标（不是cli）
        if sys.argv[1] == 'cli':
            sys.argv.pop(1)  # 移除'cli'
        run_cli()
    
    else:
        print("用法:")
        print("  直接运行: python main.py")
        print("  GUI模式: python main.py gui")
        print("  CLI模式: python main.py cli [目标] [选项]")
        print("\n示例:")
        print("  python main.py gui")
        print("  python main.py cli 192.168.1.1-254")
        print("  python main.py cli 192.168.1.0/24 -t 100 --timeout 2 -o result.csv")

def show_help():
    """显示帮助信息"""
    help_text = """
网络主机扫描软件 - 使用帮助

命令格式:
  python main.py [模式] [目标] [选项]

模式:
  gui        启动图形界面
  cli        启动命令行界面
  help       显示此帮助信息
  version    显示版本信息

目标格式:
  单个IP: 192.168.1.1
  IP范围: 192.168.1.1-100
  网段: 192.168.1.0/24

CLI模式选项:
  -t, --threads NUM    线程数 (默认: 100)
  --timeout SEC        超时时间秒 (默认: 2)
  -o, --output FILE    输出文件名
  --format FORMAT      输出格式: csv, json, txt, excel (默认: txt)

示例:
  python main.py                     # 显示主菜单
  python main.py gui                 # 直接启动GUI
  python main.py cli 192.168.1.1     # 扫描单个IP
  python main.py cli 192.168.1.1-254 -t 200 --timeout 3
  python main.py cli 192.168.1.0/24 -o results.csv --format csv

图形界面:
  双击运行程序或在菜单中选择图形界面模式
  支持实时进度显示和结果导出

注意:
  1. 获取MAC地址需要管理员/root权限
  2. 扫描大量IP时可能被防火墙拦截
  3. Excel导出需要安装pandas库
    """
    print(help_text)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行出错: {e}")
        print("\n请检查:")
        print("  1. 是否安装了所有依赖 (pip install -r requirements.txt)")
        print("  2. 是否有正确的权限")
        print("  3. 网络是否正常")
        input("按Enter键退出...")
        sys.exit(1)