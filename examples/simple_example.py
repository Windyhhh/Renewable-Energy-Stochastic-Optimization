"""
简化示例
用于快速测试和理解模型
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ========== 应用编码修复 ==========
import fix_encoding  # 修复subprocess编码问题

import numpy as np
from src.data_generation import ScenarioGenerator
from src.scenario_tree import ScenarioTree
from src.forward_pricing import ForwardPricer, create_contract_set
from src.risk_measures import RiskConstraints
from src.optimization import TradingOptimizationModel


def simple_example():
    """简化示例：使用较少的场景和阶段"""
    
    print("="*60)
    print("简化示例：可再生能源交易优化")
    print("="*60)
    
    # 简化参数
    num_scenarios = 100  # 减少场景数以加快计算
    num_stages = 3  # 3周
    
    print(f"\n使用 {num_scenarios} 个场景, {num_stages} 个阶段")
    
    # 1. 生成场景
    print("\n生成场景...")
    generator = ScenarioGenerator(
        num_scenarios=num_scenarios,
        num_stages=num_stages,
        hours_per_stage=168,
        avg_generation=100.0,
        avg_spot_price=150.0,
        seed=42
    )
    scenarios = generator.generate_scenarios()
    
    # 2. 构建场景树
    print("构建场景树...")
    branching_factors = [2, 2, 2]
    tree = ScenarioTree(scenarios, branching_factors)
    tree_info = tree.build_tree()
    print(f"  节点数: {tree_info['num_nodes']}, 叶节点数: {tree_info['num_leaf_nodes']}")
    
    # 3. 创建合约
    print("创建合约...")
    contracts = create_contract_set(num_stages)
    print(f"  合约数: {len(contracts)}")
    
    # 4. 远期定价
    print("计算远期价格...")
    pricer = ForwardPricer(tree, scenarios['spot_price'], 
                          scenarios['probabilities'], risk_premium_rate=0.05)
    forward_prices = pricer.price_forward_contracts(contracts)
    
    # 5. 风险中性优化（无风险约束）
    print("\n求解风险中性模型...")
    model_neutral = TradingOptimizationModel(
        scenario_tree=tree,
        generation=scenarios['generation'],
        spot_price=scenarios['spot_price'],
        probabilities=scenarios['probabilities'],
        forward_prices=forward_prices,
        contracts=contracts,
        risk_constraints=None,
        generation_cost=0.0
    )
    
    model_neutral.build_model(include_risk_constraints=False)
    status = model_neutral.solve(time_limit=60)
    
    print(f"  状态: {status}")
    if model_neutral.solution:
        print(f"  期望利润: {model_neutral.get_expected_profit():.2f} kR$")
    
    # 6. 风险规避优化（带风险约束）
    print("\n求解风险规避模型...")
    # 放松风险约束以确保可行性
    risk_constraints = RiskConstraints(
        alpha=0.85,  # 降低置信水平
        weekly_cvar_min=50.0,  # 降低周度CVaR阈值
        monthly_cvar_min=200.0,  # 降低月度CVaR阈值
        max_drawdown=5000.0  # 放松回撤约束
    )
    
    model_risk_averse = TradingOptimizationModel(
        scenario_tree=tree,
        generation=scenarios['generation'],
        spot_price=scenarios['spot_price'],
        probabilities=scenarios['probabilities'],
        forward_prices=forward_prices,
        contracts=contracts,
        risk_constraints=risk_constraints,
        generation_cost=0.0
    )
    
    model_risk_averse.build_model(include_risk_constraints=True)
    status = model_risk_averse.solve(time_limit=60)
    
    print(f"  状态: {status}")
    if model_risk_averse.solution:
        print(f"  期望利润: {model_risk_averse.get_expected_profit():.2f} kR$")
    
    # 7. 比较结果
    print("\n" + "="*60)
    print("结果比较")
    print("="*60)
    
    if model_neutral.solution and model_risk_averse.solution:
        profit_neutral = model_neutral.get_expected_profit()
        profit_risk_averse = model_risk_averse.get_expected_profit()
        
        print(f"风险中性策略期望利润:   {profit_neutral:.2f} kR$")
        print(f"风险规避策略期望利润:   {profit_risk_averse:.2f} kR$")
        print(f"差异:                   {profit_neutral - profit_risk_averse:.2f} kR$")
        print(f"差异百分比:             {(profit_neutral - profit_risk_averse)/profit_neutral*100:.2f}%")
        
        print("\n说明:")
        print("- 风险中性策略追求最大期望利润，不考虑风险")
        print("- 风险规避策略在满足风险约束的前提下最大化利润")
        print("- 差异反映了风险管理的成本")
    
    print("\n" + "="*60)
    print("示例完成！")
    print("="*60)


if __name__ == "__main__":
    simple_example()

