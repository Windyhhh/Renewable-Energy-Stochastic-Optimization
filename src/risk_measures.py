"""
风险度量模块
实现CVaR计算和回撤约束
"""

import numpy as np
from typing import Dict, List, Tuple


class RiskMeasures:
    """风险度量计算器"""
    
    @staticmethod
    def calculate_cvar(profits: np.ndarray, 
                       probabilities: np.ndarray, 
                       alpha: float) -> float:
        """
        计算条件风险价值 (CVaR)
        
        参数:
            profits: 利润数组
            probabilities: 概率数组
            alpha: 置信水平 (例如 0.9 表示 90%)
            
        返回:
            CVaR值
        """
        # 排序利润和对应概率
        sorted_indices = np.argsort(profits)
        sorted_profits = profits[sorted_indices]
        sorted_probs = probabilities[sorted_indices]
        
        # 计算累积概率
        cumulative_prob = np.cumsum(sorted_probs)
        
        # 找到VaR阈值
        var_index = np.searchsorted(cumulative_prob, 1 - alpha)
        
        if var_index >= len(sorted_profits):
            var_index = len(sorted_profits) - 1
        
        # CVaR是VaR以下所有值的加权平均
        if var_index == 0:
            cvar = sorted_profits[0]
        else:
            tail_probs = sorted_probs[:var_index + 1]
            tail_profits = sorted_profits[:var_index + 1]
            
            # 归一化尾部概率
            tail_probs_normalized = tail_probs / np.sum(tail_probs)
            
            cvar = np.sum(tail_probs_normalized * tail_profits)
        
        return cvar
    
    @staticmethod
    def calculate_var(profits: np.ndarray, 
                      probabilities: np.ndarray, 
                      alpha: float) -> float:
        """
        计算风险价值 (VaR)
        
        参数:
            profits: 利润数组
            probabilities: 概率数组
            alpha: 置信水平
            
        返回:
            VaR值
        """
        sorted_indices = np.argsort(profits)
        sorted_profits = profits[sorted_indices]
        sorted_probs = probabilities[sorted_indices]
        
        cumulative_prob = np.cumsum(sorted_probs)
        var_index = np.searchsorted(cumulative_prob, 1 - alpha)
        
        if var_index >= len(sorted_profits):
            var_index = len(sorted_profits) - 1
        
        return sorted_profits[var_index]
    
    @staticmethod
    def calculate_drawdown(profit_series: np.ndarray) -> Tuple[float, float]:
        """
        计算最大回撤
        
        参数:
            profit_series: 时间序列利润
            
        返回:
            (最大回撤, 平均回撤)
        """
        drawdowns = []
        
        for i in range(1, len(profit_series)):
            drawdown = profit_series[i-1] - profit_series[i]
            drawdowns.append(drawdown)
        
        if len(drawdowns) == 0:
            return 0.0, 0.0
        
        max_drawdown = max(drawdowns)
        avg_drawdown = np.mean(drawdowns)
        
        return max_drawdown, avg_drawdown


class RiskConstraints:
    """风险约束管理器"""
    
    def __init__(self, 
                 alpha: float = 0.9,
                 weekly_cvar_min: float = 500.0,  # kR$
                 monthly_cvar_min: float = 3000.0,  # kR$
                 max_drawdown: float = 300.0):  # kR$
        """
        初始化风险约束
        
        参数:
            alpha: CVaR置信水平
            weekly_cvar_min: 周度CVaR最小值 (kR$)
            monthly_cvar_min: 月度CVaR最小值 (kR$)
            max_drawdown: 最大单期回撤 (kR$)
        """
        self.alpha = alpha
        self.weekly_cvar_min = weekly_cvar_min
        self.monthly_cvar_min = monthly_cvar_min
        self.max_drawdown = max_drawdown
    
    def check_weekly_cvar(self, node_profits: Dict[int, np.ndarray],
                         node_probs: Dict[int, np.ndarray]) -> Dict[int, bool]:
        """
        检查周度CVaR约束
        
        参数:
            node_profits: {node_id: profits}
            node_probs: {node_id: probabilities}
            
        返回:
            {node_id: is_satisfied}
        """
        results = {}
        
        for node_id, profits in node_profits.items():
            probs = node_probs[node_id]
            cvar = RiskMeasures.calculate_cvar(profits, probs, self.alpha)
            results[node_id] = (cvar >= self.weekly_cvar_min)
        
        return results
    
    def check_monthly_cvar(self, path_profits: Dict[int, np.ndarray],
                          path_probs: Dict[int, np.ndarray]) -> Dict[int, bool]:
        """
        检查月度CVaR约束
        
        参数:
            path_profits: {path_id: total_profits}
            path_probs: {path_id: probabilities}
            
        返回:
            {path_id: is_satisfied}
        """
        results = {}
        
        for path_id, profits in path_profits.items():
            probs = path_probs[path_id]
            cvar = RiskMeasures.calculate_cvar(profits, probs, self.alpha)
            results[path_id] = (cvar >= self.monthly_cvar_min)
        
        return results

