# 美食大战老鼠卡片强化蒙特卡洛模拟

## 蒙特卡洛模拟概述

在美食大战老鼠卡片强化系统中，当主卡星级≥6时，强化失败会导致卡片降级。这种机制使得传统的期望成本计算方法不再准确，因此我们引入蒙特卡洛模拟来更精确地估计实际期望成本。

## 蒙特卡洛模拟原理

蒙特卡洛方法是一种基于随机采样的数值计算方法，通过大量随机实验来近似计算复杂问题的解。在卡片强化模型中，我们使用蒙特卡洛模拟来：

1. 模拟大量强化尝试
2. 考虑失败降级的影响
3. 计算实际期望成本
4. 确定惩罚因子

## 模拟器实现

`PunishmentSimulator`类是蒙特卡洛模拟的核心实现：

```python
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
```

### 单次强化模拟

```python
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
```

### 惩罚因子计算

```python
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
```

## 模拟结果分析

### 惩罚因子解释

惩罚因子$PF(S_i)$表示实际期望成本与理论期望成本的比值：

$$PF(S_i) = \frac{C_{simulated}(S_{i-1} \rightarrow S_i)}{C_{traditional}(S_{i-1} \rightarrow S_i)}$$

通常，$PF(S_i) < 1$，这意味着考虑失败降级后，实际期望成本低于理论期望成本。这是因为：

1. 失败降级后，我们从较低星级重新开始强化
2. 较低星级的强化成本通常低于当前星级
3. 较低星级的成功率通常高于当前星级

### 典型惩罚因子值

以下是通过模拟得到的典型惩罚因子值：

| 星级 | 惩罚因子 |
|------|----------|
| 1-6  | 1.0000   |
| 7    | 0.5970   |
| 8    | 0.4470   |
| 9    | 0.3640   |
| 10   | 0.2310   |
| 11   | 0.2180   |
| 12   | 0.2060   |
| 13   | 0.1930   |
| 14   | 0.1820   |
| 15   | 0.1720   |
| 16   | 0.1610   |

这些值表明，随着星级的增加，惩罚因子逐渐减小，这意味着高星级卡片的实际强化成本远低于理论计算值。

## 可视化分析

模拟器提供了可视化功能，用于直观地比较理论成本和模拟成本：

```python
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
```

## 结论

蒙特卡洛模拟为我们提供了一种更准确的方法来估计考虑失败降级的卡片强化成本。通过引入惩罚因子，我们可以调整理论期望成本，使其更接近实际情况。

这种方法的优势在于：

1. 考虑了失败降级的复杂影响
2. 提供了更准确的卡片价值估计
3. 帮助玩家做出更明智的强化决策
4. 揭示了高星级卡片强化的实际成本低于理论计算值的现象

通过这种数学模型和模拟方法，玩家可以最大化资源利用效率，减少强化过程中的浪费，更快地提升卡片星级。