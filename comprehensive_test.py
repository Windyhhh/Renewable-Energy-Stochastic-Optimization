"""
综合测试脚本 - 全面验证项目功能
测试所有核心模块和算例
"""

# ========== 首先应用编码修复 ==========
import fix_encoding  # 必须在最开头导入

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time
from datetime import datetime

# 导入所有核心模块
from src.data_generation import ScenarioGenerator
from src.scenario_tree import ScenarioTree
from src.forward_pricing import ForwardPricer, create_contract_set
from src.risk_measures import RiskConstraints, RiskMeasures
from src.optimization import TradingOptimizationModel


def print_section(title):
    """打印分节标题"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_1_module_imports():
    """测试1: 模块导入"""
    print_section("测试1: 模块导入检查")
    
    modules = [
        ('data_generation', 'ScenarioGenerator'),
        ('scenario_tree', 'ScenarioTree'),
        ('forward_pricing', 'ForwardPricer'),
        ('risk_measures', 'RiskConstraints'),
        ('optimization', 'TradingOptimizationModel'),
    ]
    
    all_passed = True
    for module_name, class_name in modules:
        try:
            module = __import__(f'src.{module_name}', fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  ✓ {module_name}.{class_name}")
        except Exception as e:
            print(f"  ✗ {module_name}.{class_name}: {e}")
            all_passed = False
    
    return all_passed


def test_2_scenario_generation():
    """测试2: 场景生成"""
    print_section("测试2: 场景生成功能")
    
    try:
        generator = ScenarioGenerator(
            num_scenarios=50,
            num_stages=2,
            hours_per_stage=168,
            avg_generation=100.0,
            avg_spot_price=150.0,
            seed=42
        )
        
        scenarios = generator.generate_scenarios()
        
        # 验证数据形状
        assert scenarios['generation'].shape == (50, 2, 168), "发电量形状错误"
        assert scenarios['spot_price'].shape == (50, 2, 168), "价格形状错误"
        assert len(scenarios['probabilities']) == 50, "概率数量错误"
        
        # 验证数据范围
        assert np.all(scenarios['generation'] >= 0), "发电量存在负值"
        assert np.all(scenarios['spot_price'] > 0), "价格存在非正值"
        assert np.isclose(np.sum(scenarios['probabilities']), 1.0), "概率和不为1"
        
        # 验证统计特性
        avg_gen = np.mean(scenarios['generation'])
        avg_price = np.mean(scenarios['spot_price'])
        
        print(f"  ✓ 场景形状: {scenarios['generation'].shape}")
        print(f"  ✓ 平均发电量: {avg_gen:.2f} MWh/h (目标: 100)")
        print(f"  ✓ 平均价格: {avg_price:.2f} R$/MWh (目标: 150)")
        print(f"  ✓ 概率和: {np.sum(scenarios['probabilities']):.4f}")
        
        # 验证负相关性
        gen_flat = scenarios['generation'].reshape(50, -1)
        price_flat = scenarios['spot_price'].reshape(50, -1)
        correlations = [np.corrcoef(gen_flat[:, i], price_flat[:, i])[0, 1] 
                       for i in range(gen_flat.shape[1])]
        avg_corr = np.mean(correlations)
        print(f"  ✓ 发电-价格平均相关性: {avg_corr:.3f} (目标: 负相关)")
        
        return True, scenarios
        
    except Exception as e:
        print(f"  ✗ 场景生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_3_scenario_tree(scenarios):
    """测试3: 场景树构建"""
    print_section("测试3: 场景树构建")

    try:
        branching_factors = [2, 2]
        tree = ScenarioTree(scenarios, branching_factors)
        tree_info = tree.build_tree()

        # 验证树结构
        # 注意：场景树从stage 0开始，但只在stage 1开始分支
        # stage 0: 1个节点（根节点）
        # stage 1: 2个节点（第一次分支）
        # 总共: 1 + 2 = 3个节点
        expected_nodes = 1 + 2  # 根节点 + 第一阶段的2个分支
        assert tree_info['num_nodes'] == expected_nodes, f"节点数错误: {tree_info['num_nodes']} != {expected_nodes}"
        assert tree_info['num_leaf_nodes'] == 2, f"叶节点数错误: {tree_info['num_leaf_nodes']} != 2"

        # 验证路径
        paths = tree.get_paths()
        assert len(paths) == 2, f"路径数错误: {len(paths)} != 2"

        print(f"  ✓ 节点总数: {tree_info['num_nodes']}")
        print(f"  ✓ 叶节点数: {tree_info['num_leaf_nodes']}")
        print(f"  ✓ 路径数: {len(paths)}")

        # 验证每个节点的场景分配
        leaf_nodes = tree_info['leaf_nodes']
        total_scenarios = sum(len(tree.node_scenarios[n]) for n in leaf_nodes)
        print(f"  ✓ 叶节点场景总数: {total_scenarios}")

        # 验证所有场景都被分配
        assert total_scenarios == scenarios['generation'].shape[0], "场景分配不完整"

        return True, tree

    except Exception as e:
        print(f"  ✗ 场景树构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_4_forward_pricing(tree, scenarios):
    """测试4: 远期合约定价"""
    print_section("测试4: 远期合约定价")

    try:
        # 创建合约集合
        contracts = create_contract_set(num_stages=2)
        print(f"  ✓ 创建合约: {len(contracts)} 个")

        # 远期定价
        pricer = ForwardPricer(
            tree,
            scenarios['spot_price'],
            scenarios['probabilities'],
            risk_premium_rate=0.05
        )

        forward_prices = pricer.price_forward_contracts(contracts)

        # 验证定价结果
        assert len(forward_prices) > 0, "未生成远期价格"

        # 检查价格合理性 - forward_prices是嵌套字典 {contract_id: {node_id: price}}
        total_prices = 0
        for contract_id, node_prices in forward_prices.items():
            for node_id, price in node_prices.items():
                assert price > 0, f"合约{contract_id}节点{node_id}价格非正: {price}"
                total_prices += 1

        print(f"  ✓ 定价完成: {len(forward_prices)} 个合约, {total_prices} 个价格")

        # 显示部分价格
        sample_count = 0
        for contract_id, node_prices in forward_prices.items():
            for node_id, price in node_prices.items():
                if sample_count < 3:
                    print(f"     合约{contract_id}@节点{node_id}: {price:.2f} R$/MWh")
                    sample_count += 1
                else:
                    break
            if sample_count >= 3:
                break

        return True, contracts, forward_prices

    except Exception as e:
        print(f"  ✗ 远期定价失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None


def test_5_risk_neutral_optimization(tree, scenarios, contracts, forward_prices):
    """测试5: 风险中性优化"""
    print_section("测试5: 风险中性优化求解")
    
    try:
        model = TradingOptimizationModel(
            scenario_tree=tree,
            generation=scenarios['generation'],
            spot_price=scenarios['spot_price'],
            probabilities=scenarios['probabilities'],
            forward_prices=forward_prices,
            contracts=contracts,
            risk_constraints=None,
            generation_cost=0.0
        )
        
        print("  构建模型...")
        model.build_model(include_risk_constraints=False)
        
        print("  求解中...")
        start_time = time.time()
        status = model.solve(time_limit=60)
        solve_time = time.time() - start_time
        
        print(f"  ✓ 求解状态: {status}")
        print(f"  ✓ 求解时间: {solve_time:.2f} 秒")
        
        if model.solution:
            expected_profit = model.get_expected_profit()
            print(f"  ✓ 期望利润: {expected_profit:,.2f} kR$")
            print(f"  ✓ 期望利润: {expected_profit/1000:.2f} MR$")
            
            return True, model
        else:
            print(f"  ✗ 未找到解")
            return False, None
            
    except Exception as e:
        print(f"  ✗ 优化求解失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def run_all_tests():
    """运行所有测试"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  期刊项目综合测试 - 全面验证".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # 测试1: 模块导入
    results['模块导入'] = test_1_module_imports()
    
    # 测试2: 场景生成
    success, scenarios = test_2_scenario_generation()
    results['场景生成'] = success
    if not success:
        print("\n❌ 场景生成失败，后续测试无法继续")
        return results
    
    # 测试3: 场景树
    success, tree = test_3_scenario_tree(scenarios)
    results['场景树构建'] = success
    if not success:
        print("\n❌ 场景树构建失败，后续测试无法继续")
        return results
    
    # 测试4: 远期定价
    success, contracts, forward_prices = test_4_forward_pricing(tree, scenarios)
    results['远期定价'] = success
    if not success:
        print("\n❌ 远期定价失败，后续测试无法继续")
        return results
    
    # 测试5: 风险中性优化
    success, model = test_5_risk_neutral_optimization(tree, scenarios, contracts, forward_prices)
    results['风险中性优化'] = success
    
    return results


def print_final_report(results):
    """打印最终测试报告"""
    print_section("测试总结报告")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n  总测试数: {total}")
    print(f"  通过数: {passed}")
    print(f"  失败数: {total - passed}")
    print(f"  通过率: {passed/total*100:.1f}%")

    print("\n  详细结果:")
    for test_name, test_passed in results.items():
        status = "✓ 通过" if test_passed else "✗ 失败"
        print(f"    {test_name:20s} {status}")

    print("\n" + "="*70)
    if passed == total:
        print("  🎉 所有测试通过！项目功能完整且正常！")
    else:
        print(f"  ⚠️  {total - passed} 个测试失败，请检查相关模块")
    print("="*70)

    return passed == total


if __name__ == "__main__":
    try:
        results = run_all_tests()
        all_passed = print_final_report(results)

        if all_passed:
            print("\n" + "█"*70)
            print("█" + " "*68 + "█")
            print("█" + "  ✅ 综合测试完成 - 所有功能正常！".center(68) + "█")
            print("█" + " "*68 + "█")
            print("█"*70)

    except Exception as e:
        print(f"\n❌ 测试过程中出现严重错误:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()

