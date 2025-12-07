# Netscanner 项目文件速查指南

## 📋 文件一览表

| 文件/目录 | 类型 | 行数 | 说明 |
|---------|------|------|------|
| **main.py** | Python | 283 | 程序主入口，选择运行GUI或CLI |
| **src/scanner.py** | Python | 958 | 核心扫描引擎，处理所有扫描逻辑 |
| **src/cli.py** | Python | ~100 | 命令行界面模块 |
| **src/gui.py** | Python | 455 | 图形用户界面模块（Tkinter） |
| **src/utils.py** | Python | - | 工具函数集合 |
| **src/__init__.py** | Python | - | 包初始化文件 |
| **README.md** | Markdown | 208 | 项目总体说明文档 |
| **docs/使用手册.md** | Markdown | - | 详细的用户使用手册 |
| **requirements.txt** | Text | 12 | Python依赖包声明 |
| **pyproject.toml** | TOML | 35 | 项目元数据和配置 |
| **build.py** | Python | 177 | PyInstaller打包脚本 |
| **pyinstaller_config.py** | Python | - | PyInstaller配置（可选） |
| **release.bat** | Batch | - | Windows发布脚本 |
| **release.sh** | Shell | - | Linux/macOS发布脚本 |
| **PROJECT_STRUCTURE.md** | Markdown | - | 项目结构详细说明文档 |
| **LICENSE.txt** | Text | - | MIT许可证 |

---

## 🎯 快速查找功能

### 如果你想要...

#### ✏️ **修改/扩展程序功能**
1. **添加新的扫描方法** → `src/scanner.py` 中的 `NetworkScanner` 类
2. **改进GUI界面** → `src/gui.py` 中的 `ScannerGUI` 类
3. **增加CLI参数** → `src/cli.py` 中的 `argparse` 配置部分
4. **添加工具函数** → `src/utils.py`

#### 📖 **查看使用说明**
1. **快速开始** → `README.md`
2. **详细使用** → `docs/使用手册.md`
3. **项目结构** → `PROJECT_STRUCTURE.md`

#### 🔧 **打包/部署**
1. **构建exe** → `build.py` 或 `release.bat`
2. **构建Linux/Mac** → `release.sh`
3. **配置打包** → `pyproject.toml` 和 `build.py`

#### 📦 **管理依赖**
1. **查看依赖** → `requirements.txt`
2. **修改依赖** → `requirements.txt` 或 `pyproject.toml`

#### 🐛 **调试和测试**
1. **主程序入口** → `main.py` 的 `check_dependencies()` 函数
2. **扫描逻辑** → `src/scanner.py` 的 `scan_range()` 方法
3. **运行测试** → `run_tests.py`

---

## 🔑 核心类和关键函数

### NetworkScanner 类 (src/scanner.py)
```python
# 创建扫描器实例
scanner = NetworkScanner(max_threads=100, timeout=2)

# 扫描IP范围/CIDR/单IP
results = scanner.scan_range("192.168.1.0/24", progress_callback)

# 获取单个主机信息
host_info = scanner.ping_host("192.168.1.1")

# 导出结果
scanner.export_results(results, format='csv', filepath='output.csv')
```

### ScannerGUI 类 (src/gui.py)
```python
# 创建GUI实例
app = ScannerGUI()

# 启动应用
app.run()
```

### CLI 主函数 (src/cli.py)
```python
# 直接调用
from src.cli import main
main()
```

---

## 🎨 界面布局

### GUI 界面结构
```
┌─ 网络主机扫描软件 v1.0 ─────────────────────────────────┐
│ 作者：张夏灵 | 班级：网云2302 | 学号：542307280233       │
├────────────────────────────────────────────────────────┤
│ ┌─ 扫描设置 ─────────────┐  ┌─ 实时结果 ─────────────┐ │
│ │ 目标输入: [________]    │  │ 扫描进度: [████░░░░░] │ │
│ │ 线程数: [100]          │  │ 在线主机: 5/50         │ │
│ │ 超时: [2] 秒           │  │ 扫描状态: 进行中...    │ │
│ │                        │  │                        │ │
│ │ [快速扫描当前网络]     │  │ ┌──────────────────┐ │ │
│ │ [开始扫描]  [停止]     │  │ │ IP      主机名    │ │ │
│ │ [导出结果]              │  │ │ 192.168.1.100 PC1│ │ │
│ │                        │  │ │ 192.168.1.101 PC2│ │ │
│ │                        │  │ └──────────────────┘ │ │
│ └────────────────────────┘  └──────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 常用命令

### 开发和调试
```bash
# 运行图形界面
python main.py gui
python main.py

# 运行命令行
python main.py cli 192.168.1.1-100 -t 50

# 格式化代码
black src/

# 代码检查
flake8 src/

# 运行测试
python run_tests.py
```

### 打包和部署
```bash
# 清理之前的构建
rm -rf build dist

# Windows打包
python build.py
release.bat

# Linux/Mac打包
chmod +x release.sh
./release.sh
```

### 依赖管理
```bash
# 安装依赖
pip install -r requirements.txt

# 更新依赖
pip install --upgrade -r requirements.txt

# 生成依赖列表
pip freeze > requirements.txt
```

---

## 📊 数据流

```
用户输入
  ↓
参数验证 → IP解析 → 生成IP列表
  ↓
多线程扫描
  ├─ Ping检测
  ├─ MAC获取
  ├─ Hostname解析
  └─ 响应时间计算
  ↓
结果收集
  ├─ HostInfo对象列表
  └─ 统计信息
  ↓
输出/导出
  ├─ 控制台显示
  ├─ GUI界面显示
  ├─ CSV文件
  ├─ JSON文件
  ├─ TXT文件
  └─ Excel文件
```

---

## 🔄 扫描流程详解

### 1. IP范围解析
```python
"192.168.1.1-100"        → [192.168.1.1, 192.168.1.2, ..., 192.168.1.100]
"192.168.1.0/24"         → [192.168.1.1, 192.168.1.2, ..., 192.168.1.254]
"192.168.1.100"          → [192.168.1.100]
```

### 2. 并发扫描
```
输入IP列表
  ↓
创建线程池（默认100线程）
  ↓
分配任务给线程
  ↓
每个线程执行 ping_host()
  ↓
收集结果到列表
  ↓
返回HostInfo对象列表
```

### 3. 结果导出
```
CSV:   IP, 主机名, MAC, 响应时间, OS类型
JSON:  {"results": [{...}, {...}]}
TXT:   格式化的文本输出
Excel: 多行表格格式
```

---

## 🛠️ 故障排除快查表

| 问题 | 原因 | 解决方案 | 相关文件 |
|------|------|--------|--------|
| ImportError | 缺少依赖 | `pip install -r requirements.txt` | main.py |
| 无法获取MAC | 权限不足 | 以管理员运行 | scanner.py |
| 扫描缓慢 | 线程数少 | 增加 `-t` 参数 | scanner.py |
| GUI卡顿 | 主线程阻塞 | 检查是否用了多线程 | gui.py |
| 打包失败 | PyInstaller错误 | 检查build.py配置 | build.py |
| 无法导出Excel | pandas缺失 | `pip install pandas openpyxl` | scanner.py |

---

## 📈 性能优化建议

### 扫描速度
- **增加线程数**：`-t 200` （局域网可用200-500线程）
- **减少超时**：`--timeout 1` （局域网可设置1秒）
- **使用ICMP**：比TCP更快

### 内存使用
- **限制范围**：分批扫描小范围
- **启用分批导出**：避免一次性加载全部结果

### GUI响应
- **使用多线程**：确保扫描在后台线程
- **优化界面更新**：减少频繁的UI刷新

---

## 📚 文件修改历史

### 已优化项目
✅ **README.md** - 升级为专业格式，添加徽章和表格  
✅ **docs/使用手册.md** - 修复Markdown格式，优化结构  
✅ **PROJECT_STRUCTURE.md** - 新增详细项目结构说明  
✅ **QUICK_REFERENCE.md** - 本文件，快速查询指南  

---

## 💡 最佳实践

### 代码规范
- 遵循PEP 8风格指南
- 使用Black格式化代码
- 使用Flake8检查代码质量
- 添加类型注解提高可读性

### 文档维护
- 保持README最新
- 更新使用手册中的命令示例
- 在代码中添加docstring

### 版本控制
- 合理使用git分支
- 提交前进行测试
- 编写清晰的commit信息

### 错误处理
- 捕获特定异常
- 提供有意义的错误信息
- 记录日志便于调试

---

## 🔗 相关资源

### 官方文档
- [Python官网](https://www.python.org)
- [Tkinter官方文档](https://docs.python.org/3/library/tkinter.html)
- [PyInstaller官方文档](https://pyinstaller.readthedocs.io)

### 项目链接
- **GitHub**: https://github.com/Ara602/Netscanner
- **Issue追踪**: https://github.com/Ara602/Netscanner/issues

---

## 📞 快速联系

- **开发者**: 张夏灵
- **邮箱**: 3518023245@qq.com
- **班级**: 网云2302
- **学号**: 542307280233

---

**最后更新**: 2025年12月7日  
**文档版本**: 1.0
