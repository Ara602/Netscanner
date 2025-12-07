#!/bin/bash
echo "正在构建网络主机扫描软件..."
echo

# 安装依赖
pip install -r requirements.txt

# 创建可执行文件
echo "正在打包为可执行文件..."
pip install pyinstaller

# 打包主程序
pyinstaller --onefile --name="网络主机扫描软件" \
  --add-data="src:src" \
  main.py

echo
echo "构建完成！"
echo "可执行文件位于: dist/网络主机扫描软件"