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
        """
        Loads the E1 basis elements from a CSV file.

        Returns:
        list: A list of dictionaries representing the E1 basis elements, each containing keys 'name', 'stem', 'Adams filtration', 'weight', and 'tautorsion'.
        """
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
        """
        Groups the E1 basis elements by their (s, f, w) degrees, taking into account tau multiples.

        Parameters:
        only_one_N (bool): If True, only include elements with s + f - w + taupower == max_N.

        Returns:
        dict: A dictionary mapping (s, f, w) to a list of E1 basis elements in that degree.
        """
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
                        "base_name": element["name"],
                        "taupower": taupower,
                        "stem": s,
                        "Adams filtration": f,
                        "weight": w - taupower,
                        "tautorsion": 0
                    })
                if int(tautorsion) > 0 and taupower < int(tautorsion):
                    elements_in_degree[s, f, w - taupower].append({
                        "name": f"tau^{taupower} {element['name']}",
                        "base_name": element["name"],
                        "taupower": taupower,
                        "stem": s,
                        "Adams filtration": f,
                        "weight": w - taupower,
                        "tautorsion": tautorsion - taupower
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

