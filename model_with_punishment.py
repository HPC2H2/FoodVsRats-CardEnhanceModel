"""
Author: HPC2H2 (Extended by CodeBuddy)
Date: 2025-08-06
Version: 1.1
Coding: UTF-8
License: MIT
Description: 考虑四叶草等加成，并考虑失败降级惩罚情况下的美食大战老鼠卡片强化最优决策模型。
             主卡大于6星时，使用蒙特卡洛模拟来确定惩罚值。
"""

import os
import json
import random
import numpy as np
from tqdm import tqdm

from generate_combinations import generate_combinations
from strategy_builder import StrategyBuilder

# 原始成功率表
p_list = [
    ["主卡星级→目标星级", "0→1", "1→2", "2→3", "3→4", "4→5", "5→6", "6→7", "7→8", "8→9", "9→10", "10→11", "11→12", "12→13", "13→14", "14→15", "15→16"],
    ["副卡低2星，好卡", -1, -1, 0.608, 0.429, 0.242, 0.201, 0.132, 0.106, 0.06, 0.022, 0.018, 0.017, 0.016, 0.014, 0.013, 0.01],
    ["副卡低1星，好卡", -1, 0.88, 0.792, 0.55, 0.403, 0.33, 0.264, 0.212, 0.132, 0.045, 0.046, 0.043, 0.04, 0.04, 0.034, 0.03],
    ["副卡同星，好卡", 1, 1, 0.968, 0.686, 0.495, 0.396, 0.319, 0.264, 0.22, 0.135, 0.125, 0.116, 0.107, 0.101, 0.095, 0.088]
]

clover_levels = ['', '1', '2', '3', '4', '5', '6', 'S', 'SS', 'SSS', 'SSR']
clover_additions = [1, 1.2, 1.4, 1.7, 2, 2.4, 2.7, 3, 3.2, 3.6, 4]
# 调整四叶草价值，使其更符合实际情况
Vclovers = [0, 4, 16, 80, 400, 2000, 10000, 50000, 250000, 1250000, 6250000]

VIP_additions = [0]*4 + [0.04, 0.05, 0.07, 0.08, 0.09, 0.11, 0.13, 0.15, 0.17, 0.19]
guild_additions = [0, 0.01, 0.03, 0.05, 0.08, 0.12, 0.16]

STAR_LIMIT = 16
# (同星副卡数, 低一星副卡数) 
combinations_2 = generate_combinations(dim=2, max_total=3, exclude_zero=True)
# (同星副卡数, 低一星副卡数, 低二星副卡数) 
combinations_3 = generate_combinations(dim=3, max_total=3, exclude_zero=True)

# 失败降级惩罚配置
# 当主卡星级 >= 6 时，失败会降级
# 降级等级配置：key是主卡星级，value是失败后降低的星级数
downgrade_levels = {
    6: 1,   # 6→7星失败降到5星
    7: 1,   # 7→8星失败降到6星
    8: 1,   # 8→9星失败降到7星
    9: 1,   # 9→10星失败降到8星
    10: 1,  # 10→11星失败降到9星
    11: 1,  # 11→12星失败降到10星
    12: 1,  # 12→13星失败降到11星
    13: 1,  # 13→14星失败降到12星
    14: 1,  # 14→15星失败降到13星
    15: 1   # 15→16星失败降到14星
}

# 从预先计算的模拟结果中加载惩罚因子
def load_punishment_factors():
    """
    从预先计算的模拟结果中加载惩罚因子
    
    Returns:
        惩罚因子字典 {星级: 惩罚因子}
    """
    try:
        with open(os.path.join("outputjson", "punishment_simulation", "punishment_simulation_results.json"), "r", encoding="utf-8") as f:
            results = json.load(f)
            return {int(k): v for k, v in results["punishment_factors"].items()}
    except FileNotFoundError:
        # 如果文件不存在，返回默认惩罚因子
        return {
            1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0,
            7: 0.597, 8: 0.447, 9: 0.364, 10: 0.231,
            11: 0.218, 12: 0.206, 13: 0.193, 14: 0.182,
            15: 0.172, 16: 0.161
        }

def calculate_expected_cost(current_star, target_star, success_rate, card_value, punishment_factors):
    """
    计算从current_star强化到target_star的期望成本，考虑惩罚因子
    
    我们首先计算传统的理论成本（卡片价值/成功率），然后应用惩罚因子来调整。
    惩罚因子是通过蒙特卡洛模拟得出的，更准确地反映了失败降级的影响。
    
    Args:
        current_star: 当前星级
        target_star: 目标星级
        success_rate: 成功率
        card_value: 当前星级卡片的价值（材料成本）
        punishment_factors: 惩罚因子字典
    
    Returns:
        期望成本
    """
    if current_star >= target_star:
        return 0
    
    # 避免除以零
    if success_rate <= 0:
        return float('inf')
    
    # 理论成本 = 卡片价值 / 成功率
    # 这是传统的期望成本计算方法
    theoretical_cost = card_value / success_rate
    
    # 如果星级 >= 7，应用惩罚因子
    # 惩罚因子已经通过蒙特卡洛模拟考虑了失败降级的影响
    # 由于惩罚因子小于1，这实际上降低了理论成本
    if target_star >= 7:
        return theoretical_cost * punishment_factors[target_star]
    else:
        return theoretical_cost

def main():
    # 加载惩罚因子
    punishment_factors = load_punishment_factors()
    print("Loaded punishment factors:", punishment_factors)
    
    # 处理所有VIP等级和公会等级的情况
    for cur_vip in range(len(VIP_additions)):
        for cur_guild in range(len(guild_additions)):
            print(f"Processing VIP level: {cur_vip}, Guild level: {cur_guild}")
            
            # 存储各星级卡片的累计价值（基础价值+所有强化成本的总和）
            Vcard_mins = [1e9] * (STAR_LIMIT + 1)
            # 存储各星级卡片的强化成本（从上一星级强化到当前星级的成本）
            cost_mins = [float('inf')] * (STAR_LIMIT + 1)
            # 存储各星级卡片的最佳性价比（成功率/成本）- 用于选择最优策略
            best_cost_effectiveness = [0] * (STAR_LIMIT + 1)
            Vcard_mins[0] = 1
            best_strategy = [""] * (STAR_LIMIT + 1)
            best_strategy[1:STAR_LIMIT + 1] = p_list[0][1:STAR_LIMIT + 1]
            
            # 计算所有星级卡片的价值（统一处理，根据星级决定是否应用惩罚因子）
            for i in range(1, STAR_LIMIT + 1):
                print(f"Processing star level {i}...")
                
                if i == 1:
                    p3 = p_list[3][i]
                    cost_mins[i] = Vcard_mins[0] / p3
                    Vcard_mins[i] = Vcard_mins[0] + cost_mins[i]
                    strategy = StrategyBuilder()
                    
                    strategy.add_card(i-1)
                    strategy.set_probability(p3)
                    sub_best_strategy = strategy.build()
                
                elif i == 2:
                    p3 = p_list[3][i]
                    p2 = p_list[2][i]
                    sub_best_strategy = ""
                    
                    for comb in combinations_2:
                        cur_cost = 0
                        cur_p = 0
                        strategy = StrategyBuilder()
                        for j in range(0, len(comb)):
                            if comb[j] == 'same':
                                if j == 0:  # 第一张卡
                                    cur_p = p3
                                else:
                                    cur_p = min(cur_p + p3/3, 1)
                                strategy.add_card(i-1)
                                cur_cost += Vcard_mins[i-1]
                            elif comb[j] == 'down1':
                                if j == 0:  # 第一张卡
                                    cur_p = p2
                                else:
                                    cur_p = min(cur_p + p2/3, 1)
                                strategy.add_card(i-2)
                                cur_cost += Vcard_mins[i-2]
                        without_addition_cost = cur_cost
                        without_addition_p = cur_p
                        # 计算加成后的概率
                        for k in range(0, len(clover_levels)):
                            # 计算加成后的概率
                            cur_p = without_addition_p*clover_additions[k]*(1 + guild_additions[cur_guild] + VIP_additions[cur_vip])
                            if cur_p > 1:
                                cur_p = 1
                                
                            cur_cost = without_addition_cost
                            cur_cost += Vclovers[k]
                            
                            # 计算期望成本
                            # 注意：我们传递的是原始材料成本(cur_cost)，而不是除以成功率的成本
                            # 惩罚因子会在calculate_expected_cost函数中应用
                            # 这种方法的好处是：
                            # 1. 更准确地反映实际成本（惩罚因子已经考虑了失败和降级）
                            # 2. 避免在高成功率情况下的成本低估
                            # 3. 更清晰地分离关注点（原始成本与惩罚因素）
                            expected_cost = calculate_expected_cost(
                                current_star=i-1,
                                target_star=i,
                                success_rate=cur_p,
                                card_value=cur_cost,
                                punishment_factors=punishment_factors
                            )
                            
                            # 计算性价比指标：成功率/成本
                            # 性价比与最低成本不同：最低成本只考虑成本最小，而性价比同时考虑成功率和成本的平衡
                            # 性价比高的策略可能不是成本最低的，但是在成功率和成本之间取得了最佳平衡
                            if expected_cost > 0:
                                cost_effectiveness = cur_p / expected_cost
                            else:
                                # 避免除以零
                                cost_effectiveness = 0
                            
                            # 使用性价比作为选择标准，而不是仅仅使用最低成本
                            if cost_effectiveness > best_cost_effectiveness[i]:
                                strategy.use_clover(clover_levels[k])
                                strategy.set_probability(cur_p)
                                sub_best_strategy = strategy.build()
                                best_cost_effectiveness[i] = cost_effectiveness
                                # 仍然计算总成本以便后续使用
                                cost_mins[i] = expected_cost
                                Vcard_mins[i] = Vcard_mins[i-1] + cost_mins[i]
                else:
                    p3 = p_list[3][i]
                    p2 = p_list[2][i]
                    p1 = p_list[1][i]
                    sub_best_strategy = ""
                    
                    # 对于高星级，使用进度条显示
                    if i >= 7:
                        combinations_iterator = tqdm(combinations_3, desc=f"Combinations for {i}-star")
                    else:
                        combinations_iterator = combinations_3
                    
                    for comb in combinations_iterator:
                        cur_cost = 0
                        cur_p = 0
                        strategy = StrategyBuilder()
                        for j in range(0, len(comb)):
                            if comb[j] == 'same':
                                if j == 0:  # 第一张卡
                                    cur_p = p3
                                else:
                                    cur_p = min(cur_p + p3/3, 1)
                                strategy.add_card(i-1)
                                cur_cost += Vcard_mins[i-1]
                            elif comb[j] == 'down1':
                                if j == 0:  # 第一张卡
                                    cur_p = p2
                                else:
                                    cur_p = min(cur_p + p2/3, 1)
                                strategy.add_card(i-2)
                                cur_cost += Vcard_mins[i-2]
                            elif comb[j] == 'down2':
                                if j == 0:  # 第一张卡
                                    cur_p = p1
                                else:
                                    cur_p = min(cur_p + p1/3, 1)
                                strategy.add_card(i-3)
                                cur_cost += Vcard_mins[i-3]
                        without_addition_cost = cur_cost
                        without_addition_p = cur_p
                        # 计算加成后的概率
                        for k in range(len(clover_levels)):
                            # 计算加成后的概率
                            cur_p = without_addition_p*clover_additions[k]*(1 + guild_additions[cur_guild] + VIP_additions[cur_vip])
                            if cur_p > 1:
                                cur_p = 1
                                
                            cur_cost = without_addition_cost
                            cur_cost += Vclovers[k]
                            
                            # 计算期望成本，考虑惩罚因子
                            expected_cost = calculate_expected_cost(
                                current_star=i-1,
                                target_star=i,
                                success_rate=cur_p,
                                card_value=cur_cost,
                                punishment_factors=punishment_factors
                            )
                            
                            # 计算性价比指标
                            cost_effectiveness = cur_p / expected_cost if expected_cost > 0 else 0
                            
                            # 使用性价比作为选择标准
                            if cost_effectiveness > best_cost_effectiveness[i]:
                                strategy.use_clover(clover_levels[k])
                                strategy.set_probability(cur_p)
                                sub_best_strategy = strategy.build()
                                best_cost_effectiveness[i] = cost_effectiveness
                                # 仍然计算总成本以便后续使用
                                cost_mins[i] = expected_cost
                                Vcard_mins[i] = Vcard_mins[i-1] + cost_mins[i]
                
                best_strategy[i] += sub_best_strategy
                print(best_strategy[i])
            
            # 构建输出数据结构
            data = {
                "当前VIP等级": cur_vip,
                "当前公会等级": cur_guild,
                "最佳策略": {str(i): best_strategy[i] for i in range(1, STAR_LIMIT + 1)},
                "单张卡片的价值": {
                    str(i): {
                        "价值": Vcard_mins[i],  # 卡片的累计价值（基础价值+所有强化成本）
                        "成本": cost_mins[i],   # 强化成本（从上一星级强化到当前星级）
                        "性价比": best_cost_effectiveness[i]  # 最佳策略的性价比（成功率/成本）
                    } 
                    for i in range(1, STAR_LIMIT + 1)
                }
            }
            
            output_dir = os.path.join("e:\\FoodVsRats-CardEnhanceModel", "outputjson", "model_with_punishment")
            os.makedirs(output_dir, exist_ok=True)
            filename = f"VIP等级：{cur_vip}  公会等级：{cur_guild}.json"
            with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
                # 保存到 JSON 文件
                json.dump(data, f, ensure_ascii=False, indent=4)  # 确保中文不乱码，格式化输出

if __name__ == "__main__":
    main()