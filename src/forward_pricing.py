"""
远期合约定价模块
基于现货价格预期和风险溢价计算远期价格
"""

import numpy as np
from typing import Dict, List


class ForwardPricer:
    """远期合约定价器"""
    
    def __init__(self, 
                 scenario_tree,
                 spot_price: np.ndarray,
                 probabilities: np.ndarray,
                 risk_premium_rate: float = 0.05):
        """
        初始化远期定价器
        
        参数:
            scenario_tree: 场景树对象
            spot_price: 现货价格场景 [S, T, H]
            probabilities: 场景概率 [S]
            risk_premium_rate: 风险溢价率
        """
        self.tree = scenario_tree
        self.spot_price = spot_price
        self.probabilities = probabilities
        self.risk_premium_rate = risk_premium_rate
        
    def price_forward_contracts(self, contracts: List[Dict]) -> Dict[int, Dict[int, float]]:
        """
        为所有合约在所有节点定价
        
        参数:
            contracts: 合约列表，每个合约包含:
                - id: 合约ID
                - decision_stage: 决策阶段
                - delivery_start: 交割开始阶段
                - delivery_end: 交割结束阶段
                
        返回:
            forward_prices: {contract_id: {node_id: price}}
        """
        forward_prices = {}
        
        for contract in contracts:
            contract_id = contract['id']
            decision_stage = contract['decision_stage']
            delivery_start = contract['delivery_start']
            delivery_end = contract['delivery_end']
            
            forward_prices[contract_id] = {}
            
            # 为决策阶段的所有节点定价
            for node in self.tree.nodes:
                if node['stage'] == decision_stage:
                    node_id = node['id']
                    price = self._price_contract_at_node(
                        node_id, delivery_start, delivery_end
                    )
                    forward_prices[contract_id][node_id] = price
        
        return forward_prices
    
    def _price_contract_at_node(self, node_id: int, 
                                delivery_start: int, 
                                delivery_end: int) -> float:
        """
        在特定节点为合约定价
        
        参数:
            node_id: 节点ID
            delivery_start: 交割开始阶段
            delivery_end: 交割结束阶段
            
        返回:
            远期价格
        """
        # 获取节点包含的场景
        scenarios = self.tree.node_scenarios[node_id]
        
        # 计算条件期望现货价格
        expected_spot = self._conditional_expected_spot(
            scenarios, delivery_start, delivery_end
        )
        
        # 添加风险溢价
        risk_premium = expected_spot * self.risk_premium_rate
        
        forward_price = expected_spot + risk_premium
        
        return forward_price
    
    def _conditional_expected_spot(self, scenarios: List[int],
                                   delivery_start: int,
                                   delivery_end: int) -> float:
        """
        计算条件期望现货价格
        
        参数:
            scenarios: 场景索引列表
            delivery_start: 交割开始阶段
            delivery_end: 交割结束阶段
            
        返回:
            条件期望现货价格
        """
        # 提取相关场景的概率
        scenario_probs = self.probabilities[scenarios]
        normalized_probs = scenario_probs / np.sum(scenario_probs)
        
        # 计算交割期内的平均现货价格
        total_expected = 0.0
        
        for i, s in enumerate(scenarios):
            # 该场景在交割期内的平均价格
            delivery_prices = []
            for t in range(delivery_start, delivery_end + 1):
                stage_avg_price = np.mean(self.spot_price[s, t, :])
                delivery_prices.append(stage_avg_price)
            
            scenario_avg = np.mean(delivery_prices)
            total_expected += normalized_probs[i] * scenario_avg
        
        return total_expected


def create_contract_set(num_stages: int) -> List[Dict]:
    """
    创建合约集合
    
    参数:
        num_stages: 阶段数
        
    返回:
        合约列表
    """
    contracts = []
    contract_id = 0
    
    # 为每个决策阶段创建合约
    for decision_stage in range(num_stages):
        # 不同交割期的合约
        for delivery_start in range(decision_stage, num_stages):
            for delivery_end in range(delivery_start, num_stages):
                contract = {
                    'id': contract_id,
                    'decision_stage': decision_stage,
                    'delivery_start': delivery_start,
                    'delivery_end': delivery_end,
                    'type': 'sell'  # 默认为销售合约
                }
                contracts.append(contract)
                contract_id += 1
    
    return contracts

