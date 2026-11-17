"""
This module defines the Ext class which serves as the interface to
interact with the entire cohomology of the C-motivic Steenrod Algebra
all at once. It provides methods to retrieve various kinds of elements
in the Ext algebra that should be useful for the creation of SAT constraints.
In addition, it should also provide methods to assert and to retrieve
known differentials that will be used to bootstrap the SAT solver.
"""

from collections import defaultdict
from sat_solver.ext_class import Undefined
from sat_solver.ext_class import ZeroClass
from sat_solver.ext_class import ExtClass
from sat_solver.differential import Differential
from sat_solver.E1_csv_parser import E1CsvParser


class Ext:
    """
    This class represents useful pieces of information contained in the cohomology of the C-motivic Steenrod algebra.
    """

    class_dct: dict[tuple[int, int, int], set[ExtClass]]
    known_differentials: set[Differential]
    product_table: dict[tuple[str, str], ExtClass]


    def __init__(self, E1: E1CsvParser=None, product_filename: str=None):
        self.classes = set()
        self.class_dct = defaultdict(set) # classes, organized as (s,f,w) -> list of classes
        self.degrees_by_N = defaultdict(set) # N -> set of (s,f,w) with nonzero class(es) such that s+f-w = N
        self.known_differentials = set()
        self.E1 = E1
        self.product_table = self.parse_products(product_filename)


        if E1 is not None:
            all_classes = E1.make_all_lin_combs()
            ext_classes = [ExtClass(*x) for x in all_classes]
            self.add_classes(ext_classes)



    def add_class(self, ext_class: ExtClass) -> None:
        """
        This method adds an ExtClass to the Ext algebra.

        Args:
            ext_class (ExtClass): The ExtClass to add to the Ext algebra.
        """
        s, f, w = ext_class.get_classdegree()

        self.class_dct[(s, f, w)].add(ext_class)
        self.degrees_by_N[s + f - w].add((s, f, w))


#generalize previous function.
    def add_classes(self, ext_classes: list[ExtClass]) -> None:
        """
        This method adds a list of ExtClasses to the Ext algebra.

        Args:
            ext_classes (list[ExtClass]): The list of ExtClasses to add to the Ext algebra.
        """
        for ext_class in ext_classes:
            self.add_class(ext_class)


    def get_classes(self) -> set[ExtClass]:
        if self.classes != set():
            return self.classes
        classes = set()
        for _, class_set in self.class_dct.items():
            classes |= class_set
        self.classes = classes
        return classes



    def get_nonzero_classes_in_tridegree(
        self, tridegree: tuple[int, int, int]
    ) -> list[ExtClass]:
        """
        This method returns a list of ExtClasses in a given tridegree (s, f, w).

        Args:
            tridegree (tuple[int, int, int]): The tridegree (s, f, w) of the ExtClasses to retrieve.

        Returns:
            list[ExtClass]: A list of all the ExtClasses in the given tridegree.
        """
        s, f, w = tridegree
        if (s, f, w) in self.class_dct:
            return list(self.class_dct[(s, f, w)])
        else:
            return []



    def multiply_classes(
        self,
        left: ExtClass,
        right: ExtClass,
        ) -> ExtClass:
        """
        Multiply two ExtClass objects.

        self.product_table has pairs of base names as keys and
        ExtClass objects as values.

        Multiplication is extended over sums using bilinearity.

        If any component product required by bilinearity is not
        present in self.product_table, the entire multiplication is aborted by raising KeyError.
        """
        if self.E1 is None:
            raise ValueError(
                "Ext multiplication requires an E1CsvParser object"
            )

        if left == Undefined or right == Undefined:
            return Undefined

        if left == ZeroClass or right == ZeroClass:
            return ZeroClass

        left_degree = left.get_classdegree()
        right_degree = right.get_classdegree()

        product_degree = tuple(
            left_coordinate + right_coordinate
            for left_coordinate, right_coordinate
            in zip(left_degree, right_degree)
        )

        left_basis = self.E1.sfw_dict.get(left_degree)
        right_basis = self.E1.sfw_dict.get(right_degree)

        # Check that both input degrees have E1 bases.
        if left_basis is None:
            raise ValueError(
                f"No E1 basis found in degree {left_degree}"
            )

        if right_basis is None:
            raise ValueError(
                f"No E1 basis found in degree {right_degree}"
            )

        left_vector = left.get_vector()
        right_vector = right.get_vector()

        if len(left_vector) != len(left_basis):
            raise ValueError(
                f"Left vector has length {len(left_vector)}, "
                f"but degree {left_degree} has "
                f"{len(left_basis)} basis elements"
            )

        if len(right_vector) != len(right_basis):
            raise ValueError(
                f"Right vector has length {len(right_vector)}, "
                f"but degree {right_degree} has "
                f"{len(right_basis)} basis elements"
            )

        product_basis = self.E1.sfw_dict.get(
            product_degree,
            [],
        )

        # Index basis elements using their mathematical data,
        # rather than their formatted names.
        product_indices = {
            (
                element["base_name"],
                element["taupower"],
            ): index
            for index, element in enumerate(product_basis)
        }

        # Start with the zero vector in the product degree.
        result_vector = [False] * len(product_basis)

        selected_left_terms = [
            element
            for element, coefficient
            in zip(left_basis, left_vector)
            if coefficient
        ]

        selected_right_terms = [
            element
            for element, coefficient
            in zip(right_basis, right_vector)
            if coefficient
        ]

        # Apply bilinearity.
        for left_term in selected_left_terms:
            for right_term in selected_right_terms:
                left_base_name = left_term["base_name"]
                right_base_name = right_term["base_name"]

                left_taupower = left_term["taupower"]
                right_taupower = right_term["taupower"]

                product_key = (
                    left_base_name,
                    right_base_name,
                )

                reverse_product_key = (
                    right_base_name,
                    left_base_name,
                )

                if product_key in self.product_table:
                    base_product = self.product_table[
                        product_key
                    ]
                elif reverse_product_key in self.product_table:
                    base_product = self.product_table[
                        reverse_product_key
                    ]
                else:
                    # One component product is unknown, so the
                    # product of the entire classes is unknown.
                    # Do not return the partially computed vector.
                    raise KeyError(
                        "Product table does not contain "
                        f"{left_base_name} * "
                        f"{right_base_name}"
                    )


                # This component product is known to be zero.
                if base_product == ZeroClass:
                    continue

                base_product_degree = (
                    base_product.get_classdegree()
                )

                base_product_basis = self.E1.sfw_dict.get(
                    base_product_degree
                )

                if base_product_basis is None:
                    raise ValueError(
                        "No E1 basis found for the product "
                        f"of {left_base_name} and "
                        f"{right_base_name} in degree "
                        f"{base_product_degree}"
                    )

                base_product_vector = (
                    base_product.get_vector()
                )

                if len(base_product_vector) != len(
                    base_product_basis
                ):
                    raise ValueError(
                        "Product vector has length "
                        f"{len(base_product_vector)}, "
                        f"but degree {base_product_degree} "
                        f"has {len(base_product_basis)} "
                        "basis elements"
                    )

                selected_base_product_terms = [
                    element
                    for element, coefficient
                    in zip(
                        base_product_basis,
                        base_product_vector,
                    )
                    if coefficient
                ]

                for base_product_term in (
                    selected_base_product_terms
                ):
                    # The product term may already have a tau
                    # power, so include all three exponents.
                    total_taupower = (
                        left_taupower
                        + right_taupower
                        + base_product_term["taupower"]
                    )

                    result_key = (
                        base_product_term["base_name"],
                        total_taupower,
                    )

                    result_index = product_indices.get(
                        result_key
                    )

                    if result_index is None:
                        # This tau multiple is absent from the
                        # product basis, for example because it
                        # is killed by tau-torsion.
                        continue

                    # Addition is over F_2.
                    result_vector[result_index] ^= True

        if not any(result_vector):
            return ZeroClass

        return ExtClass(
            product_degree,
            result_vector,
        )


#   The following functions are for finding possible sources and targets of differentials.

    def get_possible_differential_targets(
        self, ext_class: ExtClass, r: int
    ) -> list[ExtClass]:
        """
        This method returns a list of ExtClasses that could potentially be the target of a differential of length r starting from a given ExtClass. Does not return 0 or Undef unless the input is 0 or Undef.

        Args:
            ext_class (ExtClass): The ExtClass from which the differential starts.
            r (int): The length of the differential.

        Returns:
            list[ExtClass]: A list of all the ExtClasses that could potentially be the target of a differential of length r starting from the given ExtClass.
        """
        if ext_class == ZeroClass:
            return [ZeroClass]
        if ext_class == Undefined:
            return [Undefined]
        s, f, w = ext_class.get_classdegree()
        target_s = s + r - 1
        target_f = f + 1
        target_w = w + r

        if (target_s, target_f, target_w) in self.class_dct:
            return list(self.class_dct[(target_s, target_f, target_w)])
        else:
            return []

    def get_possible_nontrivial_differential_sources(
        self, target_class: ExtClass, r: int
    ) -> list[ExtClass]:
        """
        This method returns a list of ExtClasses that could potentially be the source
        of a differential of length r ending at a given ExtClass.

        Args:
            target_class (ExtClass): The ExtClass which is the target of the differential.
            r (int): The length of the differential.

        Returns:
            list[ExtClass]: A list of all the ExtClasses that could potentially be the source
            of a differential of length r ending at the given ExtClass.
        """
        assert target_class != Undefined and target_class != ZeroClass

        s, f, w = target_class.get_classdegree()
        source_s = s - r + 1
        source_f = f - 1
        source_w = w - r

        if (source_s, source_f, source_w) in self.class_dct:
            return list(self.class_dct[(source_s, source_f, source_w)])
        else:
            return []


    def r_with_nonzero_target(self, deg):
        s, f, w = deg
        possible_r = []
        for (target_s, target_f, target_w) in self.degrees_by_N[s + f - w]:
            if target_f == f + 1:
                r = target_w - w
                if r > 0:
                    possible_r.append(r)
        return possible_r

#
    def r_with_nonzero_source(self, deg):
        s, f, w = deg
        possible_r = []
        for (source_s, source_f, source_w) in self.degrees_by_N[s + f - w]:
            if source_f == f - 1:
                r = w - source_w
                if r > 0:
                    possible_r.append(r)
        return possible_r
    
#   functions below are for keeping track of known differentials. 
    
    def add_known_differential(self, diff: Differential) -> None:
        """
        This method adds a known differential to the list of known differentials in the rho-Bockstein spectral sequence.

        Args:
            diff (Differential): The Differential to add to the list of known differentials.
        """
        self.known_differentials.add(diff)

    def add_known_differentials(self, diffs: list[Differential]) -> None:
        """
        This method adds a list of known differentials to the list of known differentials in the rho-Bockstein spectral sequence.

        Args:
            diffs (list[Differential]): The list of Differentials to add to the list of known differentials.
        """
        for diff in diffs:
            self.add_known_differential(diff)


    def get_known_differentials(self) -> list[Differential]:
        """
        This method returns a list of known differentials in the rho-Bockstein spectral sequence.

        Returns:
            list[Differential]: A list of all the known differentials in the rho-Bockstein spectral sequence.
        """
        return list(self.known_differentials)


    def parse_products(self, filename: str) -> dict[tuple[str], dict]:
        """
        Parses the products from the csv file

        Returns:
        dict whose keys are pairs of names (e.g. ("{1-1}", "{1-0}")) and values are dicts like the ones in self.E1.sfw_dict
        """
        pass



