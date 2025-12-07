#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图形用户界面模块
作者：张夏灵
班级：网云2302
学号：542307280233
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
from datetime import datetime
from typing import List

# 导入本地模块
from .scanner import NetworkScanner, HostInfo

class ScannerGUI:
    """扫描器图形界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("网络主机扫描软件 v1.0 - 张夏灵 网云2302")
        self.root.geometry("900x600")
        
        # 初始化扫描器
        self.scanner = NetworkScanner(max_threads=100, timeout=2)
        
        # 扫描结果队列
        self.result_queue = queue.Queue()
        
        # 创建界面
        self.setup_ui()
        
        # 定期检查结果队列
        self.check_queue()
        
    def setup_ui(self):
        """设置用户界面"""
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="网络主机存活扫描软件", 
            font=("微软雅黑", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 作者信息
        author_label = ttk.Label(
            main_frame,
            text="作者：张夏灵 | 班级：网云2302 | 学号：542307280233",
            font=("微软雅黑", 10)
        )
        author_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="扫描设置", padding="10")
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 扫描目标输入
        ttk.Label(control_frame, text="目标输入:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.target_entry = ttk.Entry(control_frame, width=30)
        self.target_entry.grid(row=0, column=1, pady=5, padx=5)
        self.target_entry.insert(0, "192.168.1.1-254")
        
        # 示例标签
        examples = ttk.Label(
            control_frame,
            text="示例:\n单个IP: 192.168.1.1\nIP范围: 192.168.1.1-100\n网段: 192.168.1.0/24"
        )
        examples.grid(row=1, column=0, columnspan=2, pady=10)
        
        # 快速扫描按钮
        self.quick_scan_btn = ttk.Button(
            control_frame,
            text="快速扫描当前网络",
            command=self.quick_scan,
            width=25
        )
        self.quick_scan_btn.grid(row=2, column=0, columnspan=2, pady=5)
        
        # 扫描按钮
        self.scan_btn = ttk.Button(
            control_frame,
            text="开始扫描",
            command=self.start_scan,
            width=25
        )
        self.scan_btn.grid(row=3, column=0, columnspan=2, pady=5)
        
        # 停止按钮
        self.stop_btn = ttk.Button(
            control_frame,
            text="停止扫描",
            command=self.stop_scan,
            width=25,
            state="disabled"
        )
        self.stop_btn.grid(row=4, column=0, columnspan=2, pady=5)
        
        # 线程数设置
        ttk.Label(control_frame, text="线程数:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.thread_var = tk.StringVar(value="100")
        thread_spinbox = ttk.Spinbox(
            control_frame,
            from_=1,
            to=500,
            textvariable=self.thread_var,
            width=10
        )
        thread_spinbox.grid(row=5, column=1, pady=5, padx=5)
        
        # 超时设置
        ttk.Label(control_frame, text="超时(秒):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.timeout_var = tk.StringVar(value="2")
        timeout_spinbox = ttk.Spinbox(
            control_frame,
            from_=1,
            to=10,
            textvariable=self.timeout_var,
            width=10
        )
        timeout_spinbox.grid(row=6, column=1, pady=5, padx=5)
        
        # 导出按钮框架
        export_frame = ttk.LabelFrame(control_frame, text="结果导出", padding="10")
        export_frame.grid(row=7, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        export_btn_width = 20
        ttk.Button(
            export_frame,
            text="导出为CSV",
            command=lambda: self.export_results('csv'),
            width=export_btn_width
        ).grid(row=0, column=0, pady=2)
        
        ttk.Button(
            export_frame,
            text="导出为JSON",
            command=lambda: self.export_results('json'),
            width=export_btn_width
        ).grid(row=1, column=0, pady=2)
        
        ttk.Button(
            export_frame,
            text="导出为TXT",
            command=lambda: self.export_results('txt'),
            width=export_btn_width
        ).grid(row=2, column=0, pady=2)
        
        ttk.Button(
            export_frame,
            text="导出为Excel",
            command=lambda: self.export_results('excel'),
            width=export_btn_width
        ).grid(row=3, column=0, pady=2)
        
        # 中间结果区域
        result_frame = ttk.LabelFrame(main_frame, text="扫描结果", padding="10")
        result_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建Treeview显示结果
        columns = ('IP地址', '状态', 'MAC地址', '主机名', '响应时间', '操作系统')
        self.result_tree = ttk.Treeview(
            result_frame,
            columns=columns,
            show='headings',
            height=20
        )
        
        # 设置列标题
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=120)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        self.result_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 设置网格权重
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        
        # 右侧信息面板
        info_frame = ttk.LabelFrame(main_frame, text="扫描信息", padding="10")
        info_frame.grid(row=2, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # 扫描进度
        ttk.Label(info_frame, text="扫描进度:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.progress_var = tk.StringVar(value="0/0")
        progress_label = ttk.Label(info_frame, textvariable=self.progress_var)
        progress_label.grid(row=0, column=1, pady=5)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(
            info_frame,
            orient=tk.HORIZONTAL,
            length=200,
            mode='determinate'
        )
        self.progress_bar.grid(row=1, column=0, columnspan=2, pady=10)
        
        # 统计信息
        self.stats_text = tk.Text(info_frame, width=25, height=10)
        self.stats_text.grid(row=2, column=0, columnspan=2, pady=10)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E))
        
        self.log_text = tk.Text(log_frame, width=100, height=8)
        self.log_text.grid(row=0, column=0)
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 设置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def log_message(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def update_progress(self, completed: int, total: int):
        """更新进度"""
        self.progress_var.set(f"{completed}/{total}")
        if total > 0:
            progress = (completed / total) * 100
            self.progress_bar['value'] = progress
        self.root.update()
        
    def quick_scan(self):
        """快速扫描当前网络"""
        self.target_entry.delete(0, tk.END)
        self.target_entry.insert(0, "自动检测")
        self.start_scan()
        
    def start_scan(self):
        """开始扫描"""
        target = self.target_entry.get().strip()
        
        if not target:
            messagebox.showwarning("警告", "请输入扫描目标")
            return
        
        # 更新按钮状态
        self.scan_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # 清空结果树
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 清空统计信息
        self.stats_text.delete(1.0, tk.END)
        
        # 获取设置参数
        try:
            max_threads = int(self.thread_var.get())
            timeout = int(self.timeout_var.get())
            self.scanner.max_threads = max_threads
            self.scanner.timeout = timeout
        except ValueError:
            messagebox.showerror("错误", "线程数和超时时间必须是数字")
            self.scan_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            return
        
        # 在后台线程中执行扫描
        scan_thread = threading.Thread(
            target=self._perform_scan,
            args=(target,),
            daemon=True
        )
        scan_thread.start()
        
        self.log_message(f"开始扫描目标: {target}")
        
    def _perform_scan(self, target: str):
        """执行扫描（在后台线程中）"""
        try:
            results = self.scanner.scan_range(
                target,
                progress_callback=self.update_progress
            )
            
            # 将结果放入队列供主线程处理
            self.result_queue.put(results)
            
        except Exception as e:
            self.result_queue.put(f"ERROR:{str(e)}")
            
    def check_queue(self):
        """定期检查结果队列"""
        try:
            while True:
                try:
                    result = self.result_queue.get_nowait()
                    
                    if isinstance(result, str) and result.startswith("ERROR:"):
                        # 错误处理
                        error_msg = result[6:]
                        messagebox.showerror("扫描错误", error_msg)
                        self.log_message(f"扫描出错: {error_msg}")
                    else:
                        # 显示结果
                        self.display_results(result)
                        self.update_stats(result)
                        
                    # 恢复按钮状态
                    self.scan_btn.config(state="normal")
                    self.stop_btn.config(state="disabled")
                    
                except queue.Empty:
                    break
        finally:
            # 每100毫秒检查一次
            self.root.after(100, self.check_queue)
            
    def display_results(self, results: List[HostInfo]):
        """显示扫描结果"""
        for host in results:
            values = (
                host.ip,
                host.status,
                host.mac,
                host.hostname,
                f"{host.response_time:.1f}ms" if host.response_time > 0 else "N/A",
                host.os_type
            )
            
            # 根据状态设置标签颜色
            if host.status == '在线':
                tag = 'online'
            else:
                tag = 'offline'
            
            self.result_tree.insert('', tk.END, values=values, tags=(tag,))
        
        # 配置标签样式
        self.result_tree.tag_configure('online', foreground='green')
        self.result_tree.tag_configure('offline', foreground='gray')
        
        self.log_message(f"扫描完成，共发现 {len(results)} 个主机")
        
    def update_stats(self, results: List[HostInfo]):
        """更新统计信息"""
        online_count = len([h for h in results if h.status == '在线'])
        total_count = len(results)
        
        stats = f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        stats += f"扫描目标数: {total_count}\n"
        stats += f"在线主机数: {online_count}\n"
        stats += f"离线主机数: {total_count - online_count}\n"
        stats += f"在线率: {(online_count/total_count*100):.1f}%\n\n"
        
        if online_count > 0:
            online_hosts = [h for h in results if h.status == '在线' and h.response_time > 0]
            if online_hosts:
                avg_time = sum([h.response_time for h in online_hosts]) / len(online_hosts)
                stats += f"平均响应时间: {avg_time:.1f}ms\n"
            
            # 显示前5个在线主机
            stats += "\n在线主机:\n"
            online_hosts = [h for h in results if h.status == '在线']
            for i, host in enumerate(online_hosts[:5]):
                stats += f"  {i+1}. {host.ip} ({host.hostname})\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
        
    def stop_scan(self):
        """停止扫描"""
        self.scanner.stop_scan()
        self.stop_btn.config(state="disabled")
        self.log_message("扫描已停止")
        
    def export_results(self, format_type: str):
        """导出结果"""
        # 获取所有结果
        results = []
        for item in self.result_tree.get_children():
            values = self.result_tree.item(item)['values']
            if values:
                # 处理响应时间字符串
                response_time_str = values[4]
                if response_time_str == 'N/A':
                    response_time = 0.0
                else:
                    response_time = float(response_time_str.replace('ms', ''))
                
                host = HostInfo(
                    ip=values[0],
                    status=values[1],
                    mac=values[2],
                    hostname=values[3],
                    response_time=response_time,
                    os_type=values[5]
                )
                results.append(host)
        
        if not results:
            messagebox.showwarning("警告", "没有可导出的结果")
            return
        
        # 选择保存文件
        file_extensions = {
            'csv': [('CSV文件', '*.csv')],
            'json': [('JSON文件', '*.json')],
            'txt': [('文本文件', '*.txt')],
            'excel': [('Excel文件', '*.xlsx')]
        }
        
        filename = filedialog.asksaveasfilename(
            defaultextension=f".{format_type}",
            filetypes=file_extensions[format_type],
            title=f"保存为{format_type.upper()}格式"
        )
        
        if filename:
            try:
                self.scanner.export_results(results, format_type, filename)
                messagebox.showinfo("成功", f"结果已导出到: {filename}")
                self.log_message(f"结果已导出: {filename}")
            except Exception as e:
                messagebox.showerror("导出失败", f"导出时出错: {str(e)}")
        
    def run(self):
        """运行主循环"""
        self.root.mainloop()

def main():
    """GUI主函数"""
    app = ScannerGUI()
    app.run()

if __name__ == "__main__":
    main()