@echo off
chcp 65001
echo 网络主机扫描软件 - 发布脚本
echo ========================================
echo.

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请安装Python 3.8+
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist ".venv" (
    echo 创建虚拟环境...
    python -m venv .venv
)

:: 激活虚拟环境
echo 激活虚拟环境...
call .venv\Scripts\activate

:: 安装依赖
echo 安装依赖...
pip install -r requirements.txt
pip install pyinstaller
pip install pyinstaller-hooks-contrib

:: 运行打包工具
echo 启动打包工具...
python build.py

echo.
echo ========================================
echo 打包完成！
echo.
echo 生成的发布文件在 dist/ 目录下
echo 可以直接发送 网络主机扫描器.exe 给其他人使用
echo.
pause