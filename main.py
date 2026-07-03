from sat_solver import Ext, ExtClass, SATSolver, Differential
import sys


def main():
    a1 = ExtClass((0, 0, 0), [True])
    #a2 = ExtClass((0, 0, 0), [False, True])
    #a_sum = a1 + a2

    b1 = ExtClass((0, 1, 1), [True])
    #b2 = ExtClass((0, 1, 1), [False, True])
    #b_sum = b1 + b2

    diff1 = Differential(a1, b1, 1)
    #diff2 = Differential(a2, b2, 1)

    ext = Ext()
    #ext.add_classes([a1, a2, a_sum, b1, b2, b_sum])
    ext.add_classes([a1, b1])
    ext.add_known_differentials([diff1])

    sat_solver = SATSolver(ext, 2, 2)

    all_models = sat_solver.run_sat_solver()
    print("\nnumber of models: ", len(all_models))

    idx1 = int(sys.argv[1])
    idx2 = int(sys.argv[2])
    print_model_diffs(all_models, idx1, idx2)


def print_model_diffs(all_models, idx1, idx2):
    """ all_models[i] is a list of differentials that are true in model i """
    if len(all_models) > max(idx1, idx2):
        m1 = all_models[idx1]
        m2 = all_models[idx2]
        print(f"\nIn model {idx1} but not model {idx2}: ")
        for x in m1:
            if x not in m2:
                print(x)
        print(f"\nIn model {idx2} but not model {idx1}: ")
        for x in m2:
            if x not in m1:
                print(x)
    else:
        print("not enough solutions")


if __name__ == "__main__":
    main()
