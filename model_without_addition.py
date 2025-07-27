"""
Author: HPC2H2
Date: 2025-07-22
Version: 1.0
Coding: UTF-8
License: MIT
Description: 在不考虑四叶草和不考虑失败降级惩罚情况下的美食大战老鼠卡片强化最优决策模型。
"""

from generate_combinations import generate_combinations
from strategy_builder import StrategyBuilder

p_list = [
    ["主卡星级→目标星级", "0→1", "1→2", "2→3", "3→4", "4→5", "5→6", "6→7", "7→8", "8→9", "9→10", "10→11", "11→12", "12→13", "13→14", "14→15", "15→16"],
    ["副卡低2星，好卡", -1, -1, 0.608, 0.429, 0.242, 0.201, 0.132, 0.106, 0.06, 0.022, 0.018, 0.017, 0.016, 0.014, 0.013, 0.01],
    ["副卡低1星，好卡", -1, 0.88, 0.792, 0.55, 0.403, 0.33, 0.264, 0.212, 0.132, 0.045, 0.046, 0.043, 0.04, 0.04, 0.034, 0.03],
    ["副卡同星，好卡", 1, 1, 0.968, 0.686, 0.495, 0.396, 0.319, 0.264, 0.22, 0.135, 0.125, 0.116, 0.107, 0.101, 0.095, 0.088]
]


STAR_LIMIT = 16
Vcard_mins = [1e9]*(STAR_LIMIT + 1)
cost_mins = [1e9]*(STAR_LIMIT + 1)
Vcard_mins[0] = 1
best_strategy = [""]*(STAR_LIMIT + 1)
best_strategy[1:STAR_LIMIT + 1] = p_list[0][1:STAR_LIMIT + 1]

# (同星副卡数, 低一星副卡数) 
combinations_2 =generate_combinations(dim=2, max_total=3, exclude_zero=True)
#  (同星副卡数, 低一星副卡数, 低二星副卡数) 
combinations_3 = generate_combinations(dim=3, max_total=3, exclude_zero=True)
sub_best_strategy = ""

for i in range(1, STAR_LIMIT + 1):
    if i == 1:
        p3 = p_list[3][i]
        cost_mins[i] = Vcard_mins[0]/p3
        Vcard_mins[i] = Vcard_mins[0] + cost_mins[i]
        strategy = StrategyBuilder()
        strategy.add_card(i-1)
        strategy.set_probability(p3)
        sub_best_strategy = strategy.build()

    elif i == 2:
        p3 = p_list[3][i]
        p2 = p_list[2][i]
        for comb in combinations_2:
            cur_cost = 0
            cur_p = 0
            strategy = StrategyBuilder()
            for j in range(0, len(comb)):
                if comb[j] == 'same':
                    if j == 0: # 第一张卡
                        cur_p = p3
                    else:
                        cur_p = min(cur_p + p3/3, 1)
                    strategy.add_card(i-1)
                    cur_cost += Vcard_mins[i-1]
                elif comb[j] == 'down1':
                    if j == 0: # 第一张卡
                        cur_p = p2
                    else:
                        cur_p = min(cur_p + p2/3, 1)
                    strategy.add_card(i-2)
                    cur_cost += Vcard_mins[i-2]
            cur_cost /= cur_p
            print(f"当前状态：{i-1}→{i}, 当前组合: {comb}, 当前概率: {cur_p}, 当前成本: {cur_cost}")
            if cur_cost < cost_mins[i]:
                strategy.set_probability(cur_p)
                sub_best_strategy = strategy.build()
                cost_mins[i] = cur_cost
                Vcard_mins[i] = Vcard_mins[i-1] + cost_mins[i]
    else:
        p3 = p_list[3][i]
        p2 = p_list[2][i]
        p1 = p_list[1][i]
        for comb in combinations_3:
            cur_cost = 0
            cur_p = 0
            strategy = StrategyBuilder()
            for j in range(0, len(comb)):
                if comb[j] == 'same':
                    if j == 0: # 第一张卡
                        cur_p = p3
                    else:
                        cur_p = min(cur_p + p3/3, 1)
                    strategy.add_card(i-1)
                    cur_cost += Vcard_mins[i-1]
                elif comb[j] == 'down1':
                    if j == 0: # 第一张卡
                        cur_p = p2
                    else:
                        cur_p = min(cur_p + p2/3, 1)
                    strategy.add_card(i-2)
                    cur_cost += Vcard_mins[i-2]
                elif comb[j] == 'down2':
                    if j == 0: # 第一张卡
                        cur_p = p1
                    else:
                        cur_p = min(cur_p + p1/3, 1)
                    strategy.add_card(i-3)
                    cur_cost += Vcard_mins[i-3]
            cur_cost /= cur_p
            print(f"当前状态：{i-1}→{i}, 当前组合: {comb}, 当前概率: {cur_p}, 当前成本: {cur_cost}")
            if cur_cost < cost_mins[i]:
                strategy.set_probability(cur_p)
                sub_best_strategy = strategy.build()
                cost_mins[i] = cur_cost
                Vcard_mins[i] = Vcard_mins[i-1] + cost_mins[i]
    best_strategy[i] += sub_best_strategy

print("最佳策略：")
for i in range(1, STAR_LIMIT + 1):
    print(best_strategy[i], end='\n')

print("单张卡片的价值：")
for i in range(1, STAR_LIMIT + 1):
    print(f"星级 {i} 的卡片价值: {Vcard_mins[i]:.2f}，成本: {cost_mins[i]:.2f}")


