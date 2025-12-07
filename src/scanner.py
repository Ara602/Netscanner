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
from typing import List, Dict, Tuple, Optional, Callable
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
        ICMP Ping扫描 - 跨平台实现
        
        Args:
            ip: 目标IP地址
            
        Returns:
            (是否在线, 响应时间毫秒)
        """
        # 获取当前操作系统
        current_os = platform.system().lower()
        
        # 根据操作系统选择ping命令参数
        if current_os == "windows":
            # Windows系统
            return self._ping_windows(ip)
        elif current_os == "darwin":
            # macOS系统
            return self._ping_macos(ip)
        else:
            # Linux和其他Unix-like系统
            return self._ping_linux(ip)
    
    def _ping_windows(self, ip: str) -> Tuple[bool, float]:
        """Windows系统Ping实现"""
        # Windows ping命令参数:
        # -n 次数
        # -w 超时时间(毫秒)
        # -l 数据包大小
        # -4 强制使用IPv4
        
        timeout_ms = int(self.timeout * 1000)  # 转换为毫秒
        
        command = [
            "ping",
            "-n", "1",  # 发送1个数据包
            "-w", str(timeout_ms),  # 超时时间
            "-l", "32",  # 数据包大小32字节
            "-4",  # 强制使用IPv4
            ip
        ]
        
        try:
            # 执行ping命令
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='gbk',  # Windows中文系统使用GBK编码
                timeout=self.timeout + 1,
                creationflags=subprocess.CREATE_NO_WINDOW  # 不显示控制台窗口
            )
            
            # 解析Windows ping输出
            # Windows ping输出示例:
            # 正在 Ping 192.168.1.1 具有 32 字节的数据:
            # 来自 192.168.1.1 的回复: 字节=32 时间=1ms TTL=64
            # Ping 统计信息 192.168.1.1:
            #     数据包: 已发送 = 1，已接收 = 1，丢失 = 0 (0% 丢失)，
            # 往返行程的估计时间(以毫秒为单位):
            #     最短 = 1ms，最长 = 1ms，平均 = 1ms
            
            output = result.stdout
            
            # 检查是否在线
            online_indicators = [
                "TTL=",  # 正常情况
                "TTL ",  # 某些Windows版本
                "字节=",  # 中文Windows
                "来自"  # 中文Windows
            ]
            
            is_online = any(indicator in output for indicator in online_indicators)
            
            if not is_online:
                return False, 0.0
            
            # 提取响应时间
            response_time = 0.0
            
            # 尝试多种匹配模式
            time_patterns = [
                r'时间[=<](\d+)ms',  # 中文: 时间=1ms
                r'时间=(\d+)ms',  # 中文: 时间=1ms
                r'时间[=<](\d+)\s*毫秒',  # 中文: 时间=1毫秒
                r'time[=<](\d+)ms',  # 英文: time=1ms
                r'time=(\d+)ms',  # 英文: time=1ms
                r'time[=<](\d+)\s*milliseconds',  # 英文: time=1 milliseconds
                r'(\d+)\s*ms'  # 通用: 1ms
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    try:
                        response_time = float(match.group(1))
                        break
                    except ValueError:
                        continue
            
            # 如果没找到响应时间，但主机在线，返回默认值
            return True, response_time
            
        except subprocess.TimeoutExpired:
            # 命令执行超时
            return False, 0.0
        except subprocess.CalledProcessError:
            # 命令执行出错
            return False, 0.0
        except Exception:
            # 其他异常
            return False, 0.0
    
    def _ping_linux(self, ip: str) -> Tuple[bool, float]:
        """Linux系统Ping实现"""
        # Linux ping命令参数:
        # -c 次数
        # -W 超时时间(秒)
        # -s 数据包大小
        # -4 强制使用IPv4
        
        command = [
            "ping",
            "-c", "1",  # 发送1个数据包
            "-W", str(self.timeout),  # 超时时间秒
            "-s", "32",  # 数据包大小32字节
            "-4",  # 强制使用IPv4
            ip
        ]
        
        try:
            # 执行ping命令
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=self.timeout + 1
            )
            
            # 解析Linux ping输出
            # Linux ping输出示例:
            # PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.
            # 64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.123 ms
            # --- 192.168.1.1 ping statistics ---
            # 1 packets transmitted, 1 received, 0% packet loss, time 0ms
            # rtt min/avg/max/mdev = 0.123/0.123/0.123/0.000 ms
            
            output = result.stdout
            
            # 检查是否在线
            is_online = False
            if result.returncode == 0:
                # 检查是否有响应行
                lines = output.split('\n')
                for line in lines:
                    if 'bytes from' in line and 'icmp_seq=' in line:
                        is_online = True
                        break
            
            if not is_online:
                return False, 0.0
            
            # 提取响应时间
            response_time = 0.0
            
            # 匹配时间模式
            time_patterns = [
                r'time=([\d.]+)\s*ms',  # time=0.123 ms
                r'time=([\d.]+)ms',  # time=0.123ms
                r'(\d+\.\d+)\s*ms',  # 0.123 ms
                r'(\d+)\s*ms'  # 123 ms
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, output)
                if match:
                    try:
                        response_time = float(match.group(1))
                        break
                    except ValueError:
                        continue
            
            return True, response_time
            
        except subprocess.TimeoutExpired:
            return False, 0.0
        except subprocess.CalledProcessError:
            return False, 0.0
        except Exception:
            return False, 0.0
    
    def _ping_macos(self, ip: str) -> Tuple[bool, float]:
        """macOS系统Ping实现"""
        # macOS ping命令参数:
        # -c 次数
        # -t 超时时间(秒)
        # -s 数据包大小
        
        command = [
            "ping",
            "-c", "1",  # 发送1个数据包
            "-t", str(self.timeout),  # 超时时间秒
            "-s", "32",  # 数据包大小32字节
            ip
        ]
        
        try:
            # 执行ping命令
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=self.timeout + 1
            )
            
            # 解析macOS ping输出
            # macOS ping输出与Linux类似:
            # PING 192.168.1.1 (192.168.1.1): 56 data bytes
            # 64 bytes from 192.168.1.1: icmp_seq=0 ttl=64 time=1.234 ms
            # --- 192.168.1.1 ping statistics ---
            # 1 packets transmitted, 1 packets received, 0.0% packet loss
            # round-trip min/avg/max/stddev = 1.234/1.234/1.234/0.000 ms
            
            output = result.stdout
            
            # 检查是否在线
            is_online = False
            if result.returncode == 0:
                # 检查是否有响应行
                lines = output.split('\n')
                for line in lines:
                    if 'bytes from' in line and 'icmp_seq=' in line:
                        is_online = True
                        break
            
            if not is_online:
                return False, 0.0
            
            # 提取响应时间
            response_time = 0.0
            
            # 匹配时间模式
            time_patterns = [
                r'time=([\d.]+)\s*ms',  # time=1.234 ms
                r'time=([\d.]+)ms',  # time=1.234ms
                r'(\d+\.\d+)\s*ms',  # 1.234 ms
                r'(\d+)\s*ms'  # 1234 ms
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, output)
                if match:
                    try:
                        response_time = float(match.group(1))
                        break
                    except ValueError:
                        continue
            
            return True, response_time
            
        except subprocess.TimeoutExpired:
            return False, 0.0
        except subprocess.CalledProcessError:
            return False, 0.0
        except Exception:
            return False, 0.0
    
    def get_mac_address(self, ip: str) -> str:
        """
        获取MAC地址（仅限局域网）- 跨平台实现
        
        Args:
            ip: 目标IP地址
            
        Returns:
            MAC地址字符串
        """
        current_os = platform.system().lower()
        
        if current_os == "windows":
            return self._get_mac_windows(ip)
        elif current_os == "darwin":
            return self._get_mac_macos(ip)
        else:
            return self._get_mac_linux(ip)
    
    def _get_mac_windows(self, ip: str) -> str:
        """Windows系统获取MAC地址"""
        try:
            # 使用arp命令，先ping一下确保ARP表中有记录
            subprocess.run(
                ["ping", "-n", "1", "-w", "1000", ip],
                capture_output=True,
                timeout=1,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # 然后查询ARP表
            arp_command = ["arp", "-a", ip]
            output = subprocess.run(
                arp_command,
                capture_output=True,
                text=True,
                encoding='gbk',
                timeout=2
            ).stdout
            
            # Windows ARP表格式:
            # 接口: 192.168.1.100 --- 0x3
            #   192.168.1.1           00-11-22-33-44-55     动态
            
            # 解析MAC地址
            mac_patterns = [
                r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})',  # 标准格式
                r'([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}',  # 横线分隔
                r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}'  # 冒号分隔
            ]
            
            for pattern in mac_patterns:
                match = re.search(pattern, output)
                if match:
                    mac = match.group(0)
                    # 统一格式化为冒号分隔
                    mac = re.sub(r'[^0-9A-Fa-f]', '', mac)
                    if len(mac) == 12:
                        return ':'.join(mac[i:i+2].upper() for i in range(0, 12, 2))
        except Exception:
            pass
        
        return "未知"
    
    def _get_mac_linux(self, ip: str) -> str:
        """Linux系统获取MAC地址"""
        try:
            # 先ping一下确保ARP表中有记录
            subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip],
                capture_output=True,
                timeout=1
            )
            
            # 然后查询ARP表
            arp_command = ["arp", "-n", ip]
            output = subprocess.run(
                arp_command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=2
            ).stdout
            
            # Linux ARP表格式:
            # Address                  HWtype  HWaddress           Flags Mask            Iface
            # 192.168.1.1              ether   00:11:22:33:44:55   C                     eth0
            
            # 解析MAC地址
            mac_pattern = r'([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}'
            match = re.search(mac_pattern, output)
            
            if match:
                return match.group(0).upper()
        except Exception:
            pass
        
        return "未知"
    
    def _get_mac_macos(self, ip: str) -> str:
        """macOS系统获取MAC地址"""
        try:
            # 先ping一下确保ARP表中有记录
            subprocess.run(
                ["ping", "-c", "1", "-t", "1", ip],
                capture_output=True,
                timeout=1
            )
            
            # 然后查询ARP表
            arp_command = ["arp", "-n", ip]
            output = subprocess.run(
                arp_command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=2
            ).stdout
            
            # macOS ARP表格式:
            # ? (192.168.1.1) at 00:11:22:33:44:55 on en0 ifscope [ethernet]
            
            # 解析MAC地址
            mac_pattern = r'at\s+([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
            match = re.search(mac_pattern, output)
            
            if match:
                mac = match.group(0)[3:]  # 去掉"at "
                # 统一格式化为冒号分隔
                mac = re.sub(r'[^0-9A-Fa-f]', '', mac)
                if len(mac) == 12:
                    return ':'.join(mac[i:i+2].upper() for i in range(0, 12, 2))
        except Exception:
            pass
        
        return "未知"
    
    def get_hostname(self, ip: str) -> str:
        """
        获取主机名 - 跨平台实现
        
        Args:
            ip: 目标IP地址
            
        Returns:
            主机名
        """
        try:
            # 尝试反向DNS解析
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except socket.herror:
            # 如果反向DNS失败，尝试使用socket.getfqdn
            try:
                return socket.getfqdn(ip)
            except:
                # 最后尝试使用系统命令
                return self._get_hostname_system(ip)
        except Exception:
            return "未知"
    
    def _get_hostname_system(self, ip: str) -> str:
        """使用系统命令获取主机名"""
        current_os = platform.system().lower()
        
        try:
            if current_os == "windows":
                # Windows使用nbtstat命令
                command = ["nbtstat", "-A", ip]
                output = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding='gbk',
                    timeout=2
                ).stdout
                
                # 解析Windows输出中的主机名
                for line in output.split('\n'):
                    if "<00>" in line and "UNIQUE" in line:
                        parts = line.split()
                        if len(parts) > 0:
                            return parts[0]
            else:
                # Linux/macOS使用nmblookup命令
                command = ["nmblookup", "-A", ip]
                output = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=2
                ).stdout
                
                # 解析NetBIOS名称
                for line in output.split('\n'):
                    if "<00>" in line and "UNIQUE" in line:
                        parts = line.split()
                        if len(parts) > 1:
                            return parts[0]
        except Exception:
            pass
        
        return "未知"
    
    def _get_local_network(self) -> str:
        """获取本地网络地址 - 跨平台实现"""
        try:
            current_os = platform.system().lower()
            
            if current_os == "windows":
                # Windows使用ipconfig命令
                command = ["ipconfig"]
                output = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding='gbk'
                ).stdout
                
                # 解析Windows ipconfig输出
                for line in output.split('\n'):
                    if "IPv4" in line or "IP Address" in line:
                        match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if match:
                            ip = match.group(1)
                            # 假设使用C类地址
                            parts = ip.split('.')
                            return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
            
            else:
                # Linux/macOS使用ifconfig或ip命令
                try:
                    command = ["ip", "-4", "addr", "show"]
                    output = subprocess.run(
                        command,
                        capture_output=True,
                        text=True
                    ).stdout
                except:
                    command = ["ifconfig"]
                    output = subprocess.run(
                        command,
                        capture_output=True,
                        text=True
                    ).stdout
                
                # 解析网络接口信息
                for line in output.split('\n'):
                    if "inet " in line:
                        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                        if match:
                            ip = match.group(1)
                            # 获取子网掩码
                            mask_match = re.search(r'netmask (\d+\.\d+\.\d+\.\d+)', line)
                            if mask_match:
                                mask = mask_match.group(1)
                                # 计算CIDR
                                cidr = sum(bin(int(x)).count('1') for x in mask.split('.'))
                                return f"{ip}/{cidr}"
                            else:
                                # 假设使用C类地址
                                parts = ip.split('.')
                                return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        except Exception:
            pass
        
        # 默认返回常见的内网网段
        return "192.168.1.0/24"
    
    def _parse_targets(self, target_input: str) -> List[str]:
        """
        解析目标输入 - 增强的跨平台解析
        
        Args:
            target_input: 可以是单个IP、IP范围、CIDR
            
        Returns:
            IP地址列表
        """
        targets = []
        
        # 检查是否为"自动检测"
        if target_input in ["自动检测", "auto", "autodetect"]:
            network = self._get_local_network()
            target_input = network
        
        try:
            # 单个IP
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target_input):
                # 验证IP有效性
                ipaddress.ip_address(target_input)
                targets.append(target_input)
            
            # IP范围 192.168.1.1-100
            elif '-' in target_input:
                base_ip, range_part = target_input.split('-')
                base_parts = base_ip.split('.')
                
                if len(base_parts) == 4 and range_part.isdigit():
                    start = int(base_parts[3])
                    end = int(range_part)
                    
                    # 确保范围合理
                    if start < 0 or start > 255 or end < 0 or end > 255:
                        raise ValueError("IP范围必须在0-255之间")
                    
                    if start > end:
                        start, end = end, start
                    
                    for i in range(start, end + 1):
                        ip = f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{i}"
                        targets.append(ip)
            
            # CIDR格式 192.168.1.0/24
            elif '/' in target_input:
                network = ipaddress.ip_network(target_input, strict=False)
                for ip in network.hosts():
                    targets.append(str(ip))
            
            # 逗号分隔的IP列表
            elif ',' in target_input:
                for ip in target_input.split(','):
                    ip = ip.strip()
                    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                        targets.append(ip)
            
            # IP列表文件
            elif target_input.endswith('.txt'):
                if os.path.exists(target_input):
                    with open(target_input, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                targets.extend(self._parse_targets(line))
                else:
                    print(f"文件不存在: {target_input}")
            
            else:
                # 尝试解析为单个IP
                try:
                    ipaddress.ip_address(target_input)
                    targets.append(target_input)
                except ValueError:
                    print(f"无法解析的目标格式: {target_input}")
                    
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
                
                # 获取更多信息（如果在线）
                try:
                    # 获取MAC地址（需要权限）
                    if self._is_windows_admin():
                        host_info.mac = self.get_mac_address(ip)
                    
                    # 获取主机名
                    host_info.hostname = self.get_hostname(ip)
                    
                    # 简单猜测操作系统类型（根据TTL值）
                    # 注：这是一个简化的猜测，实际应用中需要更复杂的方法
                    if response_time > 0:
                        # Windows默认TTL=128，Linux/Unix默认TTL=64
                        pass
                except Exception as e:
                    print(f"获取主机 {ip} 额外信息时出错: {e}")
        except Exception as e:
            print(f"扫描 {ip} 时出错: {e}")
        
        return host_info
    
    def scan_range(self, target_input: str, progress_callback: Optional[Callable[[int, int], None]] = None) -> List[HostInfo]:
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
        
        if self.total_targets == 0:
            print("没有可扫描的目标")
            return []
        
        print(f"开始扫描 {self.total_targets} 个目标...")
        print(f"操作系统: {platform.system()} {platform.release()}")
        print(f"线程数: {self.max_threads}, 超时: {self.timeout}秒")
        
        # 使用线程池并发扫描
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_ip = {executor.submit(self.scan_single, ip): ip for ip in targets}
            
            completed = 0
            for future in as_completed(future_to_ip):
                if not self.is_scanning:
                    print("扫描被用户停止")
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
        
        # 统计结果
        online_count = len([h for h in self.results if h.status == '在线'])
        print(f"扫描完成! 在线主机: {online_count}/{self.total_targets}")
        
        return self.results
    
    def stop_scan(self):
        """停止扫描"""
        self.is_scanning = False
        print("正在停止扫描...")
    
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
                    host.ip, 
                    host.status, 
                    host.mac, 
                    host.hostname, 
                    f"{host.response_time:.1f}", 
                    host.os_type
                ])
    
    def _export_json(self, results: List[HostInfo], filename: str):
        """导出为JSON格式"""
        import json
        import datetime
        
        data = {
            'scan_time': datetime.datetime.now().isoformat(),
            'operating_system': f"{platform.system()} {platform.release()}",
            'total_hosts': len(results),
            'online_hosts': len([h for h in results if h.status == '在线']),
            'scan_config': {
                'max_threads': self.max_threads,
                'timeout': self.timeout
            },
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
            f.write("=" * 60 + "\n")
            f.write("            网络主机扫描报告\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"扫描时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"操作系统: {platform.system()} {platform.release()}\n")
            f.write(f"扫描配置: 线程数={self.max_threads}, 超时={self.timeout}秒\n")
            f.write(f"扫描主机数: {len(results)}\n")
            
            online_hosts = [h for h in results if h.status == '在线']
            f.write(f"在线主机数: {len(online_hosts)}\n")
            f.write(f"离线主机数: {len(results) - len(online_hosts)}\n")
            
            if online_hosts:
                avg_time = sum([h.response_time for h in online_hosts]) / len(online_hosts)
                f.write(f"平均响应时间: {avg_time:.1f}ms\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("在线主机列表:\n")
            f.write("=" * 60 + "\n\n")
            
            for i, host in enumerate(online_hosts, 1):
                f.write(f"{i:3d}. IP地址: {host.ip}\n")
                f.write(f"     主机名: {host.hostname}\n")
                f.write(f"     MAC地址: {host.mac}\n")
                f.write(f"     响应时间: {host.response_time:.1f}ms\n")
                
                if host.os_type != "未知":
                    f.write(f"     操作系统: {host.os_type}\n")
                
                f.write("\n")
    
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
            
            # 添加元数据
            writer = pd.ExcelWriter(filename, engine='openpyxl')
            df.to_excel(writer, sheet_name='扫描结果', index=False)
            
            # 添加摘要信息
            workbook = writer.book
            worksheet = writer.sheets['扫描结果']
            
            # 在Excel文件属性中添加元数据
            workbook.properties.title = "网络主机扫描报告"
            workbook.properties.subject = "网络主机存活扫描结果"
            workbook.properties.creator = "张夏灵"
            workbook.properties.keywords = "网络扫描,主机发现,网络安全"
            
            writer.save()
            
        except ImportError:
            print("需要安装pandas和openpyxl库: pip install pandas openpyxl")
        except Exception as e:
            print(f"导出Excel时出错: {e}")

# 测试函数
def test_ping_function():
    """测试跨平台ping功能"""
    print("=" * 60)
    print("跨平台Ping功能测试")
    print("=" * 60)
    
    scanner = NetworkScanner()
    
    # 测试目标
    test_targets = [
        "127.0.0.1",  # 本地回环地址
        "192.168.1.1",  # 常见路由器地址
        "8.8.8.8"  # Google DNS
    ]
    
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print()
    
    for target in test_targets:
        print(f"测试ping: {target}")
        try:
            is_online, response_time = scanner.ping_host(target)
            status = "在线" if is_online else "离线"
            time_str = f"{response_time:.1f}ms" if response_time > 0 else "N/A"
            print(f"  结果: {status}, 响应时间: {time_str}")
        except Exception as e:
            print(f"  出错: {e}")
        print()

if __name__ == "__main__":
    test_ping_function()