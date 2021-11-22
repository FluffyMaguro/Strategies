import matplotlib.pyplot as plt

from payoffmatrix import MixedStrategyResult
from strategies import ST, StrategyMatrix, calc_winrate

ALLIN_COEF = 0.5

# Calculate data
data: dict[int, MixedStrategyResult] = dict()
for elo_diff in range(-500, 500, 100):
    matrix = StrategyMatrix(elo_diff, 0, allin_coef=ALLIN_COEF)
    data[elo_diff] = matrix.calculate_mixed_strategy()

# Plotting
plt.rcParams['figure.dpi'] = 150
x = list(data)

# Expected payoff vs elo winrate using the same strategy
winrate = [data[diff].p1_expected_payoff for diff in data]
winrate_without_strats = [calc_winrate(diff, 0) for diff in data]

fig, ax = plt.subplots(1, 1)
ax.plot(x, winrate, label="winrate")
ax.plot(x, winrate_without_strats, label="winrate using the same strategy")
ax.set_xlabel("ELO difference")
ax.set_ylabel("Winrate")
ax.set_title(
    "The difference between winrate and winrate when using the same strategy")
ax.grid(alpha=0.2)
ax.legend()
plt.show()  #use fig here?

# Strategy frequency
fig, ax = plt.subplots(2, 1)
for i, strategy in enumerate(ST):
    strategy_freq = [data[diff].p1_dist[i] for diff in data]
    ax[0].plot(x, strategy_freq, label=strategy.name)

    strategy_freq = [data[diff].p2_dist[i] for diff in data]
    ax[1].plot(x, strategy_freq, label=strategy.name)

ax.set_xlabel("ELO difference")
ax.set_ylabel("Strategy frequency")
ax.set_title("Frequency of used strategies")
ax.grid(alpha=0.2)
ax.legend()
plt.show()  #use fig here?
