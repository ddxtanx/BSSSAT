"""
This module defines the Ext class which serves as the interface to
interact with the entire cohomology of the C-motivic Steenrod Algebra
all at once. It provides methods to retrieve various kinds of elements
in the Ext algebra that should be useful for the creation of SAT constraints.
In addition, it should also provide methods to assert and to retrieve
known differentials that will be used to bootstrap the SAT solver.
"""

from sat_solver.ext_class import Undefined
from sat_solver.ext_class import ZeroClass
from sat_solver.ext_class import ExtClass
from sat_solver.differential import Differential


class Ext:
    """
    This class represents useful pieces of information contained in the cohomology of the C-motivic Steenrod algebra.
    """

    classes: dict[tuple[int, int, int], set[ExtClass]]
    known_differentials: set[Differential]

    min_stem: int
    min_filtration: int
    min_weight: int

    max_stem: int
    max_filtration: int
    max_weight: int

    def __init__(self):
        self.classes = {}
        self.known_differentials = set()

        self.max_stem = 0
        self.max_filtration = 0
        self.max_weight = 0

        self.min_stem = 0
        self.min_filtration = 0
        self.min_weight = 0

    def add_class(self, ext_class: ExtClass) -> None:
        """
        This method adds an ExtClass to the Ext algebra.

        Args:
            ext_class (ExtClass): The ExtClass to add to the Ext algebra.
        """
        s, f, w = ext_class.get_degree()

        if (s, f, w) not in self.classes:
            self.classes[(s, f, w)] = set()
        self.classes[(s, f, w)].add(ext_class)

        if s > self.max_stem:
            self.max_stem = s
        if s < self.min_stem:
            self.min_stem = s
        if f > self.max_filtration:
            self.max_filtration = f
        if f < self.min_filtration:
            self.min_filtration = f
        if w > self.max_weight:
            self.max_weight = w
        if w < self.min_weight:
            self.min_weight = w

    def add_classes(self, ext_classes: list[ExtClass]) -> None:
        """
        This method adds a list of ExtClasses to the Ext algebra.

        Args:
            ext_classes (list[ExtClass]): The list of ExtClasses to add to the Ext algebra.
        """
        max_stem = self.max_stem
        max_filtration = self.max_filtration
        max_weight = self.max_weight
        min_stem = self.min_stem
        min_filtration = self.min_filtration
        min_weight = self.min_weight

        for ext_class in ext_classes:
            self.add_class(ext_class)

            s, f, w = ext_class.get_degree()
            if s > max_stem:
                max_stem = s
            if s < min_stem:
                min_stem = s
            if f > max_filtration:
                max_filtration = f
            if f < min_filtration:
                min_filtration = f
            if w > max_weight:
                max_weight = w
            if w < min_weight:
                min_weight = w

        self.max_stem = max_stem
        self.max_filtration = max_filtration
        self.max_weight = max_weight
        self.min_stem = min_stem
        self.min_filtration = min_filtration
        self.min_weight = min_weight

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

    def get_classes_up_to_coweight(self, coweight: int) -> list[ExtClass]:
        """
        This method returns a list of ExtClasses whose coweight (s - w) is less that a given maximum,
        which we will attempt to resolve questions about differentials.

        Args:
            coweight (int): The maximum coweight s - w of the ExtClasses to retrieve.

        Returns:
            list[ExtClass]: A list of all the ExtClasses whose coweight is less than the given maximum.
        """
        classes = []
        # s - w <= coweight implies s <= coweight + w
        for w in range(self.min_weight, self.max_weight + 1):
            for f in range(self.min_filtration, self.max_filtration + 1):
                for s in range(self.min_stem, coweight + w + 1):
                    if (s, f, w) in self.classes:
                        classes.extend(self.classes[(s, f, w)])
        return classes

    def get_possible_differential_targets(
        self, ext_class: ExtClass, r: int
    ) -> list[ExtClass]:
        """
        This method returns a list of ExtClasses that could potentially be the target of a differential of length r starting from a given ExtClass.

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
        s, f, w = ext_class.get_degree()
        target_s = s + r - 1
        target_f = f + 1
        target_w = w + r

        if (target_s, target_f, target_w) in self.classes:
            return list(self.classes[(target_s, target_f, target_w)])
        else:
            return []

    def get_classes_in_fixed_degree(self, N: int) -> list[ExtClass]:
        """
        This method returns a list of ExtClasses whose fixed degree (s + f - w) is equal to a given value N.

        Args:
            N (int): The fixed degree s + f - w of the ExtClasses to retrieve

        Returns:
            list[ExtClass]: A list of all the ExtClasses whose fixed degree is equal to N.
        """
        classes = []
        for s in range(self.min_stem, self.max_stem + 1):
            for f in range(self.min_filtration, self.max_filtration + 1):
                w = s + f - N
                if (s, f, w) in self.classes:
                    classes.extend(self.classes[(s, f, w)])
        return classes

    def get_classes_in_tridegree(
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
        if (s, f, w) in self.classes:
            return list(self.classes[(s, f, w)])
        else:
            return []

    def get_rho_periodic_elements(self) -> list[ExtClass]:
        """
        This method returns a list of ExtClasses that are known to be permanent cycles from the E1 page,
        equivalently elements in the R-motivic Ext after inverting rho.
        Since these are known to be permanent cycles, we can enforce that their differentials are zero in the SAT solver
        which will help to bootstrap the solver and reduce the search space.

        Returns:
            list[ExtClass]: A list of all the ExtClasses that are known to be rho periodic.
        """
        # rho periodic elements are in degree (2s + f, f, s + f)
        # (2s + f, f, s + f) = (s', f', w') implies (f' = 2w' - s')
        rho_periodic_elts = []

        for s in range(self.min_stem, self.max_stem + 1):
            for w in range(self.min_weight, self.max_weight + 1):
                f = 2 * w - s
                if (s, f, w) in self.classes:
                    rho_periodic_elts.extend(self.classes[(s, f, w)])
        return rho_periodic_elts

    def is_rho_periodic(self, ext_class: ExtClass) -> bool:
        """
        This method returns whether a given ExtClass is known to be rho periodic.

        Args:
            ext_class (ExtClass): The ExtClass to check for rho periodicity.

        Returns:
            bool: True if the ExtClass is known to be rho periodic, False otherwise.
        """
        s, f, w = ext_class.get_degree()
        return s - f == 2 * (w - f)

    def get_known_differentials(self) -> list[Differential]:
        """
        This method returns a list of known differentials in the rho-Bockstein spectral sequence.

        Returns:
            list[Differential]: A list of all the known differentials in the rho-Bockstein spectral sequence.
        """
        return list(self.known_differentials)
