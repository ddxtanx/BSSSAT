import csv
from collections import defaultdict
from itertools import product

class E1CsvParser:
    """
    This class handles the data contained in the csv file representing Ext over the C-motivic Steenrod algebra.q

    The set of BSS E1 classes with a fixed N = s+f-w degree is closed under rho-BSS differentials.
    Thus to avoid fringe issues we work with N <= max_N, which means we only consider
    Ext_AC classes with s+f-w <= max_N.
    """

    def __init__(self, filename: str, max_N, only_one_N: bool = False):
        self.max_N = max_N
        self.csv_classes = self.load_classes(filename)
        self.sfw_dict = self.make_sfw_grouping(only_one_N) # dictionary (s,f,w) -> list of E1 basis elements


    def load_classes(self, filename: str):
        classes = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                s = int(row['stem'])
                f = int(row['Adams filtration'])
                w = int(row['weight'])
                N = s + f - w
                if N <= self.max_N:
                    classes.append({"name": row['name'], "stem": s, "Adams filtration": f, "weight": w, "tautorsion": int(row['tautorsion'])})
        return classes



    def make_sfw_grouping(self, only_one_N):
        elements_in_degree = defaultdict(list)
        assert self.csv_classes is not None
        for element in self.csv_classes:
            s = element["stem"]
            f = element["Adams filtration"]
            w = element["weight"]
            tautorsion = element["tautorsion"]

            # need s + f - w + taupower <= self.max_N
            for taupower in range(0, self.max_N - s - f + w + 1):
                # entirely skip rho-periodic classes, which are exactly the classes with s + f - 2w = 0
                # (reference: Isaksen "Stable stems", Theorem 2.1.12)
                if s + f - 2*(w - taupower) == 0:
                    continue

                if only_one_N and s + f - w + taupower != self.max_N:
                    continue
                if tautorsion == 0:
                    elements_in_degree[s, f, w - taupower].append({
                        "name": f"tau^{taupower} {element['name']}",
                        "stem": s,
                        "Adams filtration": f,
                        "weight": w - tautorsion,
                        "tautorsion": 0
                    })
                if int(tautorsion) > 0 and taupower < int(tautorsion):
                    elements_in_degree[s, f, w - taupower].append({
                        "name": f"tau^{taupower} {element['name']}",
                        "stem": s,
                        "Adams filtration": f,
                        "weight": w,
                        "tautorsion": taupower
                    })
        return elements_in_degree


    def make_all_lin_combs(self):
        """
        Returns a list of tuples (tridegree, vector) that can be turned into ExtClass(tridegree, vector)
        and fed into Ext.add_classes
        """
        assert self.sfw_dict is not None
        classes = []
        for deg in self.sfw_dict:
            dimension = len(self.sfw_dict[deg])
            for vector in product([False, True], repeat=dimension):
                if sum(vector) == 0: # False = 0, and the zero vector is not added
                    continue
                classes.append((deg, list(vector)))
        return classes



    #returns the name of an element in a given degree.
    def class_name(self, deg, vector):
        if deg == None:
            if vector == [True]:
                return "0"
            elif vector == [False]:
                return "Undef"
            else:
                raise ValueError(f"Invalid element (None, {vector})")

        assert self.sfw_dict is not None
        name_lst = []

        if deg not in self.sfw_dict:
            raise ValueError(f"Degree {deg} not found in E1CsvParser.sfw_dict")
        elts = self.sfw_dict[deg]
        for i in range(len(vector)):
            if vector[i]:
                name_lst.append(elts[i]["name"])
        return (" + ").join(name_lst)


    # def class_name_by_index(a_degree, index):
    #     for element in class_index(a_degree):
    #         if element["index"] == index:
    #             return element["name"]
    #     return None


    # def vector_by_basis_names(a_degree, names):
    #     """
    #     Return the F2 bool vector for a linear combination of basis names.

    #     Repeating a basis name toggles its coefficient, so duplicates cancel.
    #     """
    #     basis = class_index(a_degree)
    #     index_by_name = {element["name"]: element["index"] for element in basis}
    #     vector = [False] * len(basis)

    #     for name in names:
    #         if name not in index_by_name:
    #             raise ValueError(f"{name!r} is not a basis element in degree {a_degree}")
    #         index = index_by_name[name]
    #         vector[index] = not vector[index]

    #     return vector


    # def vector_by_basis_name(a_degree, name):
    #     """Return the F2 bool vector for one basis element."""
    #     return vector_by_basis_names(a_degree, [name])


    # def basis_names_by_vector(a_degree, vector):
    #     """Return the basis names with True coefficients in a bool vector."""
    #     basis = class_index(a_degree)
    #     if len(vector) != len(basis):
    #         raise ValueError(
    #             f"Vector length {len(vector)} does not match dimension "
    #             f"{len(basis)} in degree {a_degree}"
    #         )
    #     return [element["name"] for element, coefficient in zip(basis, vector) if coefficient]


    # def tau_torsion_by_vector(a_degree, vector):
    #     """
    #     Return the tau-torsion determined by the True basis coefficients.

    #     The convention from the CSV is preserved: 0 means tau-torsion-free. For a
    #     nonzero finite-torsion sum, this returns the largest torsion exponent among
    #     the selected basis elements.
    #     """
    #     basis = class_index(a_degree)
    #     if len(vector) != len(basis):
    #         raise ValueError(
    #             f"Vector length {len(vector)} does not match dimension "
    #             f"{len(basis)} in degree {a_degree}"
    #         )

    #     selected_torsions = [
    #         element["tautorsion"]
    #         for element, coefficient in zip(basis, vector)
    #         if coefficient
    #     ]
    #     if not selected_torsions:
    #         return 0
    #     if 0 in selected_torsions:
    #         return 0
    #     return max(selected_torsions)



    def add_degree(self, degree1, degree2):
        return (degree1[0] + degree2[0], degree1[1] + degree2[1], degree1[2] + degree2[2])


    #then this differential function takes a source degree and a differential degree r and returns the possible differentials.

    # def possible_differentials_by_r(source_degree,r):
    #     source_elements = elements_by_degree(source_degree)
    #     target_degree = add_degree(source_degree, (r-1, 1, r))
    #     target_elements = elements_by_degree(target_degree)
    #     differentials = {}
    #     for source in source_elements:
    #         source_name = source['name']
    #         if source_name not in differentials:
    #              differentials[source_name] = []
    #         for target in target_elements:
    #             differentials[source_name].append(f"d_{r}({source_name})=rho^{r} {target['name']}")
    #     return differentials


    #returns a dictionary for all the elements in a range.

    # def group_by_degree(bounds):
    #     grouped = {}
    #     for s in range(bounds[0] + 1):
    #         for f in range(bounds[1] + 1):
    #             for w in range(-bounds[2], int(bounds[2]) + 1):
    #                 a_degree = (s, f, w)
    #                 elements = elements_by_degree(a_degree)
    #                 if elements:
    #                     grouped[a_degree] = elements
    #     return grouped




    #returns a dictionary for all the possible differentials for a range of r.

    # def possible_differentials_in_a_range(bounds,r):
    #     grouped = group_by_degree(bounds)
    #     differentials = {}
    #     degree_list = set(grouped.keys())
    #     for source_degree, source_elements in grouped.items():
    #         target_degree = add_degree(source_degree, (r-1, 1, r))
    #         if target_degree in degree_list:
    #             for source in source_elements:
    #                 source_name = source['name']
    #                 if source_name not in differentials:
    #                     differentials[source_name] = []
    #                 for target in grouped[target_degree]:
    #                     differentials[source_name].append(f"d_{r}({source_name})=rho^{r} {target['name']}")
    #     return differentials



    #returns a dictionary for all the possible differentials for a range of r and a range of source degrees.

    # def possible_differentials_by_source(source_degree, bounds):
    #     grouped = group_by_degree(bounds)
    #     differentials = {}
    #     degree_list = set(grouped.keys())
    #     source_elements = grouped.get(source_degree, [])
    #     max_r = min(bounds[0] - source_degree[0] + 1, bounds[2] - source_degree[2])
    #     if max_r < 1 or not source_elements:
    #         return {}
    #     for r in range(1, max_r + 1):
    #         target_degree = add_degree(source_degree, (r - 1, 1, r))
    #         if target_degree in degree_list:
    #             for source in source_elements:
    #                 source_name = source['name']
    #                 if source_name not in differentials:
    #                     differentials[source_name] = []
    #                 for target in grouped[target_degree]:
    #                     differentials[source_name].append(f"d_{r}({source_name})=rho^{r} {target['name']}")
    #     return differentials

    # def possible_differentials_within_bounds(bounds):
    #     grouped = group_by_degree(bounds)
    #     degree_list = set(grouped.keys())
    #     differentials = {}
    #     # Single-pass counting: avoid recomputing possible_differentials_by_source
    #     # (which rebuilds grouped) for every source degree.
    #     for source_degree, source_elements in grouped.items():
    #         max_r = min(bounds[0] - source_degree[0] + 1, bounds[2] - source_degree[2])
    #         if max_r < 1 or not source_elements:
    #             continue
    #         for r in range(1, max_r + 1):
    #             target_degree = add_degree(source_degree, (r - 1, 1, r))
    #             if target_degree in degree_list:
    #                  for source in source_elements:
    #                      source_name = source['name']
    #             if source_name not in differentials:
    #                             differentials[source_name] = []
    #                             for target in grouped[target_degree]:
    #                                differentials[source_name].append(f"d_{r}({source_name})=rho^{r} {target['name']}")
    #     return differentials

    def counting_values(classes):
        counting = {}
        for element, values in classes.items():
            counting[element] = len(values)
        return counting

    def finding_sources_with_fixed_number_of_differentials(classes, number):
        sources = []
        for element, values in classes.items():
            if len(values) == number:
                sources.append(element)
        return sources

    # group the elements by degree and write to a CSV file
    # elements = get_classes()
    # max_stem = max(element["stem"] for element in elements)
    # max_filtration = max(element["Adams filtration"] for element in elements)
    # max_weight = max(element["weight"] for element in elements)
    # grouped = group_by_degree((max_stem, max_filtration+1, max_weight+1))

    # with open("grouped_by_degree.csv", "w", newline="") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["degree", "number_of_elements", "elements"])
    #     for degree_key, source_elements in sorted(grouped.items()):
    #         names = [element["name"] for element in source_elements]
    #         writer.writerow([str(degree_key), len(names), json.dumps(names, ensure_ascii=False)])
