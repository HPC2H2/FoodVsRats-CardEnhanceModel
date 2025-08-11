# FoodVsRatsCardEnhanceModel

[简体中文](#chinese) | [English](#english) 
<a id="chinese"></a>
## 简体中文

本项目实现了一个针对"美食大战老鼠"游戏中卡片强化的优化决策模型，重点关注在考虑高星级强化失败惩罚时卡片的真实价值计算。

### 项目概述

该模型计算从低星级到高星级强化卡片的最优策略，考虑以下因素：

1. 基础卡片价值（0星卡）
2. 强化材料需求
3. 基于卡片组合的成功概率
4. VIP和公会加成
5. 四叶草价值和效果
6. **高星级强化的失败惩罚（6→7星及以上）**

### 项目文件

- `model_with_addition.py`：原始模型，考虑四叶草和其他加成，但不考虑失败惩罚
- `model_with_punishment.py`：增强模型，使用蒙特卡洛模拟来考虑失败惩罚
- `punishment_simulation.py`：详细分析惩罚值的工具
- `strategy_builder.py`：构建强化策略的辅助类
- `generate_combinations.py`：生成所有可能卡片组合的工具

### 惩罚模型

当从6星强化到7星及以上时，存在失败风险，导致卡片降级。这显著影响了高星级卡片的真实价值。

惩罚模型使用蒙特卡洛模拟来计算考虑失败惩罚的预期成本：

1. 对于每次强化尝试，我们基于成功概率模拟结果
2. 如果强化失败，卡片会根据降级配置降级
3. 我们继续尝试强化，直到达到目标星级
4. 经过多次模拟后，我们计算平均成本，这代表真实的预期成本

### 惩罚因子

每个星级的惩罚因子计算如下：

```
惩罚因子 = 考虑失败的模拟成本 / 不考虑失败的理论成本
```

这些因子表示考虑失败惩罚时强化卡片的成本增加倍数。

### 使用方法

运行带惩罚的模型：

```bash
python model_with_punishment.py
```

详细分析惩罚因子：

```bash
python punishment_simulation.py
```

### 结果

模型输出包含以下内容的JSON文件：

1. 每个星级的最优强化策略
2. 每个星级的卡片价值
3. 每个星级的强化成本
4. 高星级强化的惩罚因子

这些结果可用于在游戏中做出明智的卡片强化决策。

### 未来改进

- 实现更复杂的降级模型（例如，可变降级等级）
- 考虑替代强化路径
- 优化模拟性能，加快计算速度
- 添加用户界面，使模型更易于交互
- 结合真实数据来优化成功概率
- 为不同参数配置添加敏感性分析
<a id="english"></a>
## English

This project implements an optimized decision model for card enhancement in the "Food vs Rats" game, with a focus on calculating the true value of cards when considering failure penalties for high-star enhancements.

### Project Overview

The model calculates the optimal strategy for enhancing cards from lower star levels to higher star levels, taking into account:

1. Base card value (0-star cards)
2. Enhancement material requirements
3. Success probabilities based on card combinations
4. VIP and guild bonuses
5. Four-leaf clover value and effects
6. **Failure penalties for high-star enhancements (6→7 stars and above)**

### Files in this Project

- `model_with_addition.py`: Original model that considers four-leaf clover and other bonuses, but without failure penalties
- `model_with_punishment.py`: Enhanced model that incorporates failure penalties using Monte Carlo simulation
- `punishment_simulation.py`: Utility for analyzing punishment values in detail
- `strategy_builder.py`: Helper class for building enhancement strategies
- `generate_combinations.py`: Utility for generating all possible card combinations

### Punishment Model

When enhancing cards from 6-star to 7-star and above, there's a risk of failure that results in the card being downgraded. This significantly impacts the true value of high-star cards.

The punishment model uses Monte Carlo simulation to calculate the expected cost of enhancing cards with failure penalties:

1. For each enhancement attempt, we simulate the outcome based on the success probability
2. If the enhancement fails, the card is downgraded according to the downgrade level configuration
3. We continue attempting enhancements until we reach the target star level
4. After many simulations, we calculate the average cost, which represents the true expected cost

### Punishment Factors

The punishment factor for each star level is calculated as:

```
Punishment Factor = Simulated Cost with Failure / Theoretical Cost without Failure
```

These factors represent how much more expensive it is to enhance cards when considering failure penalties.

### Usage

To run the model with punishment:

```bash
python model_with_punishment.py
```

To analyze punishment factors in detail:

```bash
python punishment_simulation.py
```

### Results

The model outputs JSON files containing:

1. Optimal enhancement strategies for each star level
2. Card values at each star level
3. Enhancement costs at each star level
4. Punishment factors for high-star enhancements

These results can be used to make informed decisions about card enhancement in the game.

### Future Improvements

- Implement more sophisticated downgrade models (e.g., variable downgrade levels)
- Consider alternative enhancement paths
- Optimize simulation performance for faster calculations
- Add a user interface for easier interaction with the model
- Incorporate real-world data to refine success probabilities
- Add sensitivity analysis for different parameter configurations
