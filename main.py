from sat_solver import E1CsvParser, Ext, ExtClass, SATSolver, Differential
import sys

ZeroClass: ExtClass = ExtClass(None, [True])
Undefined: ExtClass = ExtClass(None, [False])


def main():
    E1 = E1CsvParser("ext_data/Adams-motivic-E2-machine.csv",  2, only_one_N=True)
    all_classes = E1.make_all_lin_combs()
    ext_classes = [ExtClass(*x) for x in all_classes]
    for x in ext_classes:
        print(E1.class_name(x.get_degree(), x.get_vector()), x.get_degree())
    ext = Ext()
    ext.add_classes(ext_classes)
    t2, t1h0, h02, th1 = ext_classes
    diff1 = Differential(t2, th1, 2)


    ext.add_known_differentials([diff1])

    sat_solver = SATSolver(ext, 5, 5)

    all_models = sat_solver.run_sat_solver()
    print("\nnumber of models: ", len(all_models))

#    idx1 = int(sys.argv[1])
#    idx2 = int(sys.argv[2])
#    print_model_diffs(all_models, idx1, idx2)

#    if all_models:
#        for x in all_models[0]:
#            print(x)
#    else:
#        print("No models found")





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
