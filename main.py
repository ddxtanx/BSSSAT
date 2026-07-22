from sat_solver import E1CsvParser, Ext, ExtClass, SATSolver, Differential
import sys

ZeroClass: ExtClass = ExtClass(None, [True])
Undefined: ExtClass = ExtClass(None, [False])

max_N = 4
max_differential_degree = 5

def main():
    E1 = E1CsvParser("ext_data/Adams-motivic-E2-machine.csv", max_N, only_one_N=False)  # s+f-w = 2
    #print(E1.sfw_dict)
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

##adding known differentials on tau powers.

    k = 0

    while 2**k <= max_N:
        r = 2**k
        if r == 1:
            target_tau_power = 0
        else:
            target_tau_power = 2 ** (k - 1)

        source_degree = (0, 0, -r)
        target_degree = (r - 1, 1, 0)

        # Skip differentials whose classes are not on the loaded E1 page. (we don't really need)
        if (
            source_degree not in E1.sfw_dict
            or target_degree not in E1.sfw_dict
        ):
            k += 1
            continue

        source_name = f"tau^{r} {{0-0}}"
        target_name = f"tau^{target_tau_power} {{1-{k}}}"

        source = ExtClass(source_degree,[True])

        target = ExtClass(target_degree, E1.vector_by_basis_name(target_degree, target_name),)

        ext.add_known_differential(Differential(source, target, r))

        k += 1



 
    # print("\nKnown differentials:")
    # for diff in ext.known_differentials:
    #     r = diff.degree_of_differential
    #     source_name = E1.class_name(diff.source.get_degree(), diff.source.get_vector())
    #     target_name = E1.class_name(diff.target.get_degree(), diff.target.get_vector())
    #     print(f"d_{r}: ", source_name, " -> ", target_name) 

    sat_solver = SATSolver(ext, max_differential_degree)
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
