"""
测试脚本：验证安装和基本功能
"""

# ========== 首先应用编码修复 ==========
import fix_encoding  # 必须在最开头导入，修复subprocess编码问题

import sys
import numpy as np

def test_imports():
    """测试所有模块是否可以正常导入"""
    print("测试模块导入...")
    
    try:
        from src.data_generation import ScenarioGenerator
        print("  ✓ data_generation 模块导入成功")
    except Exception as e:
        print(f"  ✗ data_generation 模块导入失败: {e}")
        return False
    
    try:
        from src.scenario_tree import ScenarioTree
        print("  ✓ scenario_tree 模块导入成功")
    except Exception as e:
        print(f"  ✗ scenario_tree 模块导入失败: {e}")
        return False
    
    try:
        from src.forward_pricing import ForwardPricer, create_contract_set
        print("  ✓ forward_pricing 模块导入成功")
    except Exception as e:
        print(f"  ✗ forward_pricing 模块导入失败: {e}")
        return False
    
    try:
        from src.risk_measures import RiskMeasures, RiskConstraints
        print("  ✓ risk_measures 模块导入成功")
    except Exception as e:
        print(f"  ✗ risk_measures 模块导入失败: {e}")
        return False
    
    try:
        from src.optimization import TradingOptimizationModel
        print("  ✓ optimization 模块导入成功")
    except Exception as e:
        print(f"  ✗ optimization 模块导入失败: {e}")
        return False
    
    return True


def test_scenario_generation():
    """测试场景生成功能"""
    print("\n测试场景生成...")
    
    try:
        from src.data_generation import ScenarioGenerator
        
        generator = ScenarioGenerator(
            num_scenarios=10,
            num_stages=2,
            hours_per_stage=24,
            avg_generation=100.0,
            avg_spot_price=150.0,
            seed=42
        )
        
        scenarios = generator.generate_scenarios()
        
        assert scenarios['generation'].shape == (10, 2, 24), "发电量场景形状错误"
        assert scenarios['spot_price'].shape == (10, 2, 24), "现货价格场景形状错误"
        assert len(scenarios['probabilities']) == 10, "概率数组长度错误"
        assert np.isclose(np.sum(scenarios['probabilities']), 1.0), "概率和不为1"
        
        print("  ✓ 场景生成测试通过")
        return True
        
    except Exception as e:
        print(f"  ✗ 场景生成测试失败: {e}")
        return False


def test_scenario_tree():
    """测试场景树构建功能"""
    print("\n测试场景树构建...")
    
    try:
        from src.data_generation import ScenarioGenerator
        from src.scenario_tree import ScenarioTree
        
        generator = ScenarioGenerator(
            num_scenarios=20,
            num_stages=3,
            hours_per_stage=24,
            seed=42
        )
        scenarios = generator.generate_scenarios()
        
        tree = ScenarioTree(scenarios, branching_factors=[2, 2, 2])
        tree_info = tree.build_tree()
        
        assert tree_info['num_nodes'] > 0, "节点数应大于0"
        assert tree_info['num_leaf_nodes'] > 0, "叶节点数应大于0"
        
        print(f"  ✓ 场景树构建测试通过 (节点数: {tree_info['num_nodes']})")
        return True
        
    except Exception as e:
        print(f"  ✗ 场景树构建测试失败: {e}")
        return False


def test_risk_measures():
    """测试风险度量功能"""
    print("\n测试风险度量...")
    
    try:
        from src.risk_measures import RiskMeasures
        
        profits = np.array([100, 200, 150, 50, 300, 80, 120])
        probabilities = np.ones(7) / 7
        
        cvar = RiskMeasures.calculate_cvar(profits, probabilities, alpha=0.9)
        var = RiskMeasures.calculate_var(profits, probabilities, alpha=0.9)
        
        assert cvar <= var, "CVaR应小于等于VaR"
        
        profit_series = np.array([100, 120, 110, 130, 125])
        max_dd, avg_dd = RiskMeasures.calculate_drawdown(profit_series)
        
        assert max_dd >= 0, "最大回撤应非负"
        
        print(f"  ✓ 风险度量测试通过 (CVaR: {cvar:.2f}, VaR: {var:.2f})")
        return True
        
    except Exception as e:
        print(f"  ✗ 风险度量测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("="*60)
    print("可再生能源交易优化模型 - 安装测试")
    print("="*60)
    
    all_passed = True
    
    # 测试导入
    if not test_imports():
        all_passed = False
    
    # 测试场景生成
    if not test_scenario_generation():
        all_passed = False
    
    # 测试场景树
    if not test_scenario_tree():
        all_passed = False
    
    # 测试风险度量
    if not test_risk_measures():
        all_passed = False
    
    # 总结
    print("\n" + "="*60)
    if all_passed:
        print("✓ 所有测试通过！系统已正确安装。")
        print("\n下一步:")
        print("  1. 运行简化示例: python examples/simple_example.py")
        print("  2. 运行完整案例: python examples/case_study.py")
    else:
        print("✗ 部分测试失败，请检查安装。")
        print("\n建议:")
        print("  1. 确保已安装所有依赖: pip install -r requirements.txt")
        print("  2. 检查Python版本 (建议 >= 3.7)")
    print("="*60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

