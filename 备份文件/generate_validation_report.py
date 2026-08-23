"""
生成完整的验证报告
包括基础测试、综合测试和简化示例运行
"""

# ========== 首先应用编码修复 ==========
import fix_encoding

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import subprocess
from datetime import datetime
import json


def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            shell=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        
        return result.returncode == 0, result.stdout
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False, str(e)


def main():
    """主函数"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  期刊项目完整验证报告生成".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    print(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    python_exe = r"C:\ProgramData\anaconda3\python.exe"
    
    results = {}
    
    # 1. 运行基础测试
    success, output = run_command(
        f"{python_exe} test_basic.py",
        "1. 基础功能测试"
    )
    results['基础测试'] = success
    
    # 2. 运行综合测试
    success, output = run_command(
        f"{python_exe} comprehensive_test.py",
        "2. 综合功能测试"
    )
    results['综合测试'] = success
    
    # 3. 运行简化示例
    success, output = run_command(
        f"{python_exe} examples/simple_example.py",
        "3. 简化示例运行"
    )
    results['简化示例'] = success
    
    # 生成总结报告
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  验证报告总结".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n  总测试项: {total}")
    print(f"  通过数: {passed}")
    print(f"  失败数: {total - passed}")
    print(f"  通过率: {passed/total*100:.1f}%")
    
    print("\n  详细结果:")
    for test_name, success in results.items():
        status = "✓ 通过" if success else "✗ 失败"
        print(f"    {test_name:20s} {status}")
    
    print("\n" + "="*70)
    if passed == total:
        print("  🎉 所有验证通过！项目已准备就绪！")
    else:
        print(f"  ⚠️  {total - passed} 项验证失败")
    print("="*70)
    
    # 保存报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'summary': {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'pass_rate': passed/total*100
        }
    }
    
    with open('validation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n  报告已保存到: validation_report.json")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

