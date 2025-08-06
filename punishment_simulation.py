"""
Author: CodeBuddy
Date: 2025-08-06
Version: 1.0
Coding: UTF-8
License: MIT
Description: 美食大战老鼠卡片强化失败惩罚模拟工具
             用于分析不同星级卡片强化失败的惩罚值
"""

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import json
import os

class PunishmentSimulator:
    def __init__(self, base_card_values, success_rates, downgrade_levels):
        """
        初始化惩罚模拟器
        
        Args:
            base_card_values: 各星级卡片的基础价值字典
            success_rates: 各星级强化的成功率字典
            downgrade_levels: 各星级强化失败后降级的等级数字典
        """
        self.base_card_values = base_card_values
        self.success_rates = success_rates
        self.downgrade_levels = downgrade_levels
        
        # 存储模拟结果
        self.simulated_values = {}
        self.punishment_factors = {}
    
    def simulate_enhancement(self, current_star, target_star, num_simulations=10000):
        """
        模拟从current_star强化到target_star的过程，考虑失败降级
        
        Args:
            current_star: 当前星级
            target_star: 目标星级
            num_simulations: 模拟次数
        
        Returns:
            期望成本
        """
        if current_star >= target_star:
            return 0
        
        total_cost = 0
        attempts_count = 0
        
        for _ in range(num_simulations):
            cost = 0
            current = current_star
            attempts = 0
            
            while current < target_star:
                attempts += 1
                # 每次尝试的成本是当前星级卡片的价值
                attempt_cost = self.base_card_values[current]
                cost += attempt_cost
                
                # 检查强化是否成功
                if np.random.random() < self.success_rates[current+1]:
                    # 成功
                    current = target_star
                else:
                    # 失败 - 如果星级>=5，则降级
                    if current >= 5 and current in self.downgrade_levels:
                        current = max(current - self.downgrade_levels[current], 0)
            
            total_cost += cost
            attempts_count += attempts
        
        avg_cost = total_cost / num_simulations
        avg_attempts = attempts_count / num_simulations
        
        return avg_cost, avg_attempts
    
    def calculate_punishment_factors(self, max_star=16, num_simulations=10000):
        """
        计算各星级强化的惩罚因子
        
        Args:
            max_star: 最大星级
            num_simulations: 每个星级的模拟次数
        
        Returns:
            惩罚因子字典 {星级: 惩罚因子}
        """
        # 计算不考虑失败惩罚的理论成本
        theoretical_costs = {}
        for star in range(1, max_star + 1):
            if star == 1:
                theoretical_costs[star] = self.base_card_values[0] / self.success_rates[star]
            else:
                theoretical_costs[star] = self.base_card_values[star-1] / self.success_rates[star]
        
        # 计算考虑失败惩罚的模拟成本
        simulated_costs = {}
        avg_attempts = {}
        
        for star in tqdm(range(1, max_star + 1), desc="Simulating star levels"):
            if star <= 6:  # 6星及以下不考虑失败惩罚
                simulated_costs[star] = theoretical_costs[star]
                avg_attempts[star] = 1 / self.success_rates[star]
            else:
                sim_cost, sim_attempts = self.simulate_enhancement(star-1, star, num_simulations)
                simulated_costs[star] = sim_cost
                avg_attempts[star] = sim_attempts
        
        # 计算惩罚因子
        punishment_factors = {}
        for star in range(1, max_star + 1):
            if star <= 6:
                punishment_factors[star] = 1.0  # 无惩罚
            else:
                punishment_factors[star] = simulated_costs[star] / theoretical_costs[star]
        
        self.simulated_values = {
            "theoretical_costs": theoretical_costs,
            "simulated_costs": simulated_costs,
            "avg_attempts": avg_attempts
        }
        self.punishment_factors = punishment_factors
        
        return punishment_factors
    
    def plot_results(self):
        """绘制模拟结果图表"""
        if not self.punishment_factors:
            print("请先运行 calculate_punishment_factors 方法")
            return
        
        stars = list(self.punishment_factors.keys())
        factors = list(self.punishment_factors.values())
        
        # 绘制惩罚因子
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.bar(stars, factors)
        plt.xlabel('Star Level')
        plt.ylabel('Punishment Factor')
        plt.title('Enhancement Punishment Factor by Star Level')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 在每个柱子上方显示数值
        for i, v in enumerate(factors):
            plt.text(stars[i], v + 0.05, f'{v:.2f}', ha='center')
        
        # 绘制成本对比
        if self.simulated_values:
            theo_costs = list(self.simulated_values["theoretical_costs"].values())
            sim_costs = list(self.simulated_values["simulated_costs"].values())
            
            plt.subplot(1, 2, 2)
            width = 0.35
            x = np.arange(len(stars))
            plt.bar(x - width/2, theo_costs, width, label='Theoretical Cost')
            plt.bar(x + width/2, sim_costs, width, label='Simulated Cost')
            plt.xlabel('Star Level')
            plt.ylabel('Cost (in base card value)')
            plt.title('Theoretical vs Simulated Enhancement Cost')
            plt.xticks(x, stars)
            plt.legend()
            plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.show()
    
    def save_results(self, output_dir="results"):
        """保存模拟结果到JSON文件"""
        if not self.punishment_factors:
            print("请先运行 calculate_punishment_factors 方法")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        results = {
            "punishment_factors": self.punishment_factors,
            "theoretical_costs": self.simulated_values.get("theoretical_costs", {}),
            "simulated_costs": self.simulated_values.get("simulated_costs", {}),
            "avg_attempts": self.simulated_values.get("avg_attempts", {})
        }
        
        with open(os.path.join(output_dir, "punishment_simulation_results.json"), "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        
        print(f"结果已保存到 {os.path.join(output_dir, 'punishment_simulation_results.json')}")

def main():
    # 示例基础卡片价值（可以从之前的模型结果中加载）
    base_card_values = {
        0: 1,
        1: 1,
        2: 2,
        3: 4,
        4: 8,
        5: 16,
        6: 32,
        7: 64,
        8: 128,
        9: 256,
        10: 512,
        11: 1024,
        12: 2048,
        13: 4096,
        14: 8192,
        15: 16384
    }
    
    # 成功率配置
    success_rates = {
        1: 1.0,   # 0→1星
        2: 1.0,   # 1→2星
        3: 0.968, # 2→3星
        4: 0.686, # 3→4星
        5: 0.495, # 4→5星
        6: 0.396, # 5→6星
        7: 0.319, # 6→7星
        8: 0.264, # 7→8星
        9: 0.220, # 8→9星
        10: 0.135, # 9→10星
        11: 0.125, # 10→11星
        12: 0.116, # 11→12星
        13: 0.107, # 12→13星
        14: 0.101, # 13→14星
        15: 0.095, # 14→15星
        16: 0.088  # 15→16星
    }
    
    # 降级等级配置
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
    
    # 创建模拟器
    simulator = PunishmentSimulator(
        base_card_values=base_card_values,
        success_rates=success_rates,
        downgrade_levels=downgrade_levels
    )
    
    # 计算惩罚因子
    punishment_factors = simulator.calculate_punishment_factors(num_simulations=5000)
    
    # 打印结果
    print("\n惩罚因子:")
    for star, factor in punishment_factors.items():
        print(f"{star}星: {factor:.4f}")
    
    # 绘制结果
    simulator.plot_results()
    
    # 保存结果
    simulator.save_results(output_dir="e:\\FoodVsRats-CardEnhanceModel\\outputjson\\punishment_simulation")

if __name__ == "__main__":
    main()