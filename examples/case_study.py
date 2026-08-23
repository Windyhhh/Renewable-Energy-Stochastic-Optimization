"""
案例研究主程序
复现期刊中的巴西电力市场案例
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
from src.risk_measures import RiskConstraints, RiskMeasures
from src.optimization import TradingOptimizationModel
from src.utils import plot_generation_and_price, plot_scenario_tree, print_summary_statistics, save_results


def main():
    """主函数"""
    print("="*60)
    print("可再生能源交易多阶段随机优化模型")
    print("="*60)
    
    # ========== 1. 参数设置 ==========
    print("\n[1/7] 设置参数...")
    
    # 基本参数
    num_scenarios = 2000  # 场景数
    num_stages = 4  # 阶段数（4周）
    hours_per_stage = 168  # 每周168小时
    
    # 发电机参数（160MW风电场）
    avg_generation = 100.0  # 平均发电量 MWh/h (100 avgMW)
    generation_cost = 0.0  # 单位可变成本（风电为0）
    
    # 市场参数
    avg_spot_price = 150.0  # 平均现货价格 R$/MWh
    risk_premium_rate = 0.05  # 风险溢价率 5%
    
    # 风险约束参数
    alpha = 0.9  # CVaR置信水平 90%
    weekly_cvar_min = 500.0  # 周度CVaR最小值 500 kR$
    monthly_cvar_min = 3000.0  # 月度CVaR最小值 3000 kR$
    max_drawdown = 300.0  # 最大单期回撤 300 kR$
    
    # 场景树分支因子
    branching_factors = [2, 2, 2, 2]  # 每阶段2个分支
    
    print(f"  - 场景数: {num_scenarios}")
    print(f"  - 阶段数: {num_stages} 周")
    print(f"  - 平均发电量: {avg_generation} MWh/h")
    print(f"  - CVaR置信水平: {alpha*100}%")
    
    # ========== 2. 生成场景 ==========
    print("\n[2/7] 生成场景数据...")
    
    generator = ScenarioGenerator(
        num_scenarios=num_scenarios,
        num_stages=num_stages,
        hours_per_stage=hours_per_stage,
        avg_generation=avg_generation,
        avg_spot_price=avg_spot_price,
        seed=42
    )
    
    scenarios = generator.generate_scenarios()
    
    print(f"  - 发电量场景形状: {scenarios['generation'].shape}")
    print(f"  - 现货价格场景形状: {scenarios['spot_price'].shape}")
    print(f"  - 平均发电量: {np.mean(scenarios['generation']):.2f} MWh/h")
    print(f"  - 平均现货价格: {np.mean(scenarios['spot_price']):.2f} R$/MWh")
    
    # ========== 3. 构建场景树 ==========
    print("\n[3/7] 构建场景树...")
    
    tree = ScenarioTree(scenarios, branching_factors)
    tree_info = tree.build_tree()
    
    print(f"  - 节点总数: {tree_info['num_nodes']}")
    print(f"  - 叶节点数: {tree_info['num_leaf_nodes']}")
    print(f"  - 路径数: {len(tree.get_paths())}")
    
    # ========== 4. 创建合约集合 ==========
    print("\n[4/7] 创建远期合约集合...")
    
    contracts = create_contract_set(num_stages)
    print(f"  - 合约总数: {len(contracts)}")
    
    # ========== 5. 远期定价 ==========
    print("\n[5/7] 计算远期价格...")
    
    pricer = ForwardPricer(
        tree,
        scenarios['spot_price'],
        scenarios['probabilities'],
        risk_premium_rate
    )
    
    forward_prices = pricer.price_forward_contracts(contracts)
    
    # 打印部分远期价格
    sample_contract = contracts[0]
    sample_node = 0
    if sample_contract['id'] in forward_prices and sample_node in forward_prices[sample_contract['id']]:
        print(f"  - 示例：合约{sample_contract['id']}在节点{sample_node}的价格: "
              f"{forward_prices[sample_contract['id']][sample_node]:.2f} R$/MWh")
    
    # ========== 6. 构建并求解优化模型 ==========
    print("\n[6/7] 构建并求解优化模型...")
    
    # 创建风险约束
    risk_constraints = RiskConstraints(
        alpha=alpha,
        weekly_cvar_min=weekly_cvar_min,
        monthly_cvar_min=monthly_cvar_min,
        max_drawdown=max_drawdown
    )
    
    # 创建优化模型
    model = TradingOptimizationModel(
        scenario_tree=tree,
        generation=scenarios['generation'],
        spot_price=scenarios['spot_price'],
        probabilities=scenarios['probabilities'],
        forward_prices=forward_prices,
        contracts=contracts,
        risk_constraints=risk_constraints,
        generation_cost=generation_cost
    )
    
    # 构建模型
    print("  - 构建优化模型...")
    model.build_model(include_risk_constraints=True)
    
    # 求解模型
    print("  - 求解优化模型（这可能需要几分钟）...")
    status = model.solve(time_limit=300)
    
    print(f"  - 求解状态: {status}")
    
    # ========== 7. 分析结果 ==========
    print("\n[7/7] 分析结果...")
    
    if model.solution is not None:
        # 打印汇总统计
        print_summary_statistics(model.solution, scenarios['probabilities'])
        
        # 保存结果
        os.makedirs('results', exist_ok=True)
        save_results(model.solution, 'results/optimization_results.json')
        print("\n结果已保存到: results/optimization_results.json")
        
        # 可视化
        print("\n生成可视化图表...")
        plot_generation_and_price(
            scenarios['generation'],
            scenarios['spot_price'],
            num_scenarios_to_plot=10,
            save_path='results/generation_and_price.png'
        )
        
        plot_scenario_tree(tree, save_path='results/scenario_tree.png')
        
        print("图表已保存到 results/ 目录")
    else:
        print("\n警告: 未找到可行解")
    
    print("\n" + "="*60)
    print("案例研究完成！")
    print("="*60)


if __name__ == "__main__":
    main()

