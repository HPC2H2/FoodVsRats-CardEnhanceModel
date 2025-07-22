"""
Author: HPC2H2
Date: 2025-07-22
Version: 1.0
Coding: UTF-8
License: MIT
Description: generate_combinations.py
"""

def generate_combinations(dim=2, max_total=3, exclude_zero=True):
    """生成所有可能的卡牌组合，其中各维度的和不超过max_total
    
    Args:
        dim: 维度 (2或3)
        max_total: 卡牌总数上限
        exclude_zero: 是否排除全零的组合
        
    Returns:
        卡牌类型列表的列表，例如：
        dim=2时: [['same', 'down1'], ['same', 'same', 'down1'], ...]
        dim=3时: [['same', 'down1', 'down2'], ['same', 'same', 'down1'], ...]
        其中'same'会排在'down1'前面，'down1'会排在'down2'前面。
    """
    if dim not in (2, 3):
        raise ValueError("dim 必须是 2 或 3")
    
    card_combinations = []
    def is_valid_combination(*values):
        return (sum(values) <= max_total and 
                not (exclude_zero and all(v == 0 for v in values)))
    
    if dim == 2:
        for same_star in range(max_total + 1):  # 同星级卡数量
            for down1_star in range(max_total + 1):  # 低一星卡数量
                if is_valid_combination(same_star, down1_star):
                    # 转换为卡牌类型列表
                    cards = ['same'] * same_star + ['down1'] * down1_star
                    card_combinations.append(cards)
    else:  # dim == 3
        for same_star in range(max_total + 1):  # 同星级卡数量
            for down1_star in range(max_total + 1):  # 低一星卡数量
                for down2_star in range(max_total + 1):  # 低二星卡数量
                    if is_valid_combination(same_star, down1_star, down2_star):
                        # 转换为卡牌类型列表
                        cards = (['same'] * same_star + 
                                ['down1'] * down1_star + 
                                ['down2'] * down2_star)
                        card_combinations.append(cards)
    
    return card_combinations
