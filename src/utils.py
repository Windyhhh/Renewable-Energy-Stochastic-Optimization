"""
工具函数模块
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List
import json


def save_results(results: Dict, filename: str):
    """保存结果到JSON文件"""
    # 转换numpy数组为列表
    def convert_to_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        else:
            return obj
    
    serializable_results = convert_to_serializable(results)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(serializable_results, f, indent=2, ensure_ascii=False)


def load_results(filename: str) -> Dict:
    """从JSON文件加载结果"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def plot_generation_and_price(generation: np.ndarray, 
                              spot_price: np.ndarray,
                              num_scenarios_to_plot: int = 5,
                              save_path: str = None):
    """
    绘制发电量和现货价格
    
    参数:
        generation: 发电量场景 [S, T, H]
        spot_price: 现货价格场景 [S, T, H]
        num_scenarios_to_plot: 要绘制的场景数
        save_path: 保存路径
    """
    S, T, H = generation.shape
    
    # 计算每个阶段的平均值
    avg_gen_per_stage = np.mean(generation, axis=2)  # [S, T]
    avg_price_per_stage = np.mean(spot_price, axis=2)  # [S, T]
    
    # 计算期望值
    expected_gen = np.mean(avg_gen_per_stage, axis=0)
    expected_price = np.mean(avg_price_per_stage, axis=0)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # 绘制发电量
    stages = list(range(T))
    
    # 绘制部分场景
    for s in range(min(num_scenarios_to_plot, S)):
        ax1.plot(stages, avg_gen_per_stage[s, :], alpha=0.3, color='blue')
    
    # 绘制期望值
    ax1.plot(stages, expected_gen, 'b-', linewidth=2, label='期望发电量')
    ax1.set_xlabel('阶段（周）')
    ax1.set_ylabel('发电量 (MWh/h)')
    ax1.set_title('可再生能源发电量')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 绘制现货价格
    for s in range(min(num_scenarios_to_plot, S)):
        ax2.plot(stages, avg_price_per_stage[s, :], alpha=0.3, color='red')
    
    ax2.plot(stages, expected_price, 'r-', linewidth=2, label='期望现货价格')
    ax2.set_xlabel('阶段（周）')
    ax2.set_ylabel('价格 (R$/MWh)')
    ax2.set_title('现货价格')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_scenario_tree(tree, save_path: str = None):
    """
    可视化场景树结构
    
    参数:
        tree: 场景树对象
        save_path: 保存路径
    """
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 计算节点位置
    stages = {}
    for node in tree.nodes:
        stage = node['stage']
        if stage not in stages:
            stages[stage] = []
        stages[stage].append(node['id'])
    
    positions = {}
    for stage, node_ids in stages.items():
        num_nodes = len(node_ids)
        for i, node_id in enumerate(node_ids):
            x = stage
            y = (i - num_nodes / 2) * 2
            positions[node_id] = (x, y)
    
    # 绘制边
    for node_id, children in tree.node_children.items():
        for child_id in children:
            x1, y1 = positions[node_id]
            x2, y2 = positions[child_id]
            ax.plot([x1, x2], [y1, y2], 'k-', alpha=0.5)
    
    # 绘制节点
    for node_id, (x, y) in positions.items():
        num_scenarios = len(tree.node_scenarios[node_id])
        ax.scatter(x, y, s=500, c='lightblue', edgecolors='black', zorder=3)
        ax.text(x, y, f'N{node_id}\n({num_scenarios})', 
               ha='center', va='center', fontsize=8)
    
    ax.set_xlabel('阶段（周）', fontsize=12)
    ax.set_ylabel('节点', fontsize=12)
    ax.set_title('场景树结构', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def print_summary_statistics(solution: Dict, probabilities: np.ndarray):
    """
    打印汇总统计信息
    
    参数:
        solution: 优化解
        probabilities: 场景概率
    """
    print("\n" + "="*60)
    print("优化结果汇总")
    print("="*60)
    
    print(f"\n求解状态: {solution['status']}")
    print(f"期望利润: {solution['objective_value']:.2f} kR$")
    
    # 统计合约决策
    print(f"\n合约决策数量: {len(solution['contract_decisions'])}")
    
    print("\n" + "="*60)

