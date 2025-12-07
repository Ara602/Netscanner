#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行界面模块
作者：张夏灵
班级：网云2302
学号：542307280233
"""

import argparse
import json
from datetime import datetime
from src.scanner import NetworkScanner

def main():
    parser = argparse.ArgumentParser(description='网络主机存活扫描软件 - 命令行版')
    
    parser.add_argument('target', help='扫描目标 (IP, IP范围, CIDR)')
    parser.add_argument('-t', '--threads', type=int, default=100, help='线程数 (默认: 100)')
    parser.add_argument('-o', '--output', help='输出文件')
    parser.add_argument('--format', choices=['csv', 'json', 'txt', 'excel'], 
                       default='txt', help='输出格式 (默认: txt)')
    parser.add_argument('--timeout', type=int, default=2, help='超时时间(秒) (默认: 2)')
    
    args = parser.parse_args()
    
    print(f"""
    网络主机存活扫描软件 v1.0
    作者：张夏灵
    班级：网云2302
    学号：542307280233
    """)
    
    print(f"开始扫描: {args.target}")
    print(f"线程数: {args.threads}")
    print(f"超时时间: {args.timeout}秒")
    print("-" * 50)
    
    scanner = NetworkScanner(max_threads=args.threads, timeout=args.timeout)
    
    def progress_callback(completed, total):
        progress = (completed / total) * 100
        print(f"\r扫描进度: {completed}/{total} ({progress:.1f}%)", end="")
    
    try:
        results = scanner.scan_range(args.target, progress_callback)
        
        print(f"\n\n扫描完成!")
        print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"扫描主机数: {len(results)}")
        print(f"在线主机数: {len([h for h in results if h.status == '在线'])}")
        
        print("\n在线主机列表:")
        print("-" * 50)
        for host in results:
            if host.status == '在线':
                print(f"IP: {host.ip:15} | 主机名: {host.hostname:20} | MAC: {host.mac:17} | 延迟: {host.response_time:.1f}ms")
        
        if args.output:
            scanner.export_results(results, args.format, args.output)
            print(f"\n结果已导出到: {args.output}")
            
    except KeyboardInterrupt:
        print("\n\n扫描被用户中断")
    except Exception as e:
        print(f"\n扫描出错: {str(e)}")

if __name__ == "__main__":
    main()