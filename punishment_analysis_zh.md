# 美食大战老鼠卡片强化模型实现（含惩罚机制）

## 模型概述

这个模型是为游戏"美食大战老鼠"中的卡片强化系统设计的，考虑了四叶草加成和失败降级惩罚情况下的最优决策模型。当主卡大于6星时，使用蒙特卡洛模拟来确定惩罚值。

## 数学模型与符号说明

### 基本符号定义

- $p_{i,j}$: 使用星级为$i$的副卡强化到星级$j$的基础成功率
- $V_{card}(i)$: 星级为$i$的卡片累计价值
- $C_{min}(i)$: 从$i-1$星强化到$i$星的最小期望成本
- $CE(i)$: 星级为$i$的最佳性价比(成功率/成本)
- $A_{clover}(k)$: 四叶草等级$k$提供的成功率加成倍数
- $A_{VIP}(v)$: VIP等级$v$提供的成功率加成
- $A_{guild}(g)$: 公会等级$g$提供的成功率加成
- $V_{clover}(k)$: 四叶草等级$k$的价值
- $PF(i)$: 星级$i$的惩罚因子

### 成功率计算

对于使用多张副卡的情况，成功率计算如下：

1. 第一张卡的成功率为基础成功率 $p_{i,j}$
2. 后续每张卡增加基础成功率的1/3，但总成功率上限为1
3. 应用四叶草、VIP和公会加成：

$$p_{final} = \min(p_{base} \times A_{clover}(k) \times (1 + A_{VIP}(v) + A_{guild}(g)), 1)$$

其中：
- $p_{base}$ 是基础成功率（考虑多张副卡后）
- $A_{clover}(k)$ 是四叶草等级$k$的加成倍数
- $A_{VIP}(v)$ 是VIP等级$v$的加成
- $A_{guild}(g)$ 是公会等级$g$的加成

### 期望成本计算（不考虑惩罚）

传统的期望成本计算公式为：

$$C_{expected} = \frac{C_{materials}}{p_{success}}$$

其中：
- $C_{materials}$ 是材料成本（副卡价值+四叶草价值）
- $p_{success}$ 是成功率

### 期望成本计算（考虑惩罚因子）

在考虑失败降级惩罚的情况下，我们引入惩罚因子：

$$C_{expected} = \frac{C_{materials}}{p_{success}} \times PF(i)$$

其中，$PF(i)$是通过蒙特卡洛模拟得出的惩罚因子，反映了失败降级对总成本的影响。

### 性价比计算

性价比定义为成功率与期望成本的比值：

$$CE = \frac{p_{success}}{C_{expected}}$$

这个指标同时考虑了成功率和成本，用于选择最优策略。

## 蒙特卡洛模拟原理

### 为什么需要蒙特卡洛模拟

在传统的期望成本计算中，我们假设每次强化尝试是独立的，且失败不会影响后续尝试。然而，在游戏中，当主卡星级≥6时，失败会导致卡片降级，这使得传统的期望成本计算方法不再准确。

蒙特卡洛模拟通过大量随机实验来近似计算实际期望成本，考虑了失败降级的影响。

### 蒙特卡洛模拟过程

1. 对于每个星级$i$（从6星开始）：
   a. 模拟大量（如10,000次）强化尝试
   b. 对于每次模拟：
      - 从初始星级开始
      - 重复尝试强化，直到成功达到目标星级
      - 记录所需的尝试次数和材料成本
   c. 计算平均尝试次数和平均材料成本
   d. 计算惩罚因子：$PF(i) = \frac{实际期望成本}{理论期望成本}$

### 惩罚因子的意义

惩罚因子$PF(i)$表示实际期望成本与理论期望成本的比值。通常$PF(i) < 1$，这是因为：

1. 失败降级后，我们需要从较低星级重新开始强化
2. 较低星级的强化成本通常低于当前星级
3. 较低星级的成功率通常高于当前星级

这种"降级后重新强化"的机制实际上降低了总体期望成本，因此惩罚因子通常小于1。

## 算法流程详解

### 1. 初始化

```python
# 加载惩罚因子
punishment_factors = load_punishment_factors()

# 存储各星级卡片的累计价值
Vcard_mins = [1e9] * (STAR_LIMIT + 1)
# 存储各星级卡片的强化成本
cost_mins = [float('inf')] * (STAR_LIMIT + 1)
# 存储各星级卡片的最佳性价比
best_cost_effectiveness = [0] * (STAR_LIMIT + 1)
Vcard_mins[0] = 1
best_strategy = [""] * (STAR_LIMIT + 1)
```

### 2. 对每个星级计算最优策略

#### 对于1星卡片

```python
p3 = p_list[3][i]  # 同星副卡的基础成功率
cost_mins[i] = Vcard_mins[0] / p3  # 期望成本
Vcard_mins[i] = Vcard_mins[0] + cost_mins[i]  # 累计价值
```

#### 对于2星卡片

考虑同星和低1星副卡的组合：

```python
for comb in combinations_2:  # 遍历所有可能的副卡组合
    cur_cost = 0  # 当前组合的材料成本
    cur_p = 0  # 当前组合的成功率
    
    # 计算基础成功率和材料成本
    for j in range(0, len(comb)):
        if comb[j] == 'same':  # 同星副卡
            if j == 0:  # 第一张卡
                cur_p = p3
            else:
                cur_p = min(cur_p + p3/3, 1)  # 后续卡增加1/3基础成功率
            cur_cost += Vcard_mins[i-1]  # 加上同星副卡的价值
        elif comb[j] == 'down1':  # 低1星副卡
            if j == 0:
                cur_p = p2
            else:
                cur_p = min(cur_p + p2/3, 1)
            cur_cost += Vcard_mins[i-2]  # 加上低1星副卡的价值
    
    # 保存不加四叶草时的成本和成功率
    without_addition_cost = cur_cost
    without_addition_p = cur_p
    
    # 对每种四叶草等级计算加成后的成功率和期望成本
    for k in range(0, len(clover_levels)):
        # 计算加成后的成功率
        cur_p = without_addition_p*clover_additions[k]*(1 + guild_additions[cur_guild] + VIP_additions[cur_vip])
        if cur_p > 1:
            cur_p = 1
        
        # 计算总材料成本（副卡+四叶草）
        cur_cost = without_addition_cost + Vclovers[k]
        
        # 计算期望成本，考虑惩罚因子
        expected_cost = calculate_expected_cost(
            current_star=i-1,
            target_star=i,
            success_rate=cur_p,
            card_value=cur_cost,
            punishment_factors=punishment_factors
        )
        
        # 计算性价比
        cost_effectiveness = cur_p / expected_cost if expected_cost > 0 else 0
        
        # 更新最优策略
        if cost_effectiveness > best_cost_effectiveness[i]:
            best_cost_effectiveness[i] = cost_effectiveness
            cost_mins[i] = expected_cost
            Vcard_mins[i] = Vcard_mins[i-1] + cost_mins[i]
            # 更新策略信息...
```

#### 对于3星及以上卡片

考虑同星、低1星和低2星副卡的组合，处理逻辑与2星卡片类似，但增加了低2星副卡的考虑。

### 3. 计算期望成本（考虑惩罚因子）

```python
def calculate_expected_cost(current_star, target_star, success_rate, card_value, punishment_factors):
    """计算从current_star强化到target_star的期望成本，考虑惩罚因子"""
    if current_star >= target_star:
        return 0
    
    if success_rate <= 0:
        return float('inf')
    
    # 理论成本 = 卡片价值 / 成功率
    theoretical_cost = card_value / success_rate
    
    # 如果星级 >= 7，应用惩罚因子
    if target_star >= 7:
        return theoretical_cost * punishment_factors[target_star]
    else:
        return theoretical_cost
```

## 蒙特卡洛模拟实现

### 模拟单次强化过程

```python
def simulate_single_enhancement(start_star, target_star, success_rates, downgrade_levels):
    """模拟单次从start_star强化到target_star的过程"""
    current_star = start_star
    attempts = 0
    material_cost = 0
    
    while current_star < target_star:
        attempts += 1
        # 获取当前星级的成功率
        success_rate = success_rates[current_star]
        # 模拟强化结果
        if random.random() < success_rate:
            # 成功，星级+1
            current_star += 1
        else:
            # 失败，如果星级>=6，则降级
            if current_star >= 6 and current_star in downgrade_levels:
                current_star -= downgrade_levels[current_star]
        
        # 累加材料成本（这里简化为1，实际应该是卡片价值）
        material_cost += 1
    
    return attempts, material_cost
```

### 批量模拟并计算惩罚因子

```python
def calculate_punishment_factors(success_rates, downgrade_levels, num_simulations=10000):
    """通过蒙特卡洛模拟计算惩罚因子"""
    punishment_factors = {}
    
    for target_star in range(7, STAR_LIMIT + 1):
        start_star = target_star - 1
        
        # 理论尝试次数 = 1/成功率
        theoretical_attempts = 1 / success_rates[start_star]
        
        # 模拟多次强化过程
        total_attempts = 0
        total_material_cost = 0
        
        for _ in range(num_simulations):
            attempts, material_cost = simulate_single_enhancement(
                start_star, target_star, success_rates, downgrade_levels
            )
            total_attempts += attempts
            total_material_cost += material_cost
        
        # 计算平均尝试次数和材料成本
        avg_attempts = total_attempts / num_simulations
        avg_material_cost = total_material_cost / num_simulations
        
        # 计算惩罚因子 = 实际期望成本 / 理论期望成本
        punishment_factor = avg_material_cost / theoretical_attempts
        punishment_factors[target_star] = punishment_factor
    
    return punishment_factors
```

## 结论与应用

通过引入惩罚因子，我们的模型能够更准确地反映游戏中卡片强化的实际成本，特别是考虑到失败降级的影响。这种方法结合了理论计算和蒙特卡洛模拟，为玩家提供了更优的强化策略决策。

模型的主要应用包括：

1. 为不同VIP等级和公会等级的玩家提供最优强化策略
2. 计算各星级卡片的实际价值和强化成本
3. 评估不同强化方案的性价比
4. 帮助玩家在资源有限的情况下做出最优决策

通过这种数学模型，玩家可以最大化资源利用效率，减少强化过程中的浪费，更快地提升卡片星级。