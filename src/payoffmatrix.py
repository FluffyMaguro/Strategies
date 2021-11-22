from pprint import pprint

import solutions


class PayoffMatrix:
    """ Class for payoff matrix that also tracks which columns 
    and rows are still there from the original matrix

    This is for a special case where the other player payoff 
    matrix is 1-payoff"""
    def __init__(self, m: list[list[float]]):
        self.m = m
        self.rows = [i for i in range(len(m))]
        self.columns = [i for i in range(len(m[0]))]
        self.original_nrows = self.n_rows
        self.original_ncolumns = self.n_columns

    def remove_row(self, index):
        print("Removing row:", index)
        self.rows.pop(index)
        self.m.pop(index)
        pprint(self.m)

    def remove_column(self, index):
        print("Removing column:", index)
        self.columns.pop(index)
        for row in self.m:
            row.pop(index)
        pprint(self.m)

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

    def solve(self) -> list[list[float]]:
        """ Solves the payoff matrix for both P1 and P2.
        Payoff for P2 are assumed to be 1 - payoffs.

        returns:
            [[mixing distributions for P2], [mixing distribution for P1]]

        """
        self.reduce_to_rationalizable_strategies()

        result: list[list[float]] = [[0] * self.original_ncolumns,
                                     [0] * self.original_nrows]

        if self.n_columns == 1 and self.n_rows == 1:
            print("Solved with one pure strategy!")
            print(
                f"row={self.rows[0]}, column={self.columns[0]}, value={self.m[0][0]}"
            )
            # We have saved which columns/rows were left in rational moves
            result[0][self.columns[0]] = 1
            result[1][self.rows[0]] = 1

        elif self.n_columns == 2 and self.n_rows == 2:
            print("Solved with a mix of two strategies!")
            a = solutions.solve_for_two(self.m)
            result[0][self.columns[0]] = a
            result[0][self.columns[1]] = 1 - a

            a = solutions.solve_for_two(self.second_player_matrix())
            result[1][self.rows[0]] = a
            result[1][self.rows[1]] = 1 - a

        elif self.n_columns == 3 and self.n_rows == 3:
            print("Solved with a mix of three strategies!")
            p, q, r = solutions.solve_for_three(self.m)
            a, b, c = solutions.solve_for_three(self.second_player_matrix())
            result = [[p, q, r], [a, b, c]]
        else:
            print("Error, this shouldn't happen!")
            pprint(self.m)

        return result
