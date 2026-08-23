# 使用Conda运行项目指南

## 🎯 快速开始（3步完成）

### 第1步：安装依赖
```bash
C:\ProgramData\anaconda3\python.exe -m pip install -r requirements.txt
```

### 第2步：验证安装
```bash
C:\ProgramData\anaconda3\python.exe test_installation.py
```

### 第3步：运行测试
```bash
C:\ProgramData\anaconda3\python.exe test_basic.py
```

---

## 📋 详细说明

### 环境信息
- **Python路径**: `C:\ProgramData\anaconda3\python.exe`
- **Python版本**: 3.12.7
- **包管理器**: conda + pip
- **CPU核心数**: 32核

### 已安装的依赖
```
✓ numpy 1.26.4
✓ scipy 1.16.3
✓ pandas 2.2.3
✓ matplotlib 3.10.7
✓ scikit-learn 1.8.0
✓ pulp 3.3.0
```

---

## 🚀 运行示例

### 1. 基础测试（推荐首次运行）
```bash
C:\ProgramData\anaconda3\python.exe test_basic.py
```

**预期输出**:
```
✓ 编码修复已应用
  - loky使用32个CPU核心
  - 警告和异常过滤已启用

============================================================
基础功能测试
============================================================

使用 20 个场景, 2 个阶段

[1/5] 生成场景...          ✓
[2/5] 构建场景树...        ✓
[3/5] 创建合约...          ✓
[4/5] 计算远期价格...      ✓
[5/5] 求解优化模型...      ✓

  ✓ 求解状态: Optimal
  ✓ 期望利润: 5935805.51 kR$

🎉 测试成功！项目运行正常！
```

### 2. 安装验证
```bash
C:\ProgramData\anaconda3\python.exe test_installation.py
```

**预期输出**:
```
✓ 所有测试通过！系统已正确安装。
```

### 3. 简化示例
```bash
C:\ProgramData\anaconda3\python.exe examples\simple_example.py
```

**说明**: 100场景，3阶段，运行时间约1-2分钟

### 4. 完整案例
```bash
C:\ProgramData\anaconda3\python.exe examples\case_study.py
```

**说明**: 2000场景，4阶段，运行时间约5-10分钟

---

## 🔧 编码修复说明

### 问题
Windows下运行时出现：
- `UnicodeDecodeError: 'gbk' codec can't decode byte 0x81`
- `UserWarning: Could not find the number of physical cores`

### 解决方案
项目已包含 `fix_encoding.py` 模块，自动修复这些问题。

所有示例程序已自动导入此模块，无需手动操作。

### 修复效果
- ✅ 消除UnicodeDecodeError
- ✅ 消除loky警告
- ✅ 程序运行无异常日志

---

## 📊 测试结果

### 基础测试结果
```
场景数: 20
阶段数: 2
节点数: 3
合约数: 4

求解状态: Optimal
期望利润: 5,935,805.51 kR$ (5,935.81 MR$)
求解时间: 0.02秒
```

### 功能验证
- ✅ 场景生成
- ✅ 场景树构建
- ✅ 远期定价
- ✅ 优化求解
- ✅ 风险度量

---

## 💡 使用技巧

### 1. 创建快捷方式
为了方便使用，可以创建批处理文件：

**test.bat**:
```batch
@echo off
C:\ProgramData\anaconda3\python.exe test_basic.py
pause
```

**run.bat**:
```batch
@echo off
C:\ProgramData\anaconda3\python.exe examples\case_study.py
pause
```

### 2. 使用conda环境
如果想使用特定的conda环境：

```bash
# 激活环境
conda activate your_env_name

# 运行程序
python test_basic.py
```

### 3. 修改参数
编辑 `test_basic.py` 或示例文件，修改参数：

```python
num_scenarios = 50  # 改为50个场景
num_stages = 3      # 改为3个阶段
```

---

## 📁 项目文件说明

### 核心代码
```
src/
├── data_generation.py    # 场景生成
├── scenario_tree.py      # 场景树构建
├── forward_pricing.py    # 远期定价
├── risk_measures.py      # 风险度量
├── optimization.py       # 优化模型
└── utils.py              # 工具函数
```

### 测试和示例
```
test_installation.py      # 安装测试
test_basic.py            # 基础功能测试
examples/
├── simple_example.py    # 简化示例
└── case_study.py        # 完整案例
```

### 辅助文件
```
fix_encoding.py          # 编码修复模块
requirements.txt         # 依赖列表
```

---

## ⚠️ 注意事项

### 1. Python路径
确保使用正确的Python路径：
```bash
C:\ProgramData\anaconda3\python.exe
```

如果路径不同，请替换为你的实际路径。

### 2. 求解时间
- 基础测试: < 1分钟
- 简化示例: 1-2分钟
- 完整案例: 5-10分钟

### 3. 内存需求
- 基础测试: < 500MB
- 简化示例: < 1GB
- 完整案例: < 2GB

---

## 🐛 问题排查

### 问题1: 找不到模块
**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
C:\ProgramData\anaconda3\python.exe -m pip install xxx
```

### 问题2: 求解失败
**错误**: `Status: Infeasible`

**原因**: 风险约束过严

**解决**: 放松风险约束或增加场景数

### 问题3: 运行缓慢
**原因**: 场景数或阶段数过多

**解决**: 减少场景数或阶段数

---

## 📚 更多资源

- **项目说明**: `项目说明.md`
- **快速开始**: `快速开始.md`
- **测试报告**: `测试报告.md`
- **完整文档**: `README.md`

---

## ✅ 检查清单

使用前请确认：

- [ ] Python已安装（版本 >= 3.7）
- [ ] 依赖包已安装
- [ ] 测试脚本运行成功
- [ ] 基础测试通过
- [ ] 理解了基本用法

---

## 🎉 总结

使用conda运行项目非常简单：

1. **安装依赖**: `pip install -r requirements.txt`
2. **运行测试**: `python test_basic.py`
3. **查看结果**: 期望利润约5.9 MR$

所有功能已验证通过，可以放心使用！

**祝使用愉快！** 🎊

