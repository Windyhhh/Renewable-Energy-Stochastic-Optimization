"""
数据生成模块
生成可再生能源发电量和现货价格的相关场景
"""

import numpy as np
from typing import Tuple, Dict


class ScenarioGenerator:
    """场景生成器：生成相关的发电量和现货价格场景"""
    
    def __init__(self, 
                 num_scenarios: int = 2000,
                 num_stages: int = 4,
                 hours_per_stage: int = 168,  # 每周168小时
                 avg_generation: float = 100.0,  # 平均发电量 MWh/h
                 avg_spot_price: float = 150.0,  # 平均现货价格 R$/MWh
                 seed: int = 42):
        """
        初始化场景生成器
        
        参数:
            num_scenarios: 场景数量
            num_stages: 阶段数（周数）
            hours_per_stage: 每阶段小时数
            avg_generation: 平均发电量
            avg_spot_price: 平均现货价格
            seed: 随机种子
        """
        self.num_scenarios = num_scenarios
        self.num_stages = num_stages
        self.hours_per_stage = hours_per_stage
        self.avg_generation = avg_generation
        self.avg_spot_price = avg_spot_price
        self.seed = seed
        
        np.random.seed(seed)
        
    def generate_scenarios(self) -> Dict[str, np.ndarray]:
        """
        生成相关的发电量和现货价格场景
        
        返回:
            包含以下键的字典:
            - 'generation': 发电量场景 [S, T, H]
            - 'spot_price': 现货价格场景 [S, T, H]
            - 'probabilities': 场景概率 [S]
        """
        # 生成发电量场景（考虑负相关性）
        generation_scenarios = self._generate_generation_scenarios()
        
        # 生成现货价格场景（与发电量负相关）
        spot_price_scenarios = self._generate_spot_price_scenarios(generation_scenarios)
        
        # 均匀概率
        probabilities = np.ones(self.num_scenarios) / self.num_scenarios
        
        return {
            'generation': generation_scenarios,
            'spot_price': spot_price_scenarios,
            'probabilities': probabilities
        }
    
    def _generate_generation_scenarios(self) -> np.ndarray:
        """
        生成可再生能源发电量场景
        使用AR(1)模型模拟时间相关性
        
        返回:
            发电量场景 [S, T, H]
        """
        S = self.num_scenarios
        T = self.num_stages
        H = self.hours_per_stage
        
        generation = np.zeros((S, T, H))
        
        # AR(1)参数
        phi = 0.7  # 自相关系数
        sigma = 0.3 * self.avg_generation  # 标准差
        
        for s in range(S):
            # 每个阶段的基准发电量（周平均）
            stage_base = np.random.normal(self.avg_generation, sigma * 0.5, T)
            
            for t in range(T):
                # 小时级波动（AR(1)过程）
                hourly_gen = np.zeros(H)
                hourly_gen[0] = stage_base[t] + np.random.normal(0, sigma)
                
                for h in range(1, H):
                    # AR(1): X_t = phi * X_{t-1} + epsilon
                    hourly_gen[h] = phi * (hourly_gen[h-1] - stage_base[t]) + \
                                   stage_base[t] + np.random.normal(0, sigma)
                
                # 确保非负
                generation[s, t, :] = np.maximum(hourly_gen, 0)
        
        return generation
    
    def _generate_spot_price_scenarios(self, generation: np.ndarray) -> np.ndarray:
        """
        生成现货价格场景（与发电量负相关）
        模拟"鸭形曲线"效应
        
        参数:
            generation: 发电量场景 [S, T, H]
            
        返回:
            现货价格场景 [S, T, H]
        """
        S, T, H = generation.shape
        spot_price = np.zeros((S, T, H))
        
        # 价格参数
        base_price = self.avg_spot_price
        price_volatility = 0.4 * base_price
        
        # 负相关系数（发电量高时价格低）
        correlation_coef = -0.6
        
        for s in range(S):
            for t in range(T):
                # 基准价格（周平均）
                stage_base_price = np.random.normal(base_price, price_volatility * 0.3)
                
                for h in range(H):
                    # 发电量归一化偏差
                    gen_deviation = (generation[s, t, h] - self.avg_generation) / self.avg_generation
                    
                    # 价格受发电量影响（负相关）
                    price_impact = correlation_coef * gen_deviation * price_volatility
                    
                    # 随机波动
                    random_shock = np.random.normal(0, price_volatility * 0.5)
                    
                    # 最终价格
                    price = stage_base_price - price_impact + random_shock
                    
                    # 确保价格在合理范围内
                    spot_price[s, t, h] = np.maximum(price, base_price * 0.2)
        
        return spot_price

