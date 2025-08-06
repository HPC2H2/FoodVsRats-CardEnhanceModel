# 美食大战老鼠卡片强化模型数学公式

## 符号定义

### 基本参数
- $S_i$: 星级为$i$的卡片
- $p_{i,j}$: 使用星级为$i$的副卡强化到星级$j$的基础成功率
- $V(S_i)$: 星级为$i$的卡片累计价值
- $C(S_{i-1} \rightarrow S_i)$: 从$i-1$星强化到$i$星的最小期望成本
- $CE(S_i)$: 星级为$i$的最佳性价比(成功率/成本)

### 加成参数
- $A_C(k)$: 四叶草等级$k$提供的成功率加成倍数
- $A_{VIP}(v)$: VIP等级$v$提供的成功率加成
- $A_G(g)$: 公会等级$g$提供的成功率加成
- $V_C(k)$: 四叶草等级$k$的价值

### 惩罚参数
- $PF(S_i)$: 星级$i$的惩罚因子
- $D(S_i)$: 星级$i$强化失败后的降级星数

## 成功率计算

### 单张副卡成功率
使用单张副卡时，基础成功率直接从成功率表中获取：
- 同星副卡: $p_{i,i+1}$
- 低1星副卡: $p_{i-1,i+1}$
- 低2星副卡: $p_{i-2,i+1}$

### 多张副卡成功率
对于使用多张副卡的情况，成功率计算如下：

1. 第一张卡的成功率为基础成功率 $p_{base}$
2. 后续每张卡增加基础成功率的1/3，但总成功率上限为1

$$p_{multi} = \min(p_{base} + \sum_{j=1}^{n-1} \frac{p_{j,base}}{3}, 1)$$

其中，$p_{j,base}$是第$j+1$张副卡的基础成功率。

### 应用加成后的成功率

$$p_{final} = \min(p_{multi} \times A_C(k) \times (1 + A_{VIP}(v) + A_G(g)), 1)$$

## 期望成本计算

### 传统期望成本（不考虑惩罚）

$$C_{traditional}(S_{i-1} \rightarrow S_i) = \frac{C_{materials}}{p_{final}}$$

其中，$C_{materials}$是材料成本（副卡价值+四叶草价值）。

### 考虑惩罚的期望成本

$$C(S_{i-1} \rightarrow S_i) = C_{traditional}(S_{i-1} \rightarrow S_i) \times PF(S_i)$$

## 性价比计算

$$CE(S_i) = \frac{p_{final}}{C(S_{i-1} \rightarrow S_i)}$$

## 惩罚因子计算

惩罚因子通过蒙特卡洛模拟计算：

$$PF(S_i) = \frac{C_{simulated}(S_{i-1} \rightarrow S_i)}{C_{traditional}(S_{i-1} \rightarrow S_i)}$$

其中：
- $C_{simulated}$是通过蒙特卡洛模拟得到的考虑失败降级的实际期望成本
- $C_{traditional}$是不考虑失败降级的理论期望成本

## 蒙特卡洛模拟算法

1. 初始化：当前星级 $current = i-1$，尝试次数 $attempts = 0$，材料成本 $cost = 0$
2. 循环直到 $current = i$：
   a. $attempts = attempts + 1$
   b. 生成随机数 $r \in [0,1]$
   c. 如果 $r < p_{final}$，则 $current = i$（成功）
   d. 否则，如果 $current \geq 6$，则 $current = current - D(S_{current})$（失败降级）
   e. $cost = cost + V(S_{current})$
3. 返回 $attempts$ 和 $cost$

通过大量重复上述模拟（如10,000次），计算平均成本，得到 $C_{simulated}$。