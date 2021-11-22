from solutions import solve_for_two
from payoffmatrix import PayoffMatrix


# m_p1 = [[2,1,4],[3,1,2], [1,0,3.]]
# m_p2_t = [[],[], []]


# matrix = PayoffMatrix(m_p1)
# p2dist, p1dist = matrix.solve()

# # print(p1dist)
# print(p2dist)

m = [[2., 4], [3,2]]
a = solve_for_two(m)
print("P2", a, 1 - a)


m = [[0., 4], [2, 3]]
a = solve_for_two(m)
print("P1", a, 1 - a)
