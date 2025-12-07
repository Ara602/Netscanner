#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络主机扫描核心模块
作者：张夏灵
班级：网云2302
学号：542307280233
"""

import subprocess
import platform
import ipaddress
import threading
import queue
import time
import socket
import struct
import ctypes
import os
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Windows下需要特殊处理
if platform.system() == "Windows":
    import ctypes.wintypes

@dataclass
class HostInfo:
    """主机信息数据类"""
    ip: str
    status: str  # '在线' 或 '离线'
    mac: str = "未知"
    hostname: str = "未知"
    response_time: float = 0.0
    os_type: str = "未知"

class NetworkScanner:
    """网络扫描器主类"""
    
    def __init__(self, max_threads=100, timeout=2):
        """
        初始化扫描器
        
        Args:
            max_threads: 最大线程数
            timeout: 超时时间（秒）
        """
        self.max_threads = max_threads
        self.timeout = timeout
        self.results = []
        self.is_scanning = False
        self.scan_progress = 0
        self.total_targets = 0
        
    def _is_windows_admin(self) -> bool:
        """检查是否以管理员权限运行"""
        if platform.system() != "Windows":
            return os.geteuid() == 0
        
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def ping_host(self, ip: str) -> Tuple[bool, float]:
        """
        ICMP Ping扫描
        
        Args:
            ip: 目标IP地址
            
        Returns:
            (是否在线, 响应时间)
        """
        param = "-n" if platform.system().lower() == "windows" else "-c"
        timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
        
        # Windows使用毫秒，Linux/Unix使用秒
        timeout_value = str(int(self.timeout * 1000)) if platform.system().lower() == "windows" else str(self.timeout)
        
        command = ["ping", param, "1", timeout_param, timeout_value, ip]
        
        try:
            output = subprocess.run(command, capture_output=True, text=True, timeout=self.timeout + 1)
            
            # 根据操作系统解析输出
            if platform.system().lower() == "windows":
                if "TTL=" in output.stdout or "TTL " in output.stdout:
                    # 提取响应时间
                    time_match = re.search(r"时间[=<](\d+)ms", output.stdout)
                    if time_match:
                        response_time = float(time_match.group(1))
                    else:
                        response_time = 0.0
                    return True, response_time
            else:  # Linux/Mac
                if "1 packets transmitted, 1 received" in output.stdout:
                    # 提取响应时间
                    time_match = re.search(r"time=([\d.]+) ms", output.stdout)
                    if time_match:
                        response_time = float(time_match.group(1))
                    else:
                        response_time = 0.0
                    return True, response_time
                
        except (subprocess.TimeoutExpired, Exception):
            pass
            
        return False, 0.0
    
    def get_mac_address(self, ip: str) -> str:
        """
        获取MAC地址（仅限局域网）
        
        Args:
            ip: 目标IP地址
            
        Returns:
            MAC地址字符串
        """
        if platform.system() == "Windows":
            return self._get_mac_windows(ip)
        else:
            return self._get_mac_unix(ip)
    
    def _get_mac_windows(self, ip: str) -> str:
        """Windows系统获取MAC地址"""
        try:
            # 使用arp命令
            arp_command = ["arp", "-a", ip]
            output = subprocess.run(arp_command, capture_output=True, text=True, timeout=2)
            
            # 解析MAC地址
            mac_pattern = r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})"
            match = re.search(mac_pattern, output.stdout)
            if match:
                return match.group(0).replace("-", ":")
        except:
            pass
        return "未知"
    
    def _get_mac_unix(self, ip: str) -> str:
        """Unix/Linux系统获取MAC地址"""
        try:
            arp_command = ["arp", "-n", ip]
            output = subprocess.run(arp_command, capture_output=True, text=True, timeout=2)
            
            mac_pattern = r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}"
            match = re.search(mac_pattern, output.stdout)
            if match:
                return match.group(0)
        except:
            pass
        return "未知"
    
    def get_hostname(self, ip: str) -> str:
        """
        获取主机名
        
        Args:
            ip: 目标IP地址
            
        Returns:
            主机名
        """
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except:
            try:
                return socket.getfqdn(ip)
            except:
                return "未知"
    
    def _get_local_network(self) -> str:
        """获取本地网络地址"""
        try:
            # 创建一个临时socket来获取本地IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # 假设使用C类地址
            network = ".".join(local_ip.split(".")[:3]) + ".0/24"
            return network
        except:
            return "192.168.1.0/24"  # 默认网络
    
    def _parse_targets(self, target_input: str) -> List[str]:
        """
        解析目标输入
        
        Args:
            target_input: 可以是单个IP、IP范围、CIDR
            
        Returns:
            IP地址列表
        """
        targets = []
        
        try:
            # 单个IP
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target_input):
                targets.append(target_input)
            
            # IP范围 192.168.1.1-100
            elif '-' in target_input:
                base_ip, range_part = target_input.split('-')
                base_parts = base_ip.split('.')
                if len(base_parts) == 4 and range_part.isdigit():
                    start = int(base_parts[3])
                    end = int(range_part)
                    for i in range(start, end + 1):
                        targets.append(f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{i}")
            
            # CIDR格式 192.168.1.0/24
            elif '/' in target_input:
                network = ipaddress.ip_network(target_input, strict=False)
                for ip in network.hosts():
                    targets.append(str(ip))
            
            # IP列表文件
            elif target_input.endswith('.txt'):
                with open(target_input, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            targets.extend(self._parse_targets(line))
        except Exception as e:
            print(f"解析目标时出错: {e}")
            
        return targets
    
    def scan_single(self, ip: str) -> HostInfo:
        """扫描单个主机"""
        host_info = HostInfo(ip=ip, status='离线')
        
        try:
            # Ping扫描
            is_online, response_time = self.ping_host(ip)
            
            if is_online:
                host_info.status = '在线'
                host_info.response_time = response_time
                
                # 获取更多信息
                if self._is_windows_admin():
                    host_info.mac = self.get_mac_address(ip)
                host_info.hostname = self.get_hostname(ip)
                
                # 简单猜测操作系统类型
                if response_time > 0:
                    # 根据TTL值猜测（简化版）
                    pass
        except Exception as e:
            print(f"扫描 {ip} 时出错: {e}")
        
        return host_info
    
    def scan_range(self, target_input: str, progress_callback=None) -> List[HostInfo]:
        """
        扫描指定范围的主机
        
        Args:
            target_input: 目标输入
            progress_callback: 进度回调函数
            
        Returns:
            扫描结果列表
        """
        self.is_scanning = True
        self.results = []
        
        # 解析目标
        targets = self._parse_targets(target_input)
        self.total_targets = len(targets)
        
        if self.total_targets == 0:
            # 自动获取本地网络
            network = self._get_local_network()
            targets = self._parse_targets(network)
            self.total_targets = len(targets)
        
        print(f"开始扫描 {self.total_targets} 个目标...")
        
        # 使用线程池并发扫描
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_ip = {executor.submit(self.scan_single, ip): ip for ip in targets}
            
            completed = 0
            for future in as_completed(future_to_ip):
                if not self.is_scanning:
                    break
                    
                ip = future_to_ip[future]
                try:
                    result = future.result(timeout=self.timeout + 1)
                    self.results.append(result)
                except Exception as e:
                    print(f"扫描 {ip} 时出错: {e}")
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, self.total_targets)
        
        self.is_scanning = False
        return self.results
    
    def stop_scan(self):
        """停止扫描"""
        self.is_scanning = False
    
    def export_results(self, results: List[HostInfo], format_type: str, filename: str):
        """
        导出扫描结果
        
        Args:
            results: 扫描结果
            format_type: 导出格式 ('csv', 'json', 'txt', 'excel')
            filename: 文件名
        """
        if format_type == 'csv':
            self._export_csv(results, filename)
        elif format_type == 'json':
            self._export_json(results, filename)
        elif format_type == 'txt':
            self._export_txt(results, filename)
        elif format_type == 'excel':
            self._export_excel(results, filename)
    
    def _export_csv(self, results: List[HostInfo], filename: str):
        """导出为CSV格式"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['IP地址', '状态', 'MAC地址', '主机名', '响应时间(ms)', '操作系统'])
            for host in results:
                writer.writerow([
                    host.ip, host.status, host.mac, 
                    host.hostname, host.response_time, host.os_type
                ])
    
    def _export_json(self, results: List[HostInfo], filename: str):
        """导出为JSON格式"""
        import json
        import datetime
        
        data = {
            'scan_time': datetime.datetime.now().isoformat(),
            'total_hosts': len(results),
            'online_hosts': len([h for h in results if h.status == '在线']),
            'results': [
                {
                    'ip': h.ip,
                    'status': h.status,
                    'mac': h.mac,
                    'hostname': h.hostname,
                    'response_time': h.response_time,
                    'os_type': h.os_type
                }
                for h in results
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _export_txt(self, results: List[HostInfo], filename: str):
        """导出为文本格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("网络主机扫描报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"扫描时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"扫描主机数: {len(results)}\n")
            f.write(f"在线主机数: {len([h for h in results if h.status == '在线'])}\n\n")
            
            f.write("在线主机列表:\n")
            f.write("-" * 50 + "\n")
            for host in results:
                if host.status == '在线':
                    f.write(f"IP地址: {host.ip}\n")
                    f.write(f"  主机名: {host.hostname}\n")
                    f.write(f"  MAC地址: {host.mac}\n")
                    f.write(f"  响应时间: {host.response_time}ms\n\n")
    
    def _export_excel(self, results: List[HostInfo], filename: str):
        """导出为Excel格式（需要pandas库）"""
        try:
            import pandas as pd
            
            data = []
            for host in results:
                data.append({
                    'IP地址': host.ip,
                    '状态': host.status,
                    'MAC地址': host.mac,
                    '主机名': host.hostname,
                    '响应时间(ms)': host.response_time,
                    '操作系统': host.os_type
                })
            
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)
        except ImportError:
            print("需要安装pandas库: pip install pandas")