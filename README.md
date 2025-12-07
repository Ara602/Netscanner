# 网络主机扫描软件 (Netscanner) v1.0

一款功能强大的网络主机存活扫描工具，提供图形界面和命令行两种操作方式。

**开发者**：张夏灵 | **班级**：网云2302 | **学号**：542307280233

## 🚀 主要功能

✅ **快速扫描**
- 网络主机存活检测
- 支持单IP、IP范围、CIDR网段三种扫描模式
- 高效的多线程并发扫描

✅ **信息收集**
- 获取主机IP地址
- 检索MAC地址和主机名
- 测量响应时间
- 识别操作系统类型

✅ **灵活导出**
- TXT纯文本
- CSV表格格式
- JSON数据格式
- Excel电子表格

✅ **用户友好**
- 直观的图形化界面
- 完整的命令行工具
- 实时进度显示
- 详细的统计信息

## 💻 系统要求

| 项目 | 要求 |
|------|------|
| **操作系统** | Windows 7/10/11 (64位) \| Linux \| macOS |
| **Python版本** | 3.8 或更高 |
| **内存** | 至少 512MB |
| **磁盘空间** | 至少 100MB |
| **权限** | 管理员权限（获取MAC地址） |
| **网络** | 需要网络连接 |

## 📦 快速开始

### 方式一：使用可执行文件（推荐）
```bash
# Windows
双击 "网络主机扫描器.exe"

# Linux/macOS
./网络主机扫描器
```

### 方式二：从源代码运行

#### 1. 克隆仓库
```bash
git clone https://github.com/Ara602/Netscanner.git
cd Netscanner
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 启动软件

**图形界面**
```bash
python main.py gui
# 或直接运行
python main.py
```

**命令行工具**
```bash
python main.py cli 192.168.1.0/24 -t 100 --timeout 2
```

## 📖 使用示例

### 图形界面操作
1. 启动程序：`python main.py`
2. 输入扫描目标（IP/范围/网段）
3. 调整线程数和超时时间
4. 点击"开始扫描"按钮
5. 查看实时进度和结果
6. 导出扫描结果

### 命令行操作

```bash
# 扫描单个IP
python main.py cli 192.168.1.100

# 扫描IP范围
python main.py cli 192.168.1.1-100 -t 50 --timeout 3

# 扫描整个网段
python main.py cli 192.168.1.0/24 -t 100

# 导出为CSV
python main.py cli 192.168.1.0/24 -o results.csv --format csv

# 导出为Excel
python main.py cli 192.168.1.0/24 -o results.xlsx --format excel

# 导出为JSON
python main.py cli 192.168.1.0/24 -o results.json --format json
```

## ⚙️ 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `-t, --threads` | 线程数 | 50 | `-t 100` |
| `--timeout` | 超时时间（秒） | 2 | `--timeout 3` |
| `-o, --output` | 输出文件路径 | 控制台 | `-o results.csv` |
| `--format` | 输出格式 | txt | `--format csv` |
| `--quiet` | 静默模式 | 否 | `--quiet` |
| `--verbose` | 详细模式 | 否 | `--verbose` |

## 🔧 构建可执行文件

### Windows
```bash
python build.py
# 或
release.bat
```

### Linux/macOS
```bash
chmod +x release.sh
./release.sh
```

## 📁 项目结构

```
Netscanner/
├── src/                          # 源代码目录
│   ├── __init__.py              # 包初始化
│   ├── scanner.py               # 核心扫描模块
│   ├── cli.py                   # 命令行界面
│   ├── gui.py                   # 图形界面
│   └── utils.py                 # 工具函数
├── docs/                         # 文档目录
│   └── 使用手册.md              # 详细使用手册
├── build/                        # 构建输出目录
├── dist/                         # 发行版本目录
├── main.py                       # 程序入口
├── build.py                      # 构建脚本
├── requirements.txt              # 依赖声明
├── pyproject.toml               # 项目配置
├── README.md                     # 本文件
└── LICENSE.txt                   # MIT许可证
```

## ⚠️ 注意事项

1. **防火墙阻止**：扫描大量IP时可能被防火墙拦截，请调整防火墙设置
2. **管理员权限**：在Windows上需要管理员权限以获取MAC地址
3. **网络影响**：扫描速度受网络状况影响，建议在局域网使用
4. **合法使用**：请勿用于非法用途，仅在授权的网络上使用
5. **线程数调整**：
   - 局域网：100-200线程
   - 远程网络：20-50线程
   - 低性能设备：10-30线程

## 🐛 常见问题

**Q: 无法获取MAC地址？**

A: 需要以管理员身份运行程序

**Q: 扫描速度很慢？**

A: 增加线程数：`-t 200` 或降低超时时间：`--timeout 1`

**Q: 导出Excel失败？**

A: 安装pandas和openpyxl：`pip install pandas openpyxl`

**Q: 权限被拒绝？**

A: 使用管理员权限运行或使用sudo（Linux/macOS）

详见 [使用手册.md](docs/使用手册.md) 获取更多帮助。

## 📞 技术支持

- **GitHub**: [https://github.com/Ara602/Netscanner](https://github.com/Ara602/Netscanner)
- **邮箱**: 3518023245@qq.com
- **Issue**: 在GitHub仓库中提交Issue获得官方支持

## 📄 许可证

MIT License - 详见 [LICENSE.txt](LICENSE.txt)

## 🙏 致谢

感谢所有使用者的支持与鼓励！