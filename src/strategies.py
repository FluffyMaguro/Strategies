"""
Calculating game-theoretic matrix of strategies and how it evolves with player skill.

Assumptions and simplifications in this model:
- Considering only three strategies (allin, standard, and greedy)
- Representing strategy advantage over another strategy as ELO bonus
- Representing player skill as ELO
- When executing allin, the skill difference (ELO points) matters only half as much

"""

import math
from enum import Enum, auto
from pprint import pprint

from payoffmatrix import MixedStrategyResult, PayoffMatrix


class ST(Enum):
    """ Strategies """
    allin = auto()
    standard = auto()
    greedy = auto()


def calc_winrate(p1elo: float, p2elo: float) -> float:
    """ Calculates winrate based on ELO of two players"""
    return 1 / (1 + math.exp((p2elo - p1elo) / 173.718))


def calc_elo_diff(winrate_diff: float) -> float:
    """ Calculates ELO difference based in winrate difference.
    Essentially an inverse function to calc_winrate."""
    return -173.718 * math.log((1 / winrate_diff) - 1)


class StrategyMatrix:
    def __init__(self, p1elo: float, p2elo: float, allin_coef: float = 0.5):
        self.allin_coef = allin_coef
        self.strats: dict[tuple[ST, ST], float] = dict()

        # BASE VALUES:
        # Calculate how big ELO offset would correspond to a winrate like that
        c_allin_standard = calc_elo_diff(0.45)
        c_standard_greedy = calc_elo_diff(0.45)
        c_allin_greedy = calc_elo_diff(0.9)

        # Fill offset data first
        # Format: (P1 strat, P2 strat)
        self.strats[(ST.allin, ST.allin)] = 0
        self.strats[(ST.allin, ST.standard)] = c_allin_standard
        self.strats[(ST.allin, ST.greedy)] = c_allin_greedy

        self.strats[(ST.standard, ST.allin)] = -c_allin_standard
        self.strats[(ST.standard, ST.standard)] = 0
        self.strats[(ST.standard, ST.greedy)] = c_standard_greedy

        self.strats[(ST.greedy, ST.allin)] = -c_allin_greedy
        self.strats[(ST.greedy, ST.standard)] = -c_standard_greedy
        self.strats[(ST.greedy, ST.greedy)] = 0

        # Then calculate win percentage based on the offset and player elo difference
        # Allins scale only with half amount of skill difference
        # The rest scales fully with skill difference
        skill_difference = p1elo - p2elo
        for strs in self.strats:
            if strs[0] == ST.allin and strs[1] == ST.allin:
                self.strats[strs] = calc_winrate(
                    skill_difference * (self.allin_coef**2) +
                    self.strats[strs], 0)
            elif strs[0] == ST.allin or strs[1] == ST.allin:
                self.strats[strs] = calc_winrate(
                    skill_difference * self.allin_coef + self.strats[strs], 0)
            else:
                self.strats[strs] = calc_winrate(
                    skill_difference + self.strats[strs], 0)

    def __str__(self):
        """ Produces an output like this:
        [P1↓ P2→]        Allin   Standard     Greedy
        Allin              50%        45%        90%
        Standard           55%        50%        45%
        Greedy             10%        55%        50%
        """
        s = [
            f"""{'[P1↓ P2→]':11}{'Allin':>11}{'Standard':>11}{'Greedy':>11}\n"""
        ]
        for p1strat in ST:
            s.append(f"{p1strat.name.capitalize():11}")
            for p2strat in ST:
                s.append(f"{self.strats[(p1strat,p2strat)]:>11.0%}")
            s.append("\n")
        return "".join(s)

    def calculate_mixed_strategy(self):
        """ """
        # Create the payoff matrix
        m = []
        for p1strat in ST:
            m.append([])
            for p2strat in ST:
                m[-1].append(self.strats[(p1strat, p2strat)])

        matrix = PayoffMatrix(m)
        result = matrix.solve()
        p1rates = dict(zip(ST, result.p1_dist))
        p2rates = dict(zip(ST, result.p2_dist))

        # Print
        print(
            f"P1: (exp-payoff: {result.p1_expected_payoff:.2f}) |",
            " | ".join([
                f"{k.name.capitalize()}: {v:.2%}" for k, v in p1rates.items()
            ]))
        print(
            f"P2: (exp-payoff: {result.p2_expected_payoff:.2f}) |",
            " | ".join([
                f"{k.name.capitalize()}: {v:.2%}" for k, v in p2rates.items()
            ]))


m = StrategyMatrix(200, 0, allin_coef=0.5)
print(m)
m.calculate_mixed_strategy()

# Calculated solution from a page (https://cgi.csc.liv.ac.uk/%7Erahul/bimatrix_solver/)
# Extreme Equilibrium
# P1:  (1)  0.078947  0.921053  0.000000  EP=  61.6052631579
# P2:  (1)  0.868421  0.000000  0.131579  EP=  38.3947368421
