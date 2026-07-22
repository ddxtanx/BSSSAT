import sys
from pathlib import Path

# Allow this file to be run directly even when the editable install is unavailable.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from sat_solver import E1CsvParser, Ext, ExtClass, SATSolver, Differential

ZeroClass: ExtClass = ExtClass(None, [True])
Undefined: ExtClass = ExtClass(None, [False])



def main():
    E1 = E1CsvParser("ext_data/Adams-motivic-E2-machine.csv", 2, only_one_N=True)  # s+f-w = 2
    print(E1.sfw_dict)
    all_classes = E1.make_all_lin_combs()
    ext_classes = [ExtClass(*x) for x in all_classes]
    print("number of E1 classes: ", len(ext_classes))
    for x in ext_classes:
        print(E1.class_name(x.get_degree(), x.get_vector()), x.get_degree())
    ext = Ext()
    ext.add_classes(ext_classes)

    # comment out these four lines if you want to try a different N = s+f-w
    # t2, t1h0, h02, th1 = ext_classes
    # print("\nAdding known differential d_2(t^2) = t h1")
    # diff1 = Differential(t2, th1, 2)
    # ext.add_known_differentials([diff1])


    sat_solver = SATSolver(ext, 5)
    all_models = sat_solver.run_sat_solver()
    print("\nnumber of SAT variables: ", len(sat_solver.literal_manager.differentials))
    print("\nnumber of possible solutions to the system: ", len(all_models))


    if all_models:
        print("\nPrinting one possible solution")
        for diff in all_models[0]:
            r = diff.degree_of_differential
            source_name = E1.class_name(diff.source.get_degree(), diff.source.get_vector())
            target_name = E1.class_name(diff.target.get_degree(), diff.target.get_vector())
            print(f"d_{r}: ", source_name, " -> ", target_name)
    else:
        print("The SAT problem is unsatisfiable")




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
