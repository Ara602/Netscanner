#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本
作者：张夏灵
班级：网云2302
学号：542307280233
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_windows():
    """Windows平台打包"""
    print("正在打包Windows版本...")
    
    # 清理之前的打包文件
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # PyInstaller命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=网络主机扫描器',
        '--windowed',  # 无控制台窗口
        '--icon=icon.ico',  # 如果图标存在
        '--add-data=src;src',  # 包含src目录
        '--add-data=requirements.txt;.',  # 包含依赖文件
        '--add-data=README.md;.',  # 包含说明文件
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--clean',  # 清理缓存
        '--onefile',  # 打包成单个文件
        '--noconsole',  # 无控制台（GUI程序）
        '--uac-admin',  # 请求管理员权限（获取MAC地址需要）
        'main.py'
    ]
    
    # 执行打包命令
    subprocess.run(cmd, check=True)
    
    print("打包完成！")
    print(f"可执行文件在: {os.path.abspath('dist/网络主机扫描器.exe')}")

def build_linux():
    """Linux平台打包"""
    print("正在打包Linux版本...")
    
    # 清理之前的打包文件
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # PyInstaller命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=network-scanner',
        '--add-data=src:src',  # Linux使用冒号
        '--add-data=requirements.txt:.',
        '--add-data=README.md:.',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=tkinter',
        '--clean',
        '--onefile',
        'main.py'
    ]
    
    subprocess.run(cmd, check=True)
    
    print("打包完成！")
    print(f"可执行文件在: {os.path.abspath('dist/network-scanner')}")

def create_simple_launcher():
    """创建简单的启动器"""
    print("创建启动器...")
    
    # 创建批处理启动器 (Windows)
    bat_content = '''@echo off
echo 网络主机扫描软件 v1.0
echo 作者：张夏灵 | 班级：网云2302 | 学号：542307280233
echo.
echo 正在启动程序...
python main.py gui
pause
'''
    
    with open('启动软件.bat', 'w', encoding='gbk') as f:
        f.write(bat_content)
    
    # 创建Shell启动器 (Linux/Mac)
    sh_content = '''#!/bin/bash
echo "网络主机扫描软件 v1.0"
echo "作者：张夏灵 | 班级：网云2302 | 学号：542307280233"
echo ""
echo "正在启动程序..."
python3 main.py gui
'''
    
    with open('start.sh', 'w', encoding='utf-8') as f:
        f.write(sh_content)
    
    # 给Shell脚本添加执行权限
    if os.name != 'nt':  # 不是Windows系统
        os.chmod('start.sh', 0o755)
    
    print("启动器创建完成！")

def main():
    print("=" * 60)
    print("网络主机扫描软件 - 打包工具")
    print("作者：张夏灵 | 班级：网云2302 | 学号：542307280233")
    print("=" * 60)
    
    while True:
        print("\n请选择打包选项:")
        print("1. Windows版 (生成.exe)")
        print("2. Linux版 (生成可执行文件)")
        print("3. 创建简易启动器")
        print("4. 完整打包 (Windows)")
        print("5. 退出")
        
        choice = input("请输入选择 (1-5): ").strip()
        
        if choice == '1':
            build_windows()
        elif choice == '2':
            build_linux()
        elif choice == '3':
            create_simple_launcher()
        elif choice == '4':
            print("开始完整打包流程...")
            # 1. 创建图标（如果不存在）
            if not os.path.exists('icon.ico'):
                create_dummy_icon()
            # 2. 创建启动器
            create_simple_launcher()
            # 3. 打包
            build_windows()
            print("\n完整打包完成！")
            print("已生成:")
            print("  - dist/网络主机扫描器.exe (主程序)")
            print("  - 启动软件.bat (启动器)")
            print("  - README.md (说明文档)")
            print("  - requirements.txt (依赖列表)")
        elif choice == '5':
            print("退出打包工具")
            break
        else:
            print("无效选择，请重新输入")

def create_dummy_icon():
    """创建虚拟图标文件（如果需要）"""
    try:
        from PIL import Image, ImageDraw
        # 创建一个简单的图标
        img = Image.new('RGB', (256, 256), color=(70, 130, 180))  # 钢蓝色
        draw = ImageDraw.Draw(img)
        draw.text((100, 100), "NS", fill=(255, 255, 255))  # NS = Network Scanner
        img.save('icon.ico', format='ICO')
        print("已创建默认图标: icon.ico")
    except ImportError:
        # 如果没有PIL，创建空文件
        with open('icon.ico', 'wb') as f:
            pass
        print("已创建空图标文件，建议手动添加图标")

if __name__ == "__main__":
    main()