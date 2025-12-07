#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有测试
"""

import sys
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, 'src')

# 添加src目录到路径
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

print("=" * 60)
print("网络主机扫描软件 - 测试套件")
print("作者：张夏灵 | 班级：网云2302 | 学号：542307280233")
print("=" * 60)

# 1. 测试导入
print("\n1. 测试模块导入...")
try:
    from src.scanner import NetworkScanner, HostInfo
    print("✓ 成功导入 NetworkScanner")
    print("✓ 成功导入 HostInfo")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 2. 创建测试目录
test_dir = os.path.join(project_root, 'tests')
if not os.path.exists(test_dir):
    os.makedirs(test_dir)

# 3. 创建测试文件
test_file = os.path.join(test_dir, 'test_scanner.py')
if not os.path.exists(test_file):
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试扫描器模块
"""

import unittest
from src.scanner import NetworkScanner, HostInfo

class TestScanner(unittest.TestCase):
    def test_hostinfo_creation(self):
        host = HostInfo(ip='192.168.1.1', status='在线')
        self.assertEqual(host.ip, '192.168.1.1')
        self.assertEqual(host.status, '在线')
    
    def test_scanner_initialization(self):
        scanner = NetworkScanner(max_threads=50, timeout=3)
        self.assertEqual(scanner.max_threads, 50)
        self.assertEqual(scanner.timeout, 3)
    
    def test_scan_localhost(self):
        scanner = NetworkScanner()
        result = scanner.scan_single('127.0.0.1')
        self.assertEqual(result.ip, '127.0.0.1')
        self.assertIn(result.status, ['在线', '离线'])

if __name__ == '__main__':
    unittest.main()
''')

# 4. 运行测试
print("\n2. 运行单元测试...")
import unittest

# 加载并运行测试
loader = unittest.TestLoader()
suite = loader.discover(test_dir, pattern='test_*.py')

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# 5. 测试基本功能
print("\n3. 测试基本功能...")
try:
    scanner = NetworkScanner()
    result = scanner.scan_single("127.0.0.1")
    print(f"✓ 扫描本地主机成功: {result.ip} - {result.status}")
except Exception as e:
    print(f"✗ 扫描测试失败: {e}")

# 6. 测试GUI导入
print("\n4. 测试GUI模块导入...")
try:
    from src.gui import ScannerGUI
    print("✓ 成功导入 ScannerGUI")
except ImportError as e:
    print(f"✗ GUI导入失败: {e}")

# 7. 测试CLI导入
print("\n5. 测试CLI模块导入...")
try:
    from src.cli import main as cli_main
    print("✓ 成功导入 CLI模块")
except ImportError as e:
    print(f"✗ CLI导入失败: {e}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)