def solve_for_two(m: list[list[float]]) -> float:
    """ Calculates a solution of two equations for one variables a:

    a*m00 + (1-a)*m01 =
    a*m10 + (1-a)*m11 

    param: matrix
        ((m00, m01)
         (m10, m11))

    returns: a
    """
    a = (m[1][1] - m[0][1]) / (m[0][0] - m[1][0] - m[0][1] + m[1][1])

    # Check if the result is correct
    res1 = a * m[0][0] + (1 - a) * m[0][1]
    res2 = a * m[1][0] + (1 - a) * m[1][1]
    if abs(res1 - res2) > 0.000001:
        print(f"Error: This should be equal!\n{res1} == {res2}")

    return a


def solve_for_three(m: list[list[float]]) -> tuple[float, float, float]:
    """ Calculates a solution of two equations for two variables a and b:

    a*m00 + b*m01 + (1-a-b)*m02 =
    a*m10 + b*m11 + (1-a-b)*m12 = 
    a*m20 + b*m21 + (1-a-b)*m22

    param: 
        matrix 
        ((m00, m01, m02)
         (m10, m11, m12)
         (m20, m21, m22))

    returns:
        (a,b, 1-a-b)
    """
    # pprint(m)

    # First change to two linear equations:
    # A * (a,b) = B
    A = ((m[0][0] - m[1][0] - m[0][2] + m[1][2],
          m[0][1] - m[1][1] - m[0][2] + m[1][2]),
         (m[1][0] - m[2][0] - m[1][2] + m[2][2],
          m[1][1] - m[2][1] - m[1][2] + m[2][2]))

    B = (m[1][2] - m[0][2], m[2][2] - m[1][2])

    # Now solve with elimination
    a = (A[1][1] * B[0] - A[0][1] * B[1]) / (A[0][0] * A[1][1] -
                                             A[0][1] * A[1][0])
    b = (B[0] - A[0][0] * a) / A[0][1]

    # Check if the result is correct
    res1 = m[0][0] * a + m[0][1] * b + (1 - a - b) * m[0][2]
    res2 = m[1][0] * a + m[1][1] * b + (1 - a - b) * m[1][2]
    res3 = m[2][0] * a + m[2][1] * b + (1 - a - b) * m[2][2]
    if abs(res1 - res2) > 0.000001 or abs(res2 - res3) > 0.000001:
        print(f"Error: This should be equal!\n{res1} == {res2} == {res3}")

    return (a, b, 1 - a - b)
