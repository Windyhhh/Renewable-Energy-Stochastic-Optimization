"""
多阶段随机优化模型
使用线性规划求解器实现核心优化模型
"""

import numpy as np
from pulp import *
from typing import Dict, List, Tuple
from src.risk_measures import RiskConstraints


class TradingOptimizationModel:
    """交易优化模型"""
    
    def __init__(self,
                 scenario_tree,
                 generation: np.ndarray,
                 spot_price: np.ndarray,
                 probabilities: np.ndarray,
                 forward_prices: Dict[int, Dict[int, float]],
                 contracts: List[Dict],
                 risk_constraints: RiskConstraints = None,
                 generation_cost: float = 0.0):
        """
        初始化优化模型
        
        参数:
            scenario_tree: 场景树对象
            generation: 发电量场景 [S, T, H]
            spot_price: 现货价格场景 [S, T, H]
            probabilities: 场景概率 [S]
            forward_prices: 远期价格 {contract_id: {node_id: price}}
            contracts: 合约列表
            risk_constraints: 风险约束对象
            generation_cost: 单位发电成本
        """
        self.tree = scenario_tree
        self.generation = generation
        self.spot_price = spot_price
        self.probabilities = probabilities
        self.forward_prices = forward_prices
        self.contracts = contracts
        self.risk_constraints = risk_constraints
        self.generation_cost = generation_cost
        
        self.num_scenarios = generation.shape[0]
        self.num_stages = generation.shape[1]
        self.hours_per_stage = generation.shape[2]
        
        # 优化模型
        self.model = None
        self.variables = {}
        self.solution = None
        
    def build_model(self, include_risk_constraints: bool = True):
        """构建优化模型"""
        self.model = LpProblem("Energy_Trading_Optimization", LpMaximize)
        
        # 创建决策变量
        self._create_variables()
        
        # 设置目标函数
        self._set_objective()
        
        # 添加约束
        self._add_profit_constraints()
        self._add_energy_balance_constraints()
        self._add_non_anticipativity_constraints()
        
        if include_risk_constraints and self.risk_constraints is not None:
            self._add_risk_constraints()
    
    def _create_variables(self):
        """创建决策变量"""
        # x_{c,n}: 合约签约比例 [0, 1]
        self.variables['x'] = {}
        for contract in self.contracts:
            c_id = contract['id']
            dec_stage = contract['decision_stage']
            
            for node in self.tree.nodes:
                if node['stage'] == dec_stage:
                    n_id = node['id']
                    var_name = f"x_c{c_id}_n{n_id}"
                    self.variables['x'][(c_id, n_id)] = LpVariable(
                        var_name, lowBound=0, upBound=1
                    )
        
        # r_{s,t}: 场景s阶段t的净收入
        self.variables['r'] = {}
        for s in range(self.num_scenarios):
            for t in range(self.num_stages):
                var_name = f"r_s{s}_t{t}"
                self.variables['r'][(s, t)] = LpVariable(var_name)
        
        # e_{s,t}^{lg}: 多头头寸（现货市场卖出）
        self.variables['e_lg'] = {}
        for s in range(self.num_scenarios):
            for t in range(self.num_stages):
                var_name = f"e_lg_s{s}_t{t}"
                self.variables['e_lg'][(s, t)] = LpVariable(
                    var_name, lowBound=0
                )
        
        # e_{s,t}^{sh}: 空头头寸（现货市场买入）
        self.variables['e_sh'] = {}
        for s in range(self.num_scenarios):
            for t in range(self.num_stages):
                var_name = f"e_sh_s{s}_t{t}"
                self.variables['e_sh'][(s, t)] = LpVariable(
                    var_name, lowBound=0
                )
        
        # CVaR辅助变量
        if self.risk_constraints is not None:
            self._create_cvar_variables()
    
    def _create_cvar_variables(self):
        """创建CVaR计算的辅助变量"""
        # z_n: VaR变量（每个节点）
        self.variables['z_weekly'] = {}
        for node in self.tree.nodes:
            n_id = node['id']
            var_name = f"z_weekly_n{n_id}"
            self.variables['z_weekly'][n_id] = LpVariable(var_name)
        
        # delta_{s,n}: 左偏离变量（周度）
        self.variables['delta_weekly'] = {}
        for s in range(self.num_scenarios):
            for node in self.tree.nodes:
                n_id = node['id']
                var_name = f"delta_weekly_s{s}_n{n_id}"
                self.variables['delta_weekly'][(s, n_id)] = LpVariable(
                    var_name, lowBound=0
                )
        
        # 月度CVaR变量（叶节点）
        leaf_nodes = [n['id'] for n in self.tree.nodes 
                     if len(self.tree.node_children[n['id']]) == 0]
        
        self.variables['z_monthly'] = {}
        for leaf_id in leaf_nodes:
            var_name = f"z_monthly_l{leaf_id}"
            self.variables['z_monthly'][leaf_id] = LpVariable(var_name)
        
        self.variables['delta_monthly'] = {}
        for s in range(self.num_scenarios):
            for leaf_id in leaf_nodes:
                var_name = f"delta_monthly_s{s}_l{leaf_id}"
                self.variables['delta_monthly'][(s, leaf_id)] = LpVariable(
                    var_name, lowBound=0
                )

    def _set_objective(self):
        """设置目标函数：最大化期望利润"""
        objective = lpSum([
            self.probabilities[s] * self.variables['r'][(s, t)]
            for s in range(self.num_scenarios)
            for t in range(self.num_stages)
        ])

        self.model += objective

    def _add_profit_constraints(self):
        """添加利润计算约束"""
        for s in range(self.num_scenarios):
            for t in range(self.num_stages):
                # 计算该场景该阶段的平均现货价格
                avg_spot = np.mean(self.spot_price[s, t, :])

                # 计算该场景该阶段的总发电量
                total_gen = np.sum(self.generation[s, t, :])

                # 现货市场收入
                spot_revenue = avg_spot * (
                    self.variables['e_lg'][(s, t)] - self.variables['e_sh'][(s, t)]
                )

                # 合约收入/成本
                contract_revenue = 0
                for contract in self.contracts:
                    c_id = contract['id']

                    # 检查合约是否在该阶段交割
                    if contract['delivery_start'] <= t <= contract['delivery_end']:
                        # 找到该场景在决策阶段所属的节点
                        node_id = self._get_scenario_node(s, contract['decision_stage'])

                        if node_id is not None and (c_id, node_id) in self.variables['x']:
                            # 合约量（假设每小时均匀交割）
                            contract_quantity = self.variables['x'][(c_id, node_id)] * total_gen

                            # 合约价格
                            if node_id in self.forward_prices[c_id]:
                                contract_price = self.forward_prices[c_id][node_id]

                                if contract['type'] == 'sell':
                                    contract_revenue += contract_price * contract_quantity
                                else:
                                    contract_revenue -= contract_price * contract_quantity

                # 发电成本
                gen_cost = self.generation_cost * total_gen

                # 利润 = 现货收入 + 合约收入 - 发电成本
                self.model += (
                    self.variables['r'][(s, t)] ==
                    spot_revenue + contract_revenue - gen_cost,
                    f"profit_s{s}_t{t}"
                )

    def _add_energy_balance_constraints(self):
        """添加能源平衡约束"""
        for s in range(self.num_scenarios):
            for t in range(self.num_stages):
                total_gen = np.sum(self.generation[s, t, :])

                # 计算合约总量
                contract_sell = 0
                contract_buy = 0

                for contract in self.contracts:
                    c_id = contract['id']

                    if contract['delivery_start'] <= t <= contract['delivery_end']:
                        node_id = self._get_scenario_node(s, contract['decision_stage'])

                        if node_id is not None and (c_id, node_id) in self.variables['x']:
                            contract_quantity = self.variables['x'][(c_id, node_id)] * total_gen

                            if contract['type'] == 'sell':
                                contract_sell += contract_quantity
                            else:
                                contract_buy += contract_quantity

                # 能源平衡：发电 + 合约买入 + 现货买入 = 合约卖出 + 现货卖出
                self.model += (
                    total_gen + contract_buy + self.variables['e_sh'][(s, t)] ==
                    contract_sell + self.variables['e_lg'][(s, t)],
                    f"energy_balance_s{s}_t{t}"
                )

    def _add_non_anticipativity_constraints(self):
        """添加非预见性约束（同一节点的场景使用相同决策）"""
        # 这已经通过变量定义实现：
        # x_{c,n} 对节点n中的所有场景都是相同的
        pass

    def _add_risk_constraints(self):
        """添加风险约束"""
        if self.risk_constraints is None:
            return

        alpha = self.risk_constraints.alpha

        # 1. 周度CVaR约束
        for node in self.tree.nodes:
            n_id = node['id']
            t = node['stage']
            scenarios = self.tree.node_scenarios[n_id]

            # CVaR约束
            cvar_expr = self.variables['z_weekly'][n_id] - \
                       (1.0 / (1.0 - alpha)) * lpSum([
                           self.probabilities[s] * self.variables['delta_weekly'][(s, n_id)]
                           for s in scenarios
                       ]) / self.tree.get_node_probability(n_id)

            self.model += (
                cvar_expr >= self.risk_constraints.weekly_cvar_min,
                f"weekly_cvar_n{n_id}"
            )

            # delta约束
            for s in scenarios:
                self.model += (
                    self.variables['delta_weekly'][(s, n_id)] >=
                    self.variables['z_weekly'][n_id] - self.variables['r'][(s, t)],
                    f"delta_weekly_s{s}_n{n_id}"
                )

        # 2. 月度CVaR约束（基于路径）
        paths = self.tree.get_paths()
        leaf_nodes = [n['id'] for n in self.tree.nodes
                     if len(self.tree.node_children[n['id']]) == 0]

        for leaf_id in leaf_nodes:
            # 找到通向该叶节点的路径
            path = None
            for p in paths:
                if p[-1] == leaf_id:
                    path = p
                    break

            if path is None:
                continue

            # 获取该路径的场景
            scenarios = self.tree.node_scenarios[leaf_id]

            # 月度CVaR约束
            cvar_expr = self.variables['z_monthly'][leaf_id] - \
                       (1.0 / (1.0 - alpha)) * lpSum([
                           self.probabilities[s] * self.variables['delta_monthly'][(s, leaf_id)]
                           for s in scenarios
                       ]) / self.tree.get_node_probability(leaf_id)

            self.model += (
                cvar_expr >= self.risk_constraints.monthly_cvar_min,
                f"monthly_cvar_l{leaf_id}"
            )

            # delta约束（基于整月利润）
            for s in scenarios:
                # 计算该场景的总利润
                total_profit = lpSum([
                    self.variables['r'][(s, t)]
                    for t in range(self.num_stages)
                ])

                self.model += (
                    self.variables['delta_monthly'][(s, leaf_id)] >=
                    self.variables['z_monthly'][leaf_id] - total_profit,
                    f"delta_monthly_s{s}_l{leaf_id}"
                )

        # 3. 单期最大回撤约束
        for s in range(self.num_scenarios):
            for t in range(1, self.num_stages):
                self.model += (
                    self.variables['r'][(s, t-1)] - self.variables['r'][(s, t)] <=
                    self.risk_constraints.max_drawdown,
                    f"drawdown_s{s}_t{t}"
                )

    def _get_scenario_node(self, scenario_id: int, stage: int) -> int:
        """获取场景在特定阶段所属的节点"""
        for node in self.tree.nodes:
            if node['stage'] == stage:
                if scenario_id in self.tree.node_scenarios[node['id']]:
                    return node['id']
        return None

    def solve(self, solver_name: str = 'PULP_CBC_CMD', time_limit: int = 300):
        """
        求解优化模型

        参数:
            solver_name: 求解器名称
            time_limit: 时间限制（秒）

        返回:
            求解状态
        """
        if self.model is None:
            raise ValueError("模型未构建，请先调用 build_model()")

        # 选择求解器
        if solver_name == 'PULP_CBC_CMD':
            solver = PULP_CBC_CMD(timeLimit=time_limit, msg=1)
        else:
            solver = None

        # 求解
        status = self.model.solve(solver)

        # 提取解
        if status == LpStatusOptimal:
            self.solution = self._extract_solution()

        return LpStatus[status]

    def _extract_solution(self) -> Dict:
        """提取优化解"""
        solution = {
            'status': 'Optimal',
            'objective_value': value(self.model.objective),
            'contract_decisions': {},
            'profits': {},
            'spot_positions': {}
        }

        # 提取合约决策
        for (c_id, n_id), var in self.variables['x'].items():
            if var.varValue is not None:
                if c_id not in solution['contract_decisions']:
                    solution['contract_decisions'][c_id] = {}
                solution['contract_decisions'][c_id][n_id] = var.varValue

        # 提取利润
        for (s, t), var in self.variables['r'].items():
            if var.varValue is not None:
                if s not in solution['profits']:
                    solution['profits'][s] = {}
                solution['profits'][s][t] = var.varValue

        # 提取现货头寸
        for (s, t), var in self.variables['e_lg'].items():
            if var.varValue is not None:
                if s not in solution['spot_positions']:
                    solution['spot_positions'][s] = {}
                solution['spot_positions'][s][t] = {
                    'long': var.varValue,
                    'short': self.variables['e_sh'][(s, t)].varValue
                }

        return solution

    def get_expected_profit(self) -> float:
        """获取期望利润"""
        if self.solution is None:
            return None
        return self.solution['objective_value']

    def get_contract_strategy(self) -> Dict:
        """获取合约策略"""
        if self.solution is None:
            return None
        return self.solution['contract_decisions']

