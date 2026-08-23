#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键安装项目所有依赖的脚本
自动检查和安装 requirements.txt 中的所有依赖包
"""

import subprocess
import sys
import os
from pathlib import Path


def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ 错误: 需要 Python 3.7 或更高版本")
        sys.exit(1)


def get_requirements_file():
    """获取 requirements.txt 文件路径"""
    # 优先查找脚本所在目录的 requirements.txt
    script_dir = Path(__file__).parent
    req_file = script_dir / "requirements.txt"
    
    if req_file.exists():
        return req_file
    
    # 如果没找到，查找当前工作目录
    cwd_req = Path.cwd() / "requirements.txt"
    if cwd_req.exists():
        return cwd_req
    
    print("✗ 错误: 找不到 requirements.txt 文件")
    sys.exit(1)


def read_requirements(req_file):
    """读取 requirements.txt 文件"""
    try:
        with open(req_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 过滤空行和注释
        packages = [line.strip() for line in lines 
                   if line.strip() and not line.strip().startswith('#')]
        return packages
    except Exception as e:
        print(f"✗ 错误: 无法读取 requirements.txt - {e}")
        sys.exit(1)


def install_packages(packages):
    """安装所有依赖包"""
    if not packages:
        print("✗ 错误: requirements.txt 中没有找到任何依赖包")
        sys.exit(1)
    
    print(f"\n📦 找到 {len(packages)} 个依赖包:")
    for pkg in packages:
        print(f"   - {pkg}")
    
    print("\n⏳ 开始安装依赖包...")
    print("-" * 50)
    
    try:
        # 使用 pip install -r 安装所有依赖
        req_file = get_requirements_file()
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 错误: 安装失败 - {e}")
        return False


def verify_installation(packages):
    """验证安装是否成功"""
    print("\n" + "-" * 50)
    print("✓ 验证安装结果...")

    # 包名映射（处理特殊情况）
    import_map = {
        'scikit-learn': 'sklearn',
        'pillow': 'PIL',
        'pyyaml': 'yaml',
    }

    failed = []
    for pkg in packages:
        # 提取包名（去掉版本号）
        pkg_name = pkg.split('>=')[0].split('==')[0].split('<')[0].split('>')[0].strip()

        # 使用映射表或直接替换 - 为 _
        import_name = import_map.get(pkg_name, pkg_name.replace('-', '_'))

        try:
            __import__(import_name)
            print(f"   ✓ {pkg_name}")
        except ImportError as e:
            print(f"   ✗ {pkg_name} (导入名: {import_name})")
            failed.append(pkg_name)

    return len(failed) == 0, failed


def main():
    """主函数"""
    print("=" * 50)
    print("🚀 项目依赖一键安装脚本")
    print("=" * 50)
    
    # 检查 Python 版本
    check_python_version()
    
    # 获取 requirements.txt
    req_file = get_requirements_file()
    print(f"✓ 找到依赖文件: {req_file}")
    
    # 读取依赖列表
    packages = read_requirements(req_file)
    
    # 安装依赖
    success = install_packages(packages)
    
    if not success:
        print("\n✗ 安装过程中出现错误，请检查网络连接或依赖包名称")
        sys.exit(1)
    
    # 验证安装
    all_ok, failed = verify_installation(packages)
    
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ 所有依赖安装成功！")
        print("=" * 50)
        return 0
    else:
        print(f"⚠️  部分依赖安装失败: {', '.join(failed)}")
        print("=" * 50)
        return 1


if __name__ == "__main__":
    sys.exit(main())

