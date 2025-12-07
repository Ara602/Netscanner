#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 更新版本
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scanner import NetworkScanner

class TestNetworkScanner(unittest.TestCase):
    """测试网络扫描器"""
    
    def setUp(self):
        self.scanner = NetworkScanner(max_threads=10, timeout=1)
    
    def test_parse_targets_single_ip(self):
        """测试单个IP解析"""
        targets = self.scanner._parse_targets("192.168.1.1")
        self.assertEqual(targets, ["192.168.1.1"])
    
    def test_parse_targets_ip_range(self):
        """测试IP范围解析"""
        targets = self.scanner._parse_targets("192.168.1.1-3")
        expected = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
        self.assertEqual(targets, expected)
    
    def test_parse_targets_cidr(self):
        """测试CIDR解析"""
        targets = self.scanner._parse_targets("192.168.1.0/30")
        expected = ["192.168.1.1", "192.168.1.2"]
        self.assertEqual(targets, expected)
    
    def test_ping_localhost(self):
        """测试ping本地回环地址"""
        is_online, response_time = self.scanner.ping_host("127.0.0.1")
        self.assertTrue(is_online)
        self.assertGreaterEqual(response_time, 0)
    
    def test_scan_single_localhost(self):
        """测试扫描本地回环地址"""
        result = self.scanner.scan_single("127.0.0.1")
        self.assertEqual(result.ip, "127.0.0.1")
        self.assertEqual(result.status, "在线")
        
        # 检查主机名是否为字符串类型
        self.assertIsInstance(result.hostname, str)
        
        # 检查响应时间是否为数字
        self.assertIsInstance(result.response_time, float)
        self.assertGreaterEqual(result.response_time, 0)
    
    def test_parse_targets_empty(self):
        """测试空输入"""
        targets = self.scanner._parse_targets("")
        self.assertEqual(targets, [])
    
    def test_parse_targets_invalid(self):
        """测试无效输入"""
        targets = self.scanner._parse_targets("invalid.input")
        self.assertEqual(targets, [])
    
    def test_scan_offline_host(self):
        """测试扫描一个离线的主机（一个不可能在线的地址）"""
        # 使用一个保留地址，如 192.0.2.1 (TEST-NET-1)
        result = self.scanner.scan_single("192.0.2.1")
        self.assertEqual(result.ip, "192.0.2.1")
        self.assertEqual(result.status, "离线")
        self.assertEqual(result.mac, "未知")
        self.assertEqual(result.response_time, 0.0)

if __name__ == '__main__':
    unittest.main()