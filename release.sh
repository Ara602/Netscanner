#!/bin/bash

echo "网络主机扫描软件 - 发布脚本"
echo "========================================"
echo

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请安装Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt
pip install pyinstaller
pip install pyinstaller-hooks-contrib

# 运行打包工具
echo "启动打包工具..."
python3 build.py

echo
echo "========================================"
echo "打包完成！"
echo
echo "生成的发布文件在 dist/ 目录下"
echo