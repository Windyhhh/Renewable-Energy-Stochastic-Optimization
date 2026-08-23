"""
场景树构建模块
通过聚类算法构建多阶段决策树
"""

import numpy as np
from sklearn.cluster import KMeans
from typing import Dict, List, Tuple


class ScenarioTree:
    """场景树构建器"""
    
    def __init__(self, 
                 scenarios: Dict[str, np.ndarray],
                 branching_factors: List[int] = [2, 2, 2, 2]):
        """
        初始化场景树
        
        参数:
            scenarios: 场景数据字典
            branching_factors: 每个阶段的分支因子
        """
        self.generation = scenarios['generation']  # [S, T, H]
        self.spot_price = scenarios['spot_price']  # [S, T, H]
        self.probabilities = scenarios['probabilities']  # [S]
        
        self.num_scenarios = self.generation.shape[0]
        self.num_stages = self.generation.shape[1]
        self.branching_factors = branching_factors
        
        # 树结构
        self.nodes = []  # 节点列表
        self.node_scenarios = {}  # 每个节点包含的场景
        self.node_parents = {}  # 节点的父节点
        self.node_children = {}  # 节点的子节点
        
    def build_tree(self) -> Dict:
        """
        构建场景树
        
        返回:
            树结构信息
        """
        # 初始化根节点
        root_node = {
            'id': 0,
            'stage': 0,
            'scenarios': list(range(self.num_scenarios)),
            'avg_spot_price': np.mean(self.spot_price[:, 0, :]),
            'avg_generation': np.mean(self.generation[:, 0, :])
        }
        
        self.nodes.append(root_node)
        self.node_scenarios[0] = root_node['scenarios']
        self.node_children[0] = []
        
        node_counter = 1
        current_stage_nodes = [0]
        
        # 逐阶段构建树
        for t in range(1, self.num_stages):
            next_stage_nodes = []
            
            for parent_node_id in current_stage_nodes:
                parent_scenarios = self.node_scenarios[parent_node_id]
                
                # 对父节点的场景进行聚类
                clusters = self._cluster_scenarios(parent_scenarios, t, 
                                                   self.branching_factors[t-1])
                
                # 为每个聚类创建子节点
                for cluster_scenarios in clusters:
                    child_node = {
                        'id': node_counter,
                        'stage': t,
                        'scenarios': cluster_scenarios,
                        'avg_spot_price': np.mean(self.spot_price[cluster_scenarios, t, :]),
                        'avg_generation': np.mean(self.generation[cluster_scenarios, t, :])
                    }
                    
                    self.nodes.append(child_node)
                    self.node_scenarios[node_counter] = cluster_scenarios
                    self.node_parents[node_counter] = parent_node_id
                    self.node_children[parent_node_id].append(node_counter)
                    self.node_children[node_counter] = []
                    
                    next_stage_nodes.append(node_counter)
                    node_counter += 1
            
            current_stage_nodes = next_stage_nodes
        
        return self._get_tree_info()
    
    def _cluster_scenarios(self, scenario_indices: List[int], 
                          stage: int, num_clusters: int) -> List[List[int]]:
        """
        对场景进行聚类
        
        参数:
            scenario_indices: 要聚类的场景索引
            stage: 当前阶段
            num_clusters: 聚类数量
            
        返回:
            聚类结果（场景索引列表的列表）
        """
        if len(scenario_indices) <= num_clusters:
            return [[idx] for idx in scenario_indices]
        
        # 使用周平均现货价格作为聚类特征
        features = []
        for idx in scenario_indices:
            avg_price = np.mean(self.spot_price[idx, stage, :])
            features.append([avg_price])
        
        features = np.array(features)
        
        # K-means聚类
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features)
        
        # 按聚类分组
        clusters = [[] for _ in range(num_clusters)]
        for i, label in enumerate(labels):
            clusters[label].append(scenario_indices[i])
        
        # 移除空聚类
        clusters = [c for c in clusters if len(c) > 0]
        
        return clusters
    
    def _get_tree_info(self) -> Dict:
        """获取树结构信息"""
        leaf_nodes = [n['id'] for n in self.nodes if len(self.node_children[n['id']]) == 0]
        
        return {
            'num_nodes': len(self.nodes),
            'num_leaf_nodes': len(leaf_nodes),
            'leaf_nodes': leaf_nodes,
            'nodes': self.nodes,
            'node_scenarios': self.node_scenarios,
            'node_parents': self.node_parents,
            'node_children': self.node_children
        }
    
    def get_node_probability(self, node_id: int) -> float:
        """计算节点概率"""
        scenarios = self.node_scenarios[node_id]
        return np.sum(self.probabilities[scenarios])
    
    def get_paths(self) -> List[List[int]]:
        """获取从根节点到所有叶节点的路径"""
        leaf_nodes = [n['id'] for n in self.nodes if len(self.node_children[n['id']]) == 0]
        paths = []
        
        for leaf in leaf_nodes:
            path = [leaf]
            current = leaf
            while current in self.node_parents:
                current = self.node_parents[current]
                path.insert(0, current)
            paths.append(path)
        
        return paths

