from dataclasses import dataclass, field
from pprint import pprint

import solutions


@dataclass
class MixedStrategyResult:
    p1_dist: list[float] = field(default_factory=list)
    p2_dist: list[float] = field(default_factory=list)
    p1_expected_payoff: float = -1
    p2_expected_payoff: float = -1


class PayoffMatrix:
    """ Class for payoff matrix that also tracks which columns 
    and rows are still there from the original matrix

    This is for a special case where the other player payoff 
    matrix is 1-payoff.

    Manages only up-to 3 strategies."""
    def __init__(self, m: list[list[float]]):
        self.m = m
        self.rows = [i for i in range(len(m))]
        self.columns = [i for i in range(len(m[0]))]
        self.original_nrows = self.n_rows
        self.original_ncolumns = self.n_columns

    def remove_row(self, index):
        print("Removing row:   ", index)
        self.rows.pop(index)
        self.m.pop(index)

    def remove_column(self, index):
        print("Removing column:", index)
        self.columns.pop(index)
        for row in self.m:
            row.pop(index)

    @property
    def n_rows(self):
        return len(self.rows)

    @property
    def n_columns(self):
        return len(self.columns)

    def check_rows(self):
        """ Checks if all rows correspond to rationalizable strategies """
        invalid_strats = {i for i in range(self.n_rows)}

        for column_index in range(self.n_columns):
            col = [self.m[i][column_index] for i in range(self.n_rows)]
            index = col.index(max(col))
            if index in invalid_strats:
                invalid_strats.remove(index)

        if invalid_strats:
            index = tuple(invalid_strats)[0]
            self.remove_row(index)

    def check_columns(self):
        """ Checks if all columns correspond to rationalizable strategies
        This assumes payoff for the other player = 1 - payoff """
        invalid_strats = {i for i in range(self.n_columns)}

        for row in self.m:
            index = row.index(min(row))
            if index in invalid_strats:
                invalid_strats.remove(index)

        if invalid_strats:
            index = tuple(invalid_strats)[0]
            self.remove_column(index)

    def reduce_to_rationalizable_strategies(self):
        """ Reduces the matrix to only rationalizable strategies by checking rows and columns """
        for _ in range(max(self.n_rows, self.n_columns)):
            self.check_rows()
            self.check_columns()

    def second_player_matrix(self) -> list[list[float]]:
        """ Transposes and substracts from 1
            = 1 - A_transposed """
        matrix = []
        for column_index in range(self.n_columns):
            matrix.append([])
            for row in self.m:
                matrix[-1].append(1 - row[column_index])

        return matrix

    def solve(self) -> MixedStrategyResult:
        """ Solves the payoff matrix for both P1 and P2.
        Payoff for P2 are assumed to be 1 - payoffs.
        """
        result = self._solve()
        # Print matrix if it changed
        if len(self.m) != self.original_nrows:
            pprint(self.m)

        return result

    def _solve(self) -> MixedStrategyResult:
        self.reduce_to_rationalizable_strategies()

        result = MixedStrategyResult()
        result.p1_dist = [0] * self.original_nrows
        result.p2_dist = [0] * self.original_ncolumns

        if self.n_columns == 1 and self.n_rows == 1:
            print("Solved with one pure strategy!")
            # We have saved which columns/rows were left in rational moves
            result.p1_expected_payoff = self.m[0][0]
            result.p2_expected_payoff = 1 - self.m[0][0]
            result.p1_dist[self.rows[0]] = 1
            result.p2_dist[self.columns[0]] = 1

        elif self.n_columns == 2 and self.n_rows == 2:
            print("Solved with a mix of two strategies!")
            a, result.p2_expected_payoff = solutions.solve_for_two(self.m)
            result.p2_dist[self.columns[0]] = a
            result.p2_dist[self.columns[1]] = 1 - a

            a, result.p1_expected_payoff = solutions.solve_for_two(
                self.second_player_matrix())
            result.p1_dist[self.rows[0]] = a
            result.p1_dist[self.rows[1]] = 1 - a

        elif self.n_columns == 3 and self.n_rows == 3:
            print("Solving with a mix of three strategies!")
            result.p2_dist, result.p2_expected_payoff = solutions.solve_for_three(
                self.m)
            result.p1_dist, result.p1_expected_payoff = solutions.solve_for_three(
                self.second_player_matrix())

            # If there are some negative chances, remove those columns/row and recursively solve
            if any(i < 0 for i in result.p1_dist + result.p2_dist):
                if any(i < 0 for i in result.p1_dist):
                    index = result.p1_dist.index(min(result.p1_dist))
                    print("Negative index at row:", index)
                    self.remove_row(index)

                if any(i < 0 for i in result.p2_dist):
                    index = result.p2_dist.index(min(result.p2_dist))
                    print("Negative index at column:", index)
                    self.remove_column(index)

                return self._solve()

        else:
            print("Error, this shouldn't happen!")
            pprint(self.m)

        return result
