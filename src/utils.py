#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
作者：张夏灵
班级：网云2302
学号：542307280233
"""

import ipaddress
import socket
import re
from typing import List

def is_valid_ip(ip: str) -> bool:
    """检查IP地址是否有效"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_cidr(cidr: str) -> bool:
    """检查CIDR表示法是否有效"""
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False

def ip_range_to_list(start_ip: str, end_ip: str) -> List[str]:
    """将IP范围转换为IP列表"""
    try:
        start = ipaddress.ip_address(start_ip)
        end = ipaddress.ip_address(end_ip)
        
        if start > end:
            start, end = end, start
            
        return [str(ipaddress.ip_address(ip)) 
                for ip in range(int(start), int(end) + 1)]
    except ValueError:
        return []

def get_local_ip() -> str:
    """获取本地IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def format_mac(mac: str) -> str:
    """格式化MAC地址（统一为冒号分隔）"""
    if not mac or mac == "未知":
        return "未知"
    
    # 移除所有分隔符
    mac = re.sub(r'[:\-\.]', '', mac)
    
    if len(mac) != 12:
        return mac
    
    # 添加冒号分隔符
    return ':'.join(mac[i:i+2] for i in range(0, 12, 2))

def format_time(seconds: float) -> str:
    """格式化时间"""
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}min"
    else:
        return f"{seconds/3600:.1f}h"