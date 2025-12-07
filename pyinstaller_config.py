# PyInstaller配置文件

# 隐藏导入（PyInstaller可能无法自动检测到的模块）
hiddenimports = [
    'pandas',
    'openpyxl',
    'tkinter',
    'tkinter.ttk',
    'queue',
    'concurrent.futures',
    'ipaddress',
    'dataclasses',
    'typing',
]

# 数据文件
datas = [
    ('src/*.py', 'src'),
    ('README.md', '.'),
    ('requirements.txt', '.'),
]

# 排除的模块
excludes = [
    'matplotlib',
    'numpy',
    'scipy',
    'PyQt5',
    'PySide2',
    'pytest',
    'black',
    'flake8',
]

# 运行时hook
runtime_hooks = []

# 不再收集的模块
noarchive = False