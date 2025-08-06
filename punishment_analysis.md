# Food vs Rats Card Enhancement Model Implementation (with Punishment Mechanism)

## Model Overview

This model is designed for the card enhancement system in the game "Food vs Rats," considering four-leaf clover bonuses and failure downgrade penalties for optimal decision-making. When the main card is above 6 stars, Monte Carlo simulation is used to determine the punishment values.

## Mathematical Model and Symbol Definitions

### Basic Symbol Definitions

- $p_{i,j}$: Base success rate for enhancing from star level $i$ to star level $j$ using a sub-card
- $V_{card}(i)$: Cumulative value of a card at star level $i$
- $C_{min}(i)$: Minimum expected cost to enhance from star level $i-1$ to $i$
- $CE(i)$: Best cost-effectiveness ratio (success rate/cost) for star level $i$
- $A_{clover}(k)$: Success rate multiplier provided by four-leaf clover level $k$
- $A_{VIP}(v)$: Success rate bonus provided by VIP level $v$
- $A_{guild}(g)$: Success rate bonus provided by guild level $g$
- $V_{clover}(k)$: Value of four-leaf clover level $k$
- $PF(i)$: Punishment factor for star level $i$

### Success Rate Calculation

For cases using multiple sub-cards, the success rate is calculated as follows:
1. The first card's success rate is the base success rate $p_{i,j}$
2. Each subsequent card increases the base success rate by 1/3, with a maximum total success rate of 1
3. Apply four-leaf clover, VIP, and guild bonuses:

$$p_{final} = \min(p_{base} \times A_{clover}(k) \times (1 + A_{VIP}(v) + A_{guild}(g)), 1)$$

Where:
- $p_{base}$ is the base success rate (after considering multiple sub-cards)
- $A_{clover}(k)$ is the multiplier from four-leaf clover level $k$
- $A_{VIP}(v)$ is the bonus from VIP level $v$
- $A_{guild}(g)$ is the bonus from guild level $g$

### Expected Cost Calculation (Without Punishment)

The traditional expected cost calculation formula is:

$$C_{expected} = \frac{C_{materials}}{p_{success}}$$

Where:
- $C_{materials}$ is the material cost (sub-card value + four-leaf clover value)
- $p_{success}$ is the success rate

### Expected Cost Calculation (With Punishment Factor)

When considering failure downgrade penalties, we introduce a punishment factor:

$$C_{expected} = \frac{C_{materials}}{p_{success}} \times PF(i)$$

Where $PF(i)$ is the punishment factor determined through Monte Carlo simulation, reflecting the impact of failure downgrades on total cost.

### Cost-Effectiveness Calculation

Cost-effectiveness is defined as the ratio of success rate to expected cost:

$$CE = \frac{p_{success}}{C_{expected}}$$

This metric considers both success rate and cost simultaneously, used for selecting the optimal strategy.

## Monte Carlo Simulation Principles

### Why Monte Carlo Simulation is Needed

In traditional expected cost calculations, we assume each enhancement attempt is independent, and failure doesn't affect subsequent attempts. However, in the game, when the main card's star level is ≥6, failure causes the card to downgrade, making traditional expected cost calculation methods inaccurate.

Monte Carlo simulation approximates the actual expected cost through numerous random experiments, considering the impact of failure downgrades.

### Monte Carlo Simulation Process

1. For each star level $i$ (starting from 6):
   a. Simulate a large number (e.g., 10,000) of enhancement attempts
   b. For each simulation:
      - Start from the initial star level
      - Repeatedly attempt enhancement until successfully reaching the target star level
      - Record the number of attempts and material costs required
   c. Calculate the average number of attempts and average material cost
   d. Calculate the punishment factor: $PF(i) = \frac{actual\ expected\ cost}{theoretical\ expected\ cost}$

### Significance of the Punishment Factor

The punishment factor $PF(i)$ represents the ratio of actual expected cost to theoretical expected cost. Typically $PF(i) < 1$, because:

1. After a failure downgrade, we need to restart enhancement from a lower star level
2. The enhancement cost for lower star levels is usually lower than the current star level
3. The success rate for lower star levels is usually higher than the current star level

This "downgrade and re-enhance" mechanism actually reduces the overall expected cost, so the punishment factor is usually less than 1.

## Detailed Algorithm Flow

### 1. Initialization

```python
# Load punishment factors
punishment_factors = load_punishment_factors()

# Store cumulative value of cards at each star level
Vcard_mins = [1e9] * (STAR_LIMIT + 1)
# Store enhancement cost for each star level
cost_mins = [float('inf')] * (STAR_LIMIT + 1)
# Store best cost-effectiveness for each star level
best_cost_effectiveness = [0] * (STAR_LIMIT + 1)
Vcard_mins[0] = 1
best_strategy = [""] * (STAR_LIMIT + 1)
```

### 2. Calculate Optimal Strategy for Each Star Level

#### For 1-Star Cards

```python
p3 = p_list[3][i]  # Base success rate for same-star sub-card
cost_mins[i] = Vcard_mins[0] / p3  # Expected cost
Vcard_mins[i] = Vcard_mins[0] + cost_mins[i]  # Cumulative value
```

#### For 2-Star Cards

Consider combinations of same-star and 1-star-lower sub-cards:

```python
for comb in combinations_2:  # Iterate through all possible sub-card combinations
    cur_cost = 0  # Current combination's material cost
    cur_p = 0  # Current combination's success rate
    
    # Calculate base success rate and material cost
    for j in range(0, len(comb)):
        if comb[j] == 'same':  # Same-star sub-card
            if j == 0:  # First card
                cur_p = p3
            else:
                cur_p = min(cur_p + p3/3, 1)  # Subsequent cards add 1/3 of base success rate
            cur_cost += Vcard_mins[i-1]  # Add same-star sub-card value
        elif comb[j] == 'down1':  # 1-star-lower sub-card
            if j == 0:
                cur_p = p2
            else:
                cur_p = min(cur_p + p2/3, 1)
            cur_cost += Vcard_mins[i-2]  # Add 1-star-lower sub-card value
    
    # Save cost and success rate without four-leaf clover
    without_addition_cost = cur_cost
    without_addition_p = cur_p
    
    # Calculate success rate and expected cost with four-leaf clover bonuses
    for k in range(0, len(clover_levels)):
        # Calculate success rate with bonuses
        cur_p = without_addition_p*clover_additions[k]*(1 + guild_additions[cur_guild] + VIP_additions[cur_vip])
        if cur_p > 1:
            cur_p = 1
        
        # Calculate total material cost (sub-cards + four-leaf clover)
        cur_cost = without_addition_cost + Vclovers[k]
        
        # Calculate expected cost, considering punishment factor
        expected_cost = calculate_expected_cost(
            current_star=i-1,
            target_star=i,
            success_rate=cur_p,
            card_value=cur_cost,
            punishment_factors=punishment_factors
        )
        
        # Calculate cost-effectiveness
        cost_effectiveness = cur_p / expected_cost if expected_cost > 0 else 0
        
        # Update optimal strategy
        if cost_effectiveness > best_cost_effectiveness[i]:
            best_cost_effectiveness[i] = cost_effectiveness
            cost_mins[i] = expected_cost
            Vcard_mins[i] = Vcard_mins[i-1] + cost_mins[i]
            # Update strategy information...
```

#### For 3-Star and Above Cards

Consider combinations of same-star, 1-star-lower, and 2-star-lower sub-cards, with logic similar to 2-star cards but adding consideration for 2-star-lower sub-cards.

### 3. Calculate Expected Cost (Considering Punishment Factor)

```python
def calculate_expected_cost(current_star, target_star, success_rate, card_value, punishment_factors):
    """Calculate the expected cost to enhance from current_star to target_star, considering punishment factors"""
    if current_star >= target_star:
        return 0
    
    if success_rate <= 0:
        return float('inf')
    
    # Theoretical cost = card value / success rate
    theoretical_cost = card_value / success_rate
    
    # If star level >= 7, apply punishment factor
    if target_star >= 7:
        return theoretical_cost * punishment_factors[target_star]
    else:
        return theoretical_cost
```

## Monte Carlo Simulation Implementation

### Simulating a Single Enhancement Process

```python
def simulate_single_enhancement(start_star, target_star, success_rates, downgrade_levels):
    """Simulate a single enhancement process from start_star to target_star"""
    current_star = start_star
    attempts = 0
    material_cost = 0
    
    while current_star < target_star:
        attempts += 1
        # Cost of each attempt is the value of the current star level card
        attempt_cost = base_card_values[current_star]
        material_cost += attempt_cost
        
        # Check if enhancement is successful
        if random.random() < success_rates[current_star+1]:
            # Success, star level +1
            current_star += 1
        else:
            # Failure - if star level >= 6, downgrade
            if current_star >= 6 and current_star in downgrade_levels:
                current_star -= downgrade_levels[current_star]
        
        # Add material cost (simplified as 1 here, should be card value in reality)
        material_cost += 1
    
    return attempts, material_cost
```

### Batch Simulation and Punishment Factor Calculation

```python
def calculate_punishment_factors(success_rates, downgrade_levels, num_simulations=10000):
    """Calculate punishment factors through Monte Carlo simulation"""
    punishment_factors = {}
    
    for target_star in range(7, STAR_LIMIT + 1):
        start_star = target_star - 1
        
        # Theoretical number of attempts = 1/success rate
        theoretical_attempts = 1 / success_rates[start_star]
        
        # Simulate multiple enhancement processes
        total_attempts = 0
        total_material_cost = 0
        
        for _ in range(num_simulations):
            attempts, material_cost = simulate_single_enhancement(
                start_star, target_star, success_rates, downgrade_levels
            )
            total_attempts += attempts
            total_material_cost += material_cost
        
        # Calculate average number of attempts and material cost
        avg_attempts = total_attempts / num_simulations
        avg_material_cost = total_material_cost / num_simulations
        
        # Calculate punishment factor = actual expected cost / theoretical expected cost
        punishment_factor = avg_material_cost / theoretical_attempts
        punishment_factors[target_star] = punishment_factor
    
    return punishment_factors
```

## Conclusion and Application

By introducing punishment factors, our model can more accurately reflect the actual cost of card enhancement in the game, especially considering the impact of failure downgrades. This method combines theoretical calculation and Monte Carlo simulation to provide players with optimal enhancement strategy decisions.

The main applications of the model include:

1. Providing optimal enhancement strategies for players of different VIP and guild levels
2. Calculating the actual value and enhancement cost of cards at each star level
3. Evaluating the cost-effectiveness of different enhancement schemes
4. Helping players make optimal decisions when resources are limited

Through this mathematical model, players can maximize resource utilization efficiency, reduce waste in the enhancement process, and upgrade card star levels more quickly.