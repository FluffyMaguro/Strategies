"""
Calculating game-theoretic matrix of strategies and how it evolves with player skill.

Assumptions and simplifications in this model:
- Considering only three strategies (allin, defensive, and standard)
- Representing strategy advantage over another strategy as ELO bonus
- Representing player skill as ELO
- When one player executes an allin, the skill difference is reduce. Doubly if it's allin vs allin.

"""

import math
from enum import Enum, auto

from payoffmatrix import MixedStrategyResult, PayoffMatrix


class ST(Enum):
    """ Strategies """
    allin = auto()
    standard = auto()
    defensive = auto()


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
        c_allin_defensive = calc_elo_diff(0.35)
        c_defensive_standard = calc_elo_diff(0.40)
        c_allin_standard = calc_elo_diff(0.55)

        # Fill offset data first
        # Format: (P1 strat, P2 strat)
        self.strats[(ST.allin, ST.allin)] = 0
        self.strats[(ST.allin, ST.defensive)] = c_allin_defensive
        self.strats[(ST.allin, ST.standard)] = c_allin_standard

        self.strats[(ST.defensive, ST.allin)] = -c_allin_defensive
        self.strats[(ST.defensive, ST.defensive)] = 0
        self.strats[(ST.defensive, ST.standard)] = c_defensive_standard

        self.strats[(ST.standard, ST.allin)] = -c_allin_standard
        self.strats[(ST.standard, ST.defensive)] = -c_defensive_standard
        self.strats[(ST.standard, ST.standard)] = 0

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
        [P1↓ P2→]        Allin  Defensive   Standard
        Allin              50%        35%        55%
        Defensive          65%        50%        40%
        Standard           45%        60%        50%
        """
        s = [
            f"""{'[P1↓ P2→]':11}{'Allin':>11}{'Defensive':>11}{'Standard':>11}\n"""
        ]
        for p1strat in ST:
            s.append(f"{p1strat.name.capitalize():11}")
            for p2strat in ST:
                s.append(f"{self.strats[(p1strat,p2strat)]:>11.0%}")
            s.append("\n")
        return "".join(s)

    def print_result(self, result: MixedStrategyResult):
        p1rates = dict(zip(ST, result.p1_dist))
        p2rates = dict(zip(ST, result.p2_dist))
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

    def calculate_mixed_strategy(self):
        """ """
        # Create the payoff matrix
        m = []
        for p1strat in ST:
            m.append([])
            for p2strat in ST:
                m[-1].append(self.strats[(p1strat, p2strat)])

        matrix = PayoffMatrix(m)
        return matrix.solve()
