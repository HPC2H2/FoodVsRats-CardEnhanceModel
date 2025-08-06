# Food vs Rats Card Enhancement Model with Punishment

This project implements an optimized decision model for card enhancement in the "Food vs Rats" game, with a focus on calculating the true value of cards when considering failure penalties for high-star enhancements.

## Project Overview

The model calculates the optimal strategy for enhancing cards from lower star levels to higher star levels, taking into account:

1. Base card value (0-star cards)
2. Enhancement material requirements
3. Success probabilities based on card combinations
4. VIP and guild bonuses
5. Four-leaf clover value and effects
6. **Failure penalties for high-star enhancements (6→7 stars and above)**

## Files in this Project

- `model_with_addition.py`: Original model that considers four-leaf clover and other bonuses, but without failure penalties
- `model_with_punishment.py`: Enhanced model that incorporates failure penalties using Monte Carlo simulation
- `punishment_simulation.py`: Utility for analyzing punishment values in detail
- `strategy_builder.py`: Helper class for building enhancement strategies
- `generate_combinations.py`: Utility for generating all possible card combinations

## Punishment Model

When enhancing cards from 6-star to 7-star and above, there's a risk of failure that results in the card being downgraded. This significantly impacts the true value of high-star cards.

The punishment model uses Monte Carlo simulation to calculate the expected cost of enhancing cards with failure penalties:

1. For each enhancement attempt, we simulate the outcome based on the success probability
2. If the enhancement fails, the card is downgraded according to the downgrade level configuration
3. We continue attempting enhancements until we reach the target star level
4. After many simulations, we calculate the average cost, which represents the true expected cost

## Punishment Factors

The punishment factor for each star level is calculated as:

```
Punishment Factor = Simulated Cost with Failure / Theoretical Cost without Failure
```

These factors represent how much more expensive it is to enhance cards when considering failure penalties.

## Usage

To run the model with punishment:

```bash
python model_with_punishment.py
```

To analyze punishment factors in detail:

```bash
python punishment_simulation.py
```

## Results

The model outputs JSON files containing:

1. Optimal enhancement strategies for each star level
2. Card values at each star level
3. Enhancement costs at each star level
4. Punishment factors for high-star enhancements

These results can be used to make informed decisions about card enhancement in the game.

## Future Improvements

- Implement more sophisticated downgrade models (e.g., variable downgrade levels)
- Consider alternative enhancement paths
- Optimize simulation performance for faster calculations
- Add a user interface for easier interaction with the model
- Incorporate real-world data to refine success probabilities
- Add sensitivity analysis for different parameter configurations
