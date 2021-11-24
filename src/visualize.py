import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

from payoffmatrix import MixedStrategyResult
from strategies import ST, StrategyMatrix, calc_winrate

ALLIN_COEF = 0.5
MAX = 700


def calculate_data() -> dict[int, MixedStrategyResult]:
    data = dict()
    for elo_diff in range(-MAX, MAX + 1, 1):
        matrix = StrategyMatrix(elo_diff, 0, allin_coef=ALLIN_COEF)
        data[elo_diff] = matrix.calculate_mixed_strategy()
    return data


def plot_allin_coef_impact(data):
    x = list(data)
    winrate = [data[diff].p1_expected_payoff for diff in data]
    allins = [calc_winrate(diff * (ALLIN_COEF**2), 0) for diff in data]
    one_allins = [calc_winrate(diff * ALLIN_COEF, 0) for diff in data]
    winrate_without_strats = [calc_winrate(diff, 0) for diff in data]

    fig, ax = plt.subplots(1, 1, dpi=200)
    ax.plot(x, winrate_without_strats, label="Standard vs standard")
    ax.plot(x, winrate, label="Mixed strategies")
    ax.plot(x, one_allins, label=f"All-in vs not all-in (-{1-ALLIN_COEF:.0%})")
    ax.plot(x, allins, label=f"All-in vs all-in (-{1-ALLIN_COEF**2:.0%})")
    ax.plot(x, 0.5 * np.ones(len(x)), 'k--', alpha=0.5, linewidth=0.5)
    ax.plot([0, 0], [0, 1], 'k--', alpha=0.5, linewidth=0.5)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_xlabel("ELO difference")
    ax.set_ylabel("Winrate")
    ax.set_title(
        f"The impact of having certain strategies reflect skill less"
        f"\nOne all-in is set to reduce ELO difference by {1-ALLIN_COEF:.0%}")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig("img/reduction.png")


# Strategy frequency
def plot_strategy_frequency(data):
    x = list(data)
    zeros = np.zeros(len(x))
    fig, ax = plt.subplots(2, 1, figsize=(7, 8), dpi=200)

    frequencies = [[], []]
    labels = [e.name.capitalize().replace("Allin", "All-in") for e in ST]
    for i, _ in enumerate(ST):
        frequencies[0].append([data[diff].p1_dist[i] for diff in data])
        frequencies[1].append([data[diff].p2_dist[i] for diff in data])

    for i in range(2):
        ax[i].stackplot(x,
                        *frequencies[i],
                        labels=labels,
                        alpha=0.5,
                        edgecolor="k",
                        linewidth=0.5)
        labels = [f"P2 {l}".replace("Allin", "All-in") for l in labels]

    # Plot P1 winrate
    p1winrate = [data[diff].p1_expected_payoff for diff in data]
    ax[0].plot(x, p1winrate, '-.', label="winrate", alpha=0.7, linewidth=1)

    # Find and plot breakpoints where there is a different number of strategies viable
    breakpoints = []
    viable_strategies = -1
    for diff in data:
        n = len([i for i in data[diff].p1_dist if i != 0])
        if viable_strategies == -1:
            viable_strategies = n
        elif n != viable_strategies:
            viable_strategies = n
            breakpoints.append(diff)

    for i in range(2):
        for brk in breakpoints:
            ax[i].plot([brk, brk], [0, 1], 'k--', alpha=0.5, linewidth=0.5)
            ax[i].text(brk, 0.2, f"{brk}", ha="center", alpha=0.7)

    # Stylize
    ax[0].set_title("Frequency of used strategies")
    for i in range(2):
        ax[i].plot(x, 0.5 * np.ones(len(x)), 'k--', alpha=0.5, linewidth=0.5)
        ax[i].plot([0, 0], [0, 1], 'k--', alpha=0.5, linewidth=0.5)
        ax[i].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax[i].set_xlabel("ELO difference")
        ax[i].set_ylabel("Strategy frequency")
        ax[i].grid(alpha=0.2)
        ax[i].legend(loc="upper left")

    fig.tight_layout()
    fig.savefig("img/strategy_frequency.png")


if __name__ == "__main__":
    data = calculate_data()
    plot_allin_coef_impact(data)
    plot_strategy_frequency(data)
