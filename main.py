from sat_solver import Ext, ExtClass, SATSolver, Differential


def main():
    a1 = ExtClass((0, 0, 0), [True, False])
    a2 = ExtClass((0, 0, 0), [False, True])
    a_sum = a1 + a2

    b1 = ExtClass((0, 1, 1), [True, False])
    b2 = ExtClass((0, 1, 1), [False, True])
    b_sum = b1 + b2

    diff1 = Differential(a1, b1, 1)
    diff2 = Differential(a2, b2, 1)

    ext = Ext()
    ext.add_classes([a1, a2, a_sum, b1, b2, b_sum])
    ext.add_known_differentials([diff1, diff2])

    sat_solver = SATSolver(ext, 10, 10)

    sat_solver.run_sat_solver()


if __name__ == "__main__":
    main()
