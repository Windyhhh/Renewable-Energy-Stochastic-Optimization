# 安装指南

## 前置要求

### 1. 安装Python

本项目需要Python 3.7或更高版本。

**Windows系统:**
1. 访问 https://www.python.org/downloads/
2. 下载最新的Python 3.x版本
3. 运行安装程序，**务必勾选"Add Python to PATH"**
4. 验证安装：打开命令提示符，输入 `python --version`

**Linux/Mac系统:**
```bash
# 检查Python版本
python3 --version

# 如果未安装，使用包管理器安装
# Ubuntu/Debian:
sudo apt-get install python3 python3-pip

# Mac (使用Homebrew):
brew install python3
```

### 2. 安装依赖包

在项目根目录下运行：

```bash
# Windows
python -m pip install -r requirements.txt

# Linux/Mac
python3 -m pip install -r requirements.txt
```

依赖包列表：
- `numpy`: 数值计算
- `scipy`: 科学计算
- `pandas`: 数据处理
- `matplotlib`: 数据可视化
- `scikit-learn`: 机器学习（用于聚类）
- `pulp`: 线性规划求解器

## 验证安装

运行测试脚本验证安装：

```bash
# Windows
python test_installation.py

# Linux/Mac
python3 test_installation.py
```

如果所有测试通过，将看到：
```
✓ 所有测试通过！系统已正确安装。
```

## 常见问题

### Q1: 提示"python不是内部或外部命令"

**解决方案:**
1. 确认Python已安装
2. 将Python添加到系统PATH环境变量
3. 重启命令提示符/终端

### Q2: pip安装依赖失败

**解决方案:**
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源（如果网络慢）
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 导入模块失败

**解决方案:**
确保在项目根目录下运行脚本，或者将项目目录添加到PYTHONPATH：

```bash
# Windows
set PYTHONPATH=%PYTHONPATH%;C:\path\to\project

# Linux/Mac
export PYTHONPATH=$PYTHONPATH:/path/to/project
```

### Q4: PuLP求解器问题

**解决方案:**
PuLP默认使用CBC求解器。如果遇到问题，可以：

1. 手动安装CBC求解器
2. 或使用其他求解器（如GLPK）：
```bash
# 安装GLPK
# Windows: 下载预编译版本
# Linux:
sudo apt-get install glpk-utils

# Mac:
brew install glpk
```

## 快速开始

安装完成后，按以下步骤运行：

### 1. 运行测试
```bash
python test_installation.py
```

### 2. 运行简化示例（推荐首次使用）
```bash
python examples/simple_example.py
```

这个示例使用较少的场景，运行时间约1-2分钟。

### 3. 运行完整案例研究
```bash
python examples/case_study.py
```

这个案例使用完整参数，运行时间约5-10分钟。

## 目录结构

```
期刊/
├── src/                      # 源代码
│   ├── __init__.py
│   ├── data_generation.py    # 场景生成
│   ├── scenario_tree.py      # 场景树构建
│   ├── forward_pricing.py    # 远期定价
│   ├── risk_measures.py      # 风险度量
│   ├── optimization.py       # 优化模型
│   └── utils.py             # 工具函数
├── examples/                 # 示例程序
│   ├── simple_example.py    # 简化示例
│   └── case_study.py        # 完整案例
├── data/                     # 数据文件
│   └── input_data.json      # 输入参数
├── results/                  # 结果输出（自动创建）
├── requirements.txt          # 依赖列表
├── test_installation.py      # 安装测试
├── README.md                # 项目说明
├── USAGE.md                 # 使用指南
└── INSTALL.md               # 本文件
```

## 下一步

安装成功后，请阅读：
- `README.md`: 了解项目概述
- `USAGE.md`: 学习如何使用和自定义模型
- `examples/`: 查看示例代码

## 技术支持

如遇到问题，请检查：
1. Python版本是否 >= 3.7
2. 所有依赖包是否正确安装
3. 是否在项目根目录下运行脚本

