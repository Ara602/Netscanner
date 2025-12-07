# 网络主机扫描软件包
# 作者：张夏灵
# 班级：网云2302
# 学号：542307280233

__version__ = "1.0.0"
__author__ = "张夏灵"
__email__ = "zhangxialing@example.com"

# 导出主要类
from .scanner import NetworkScanner, HostInfo
from .gui import ScannerGUI
from .cli import main as cli_main

__all__ = ['NetworkScanner', 'HostInfo', 'ScannerGUI', 'cli_main']