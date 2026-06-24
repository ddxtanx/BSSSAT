"""
This module defines the ExtClass class, which provides a 
useful abstraction for working with classes in the 
cohomology of the C-motivic steenrod algebra.
It also defines ZeroClass,
which is an instance of ExtClass that represents the zero class.
Finally there is Undefined which is the ``None" variant of ExtClass,
used as the ``target" of a differential when the source is not a cycle on the E_r page.
"""

import find_differential

class ExtClass:
    """
    This class represents a class in the cohomology of the C-motivic steenrod algebra.
    """
    def __init__(self, name: str, stem: int, adams_filtration: int, weight: int):
        self.name = name
        self.stem = stem
        self.adams_filtration = adams_filtration
        self.weight = weight

    def get_name(self) -> str:
        """
        Returns the name of the class as a string.
        """
        return self.name

    def get_degree(self) -> tuple[int, int, int]:
        """
        Returns the tridegree (s, f, w) of the class as a tuple of three integers.
        """
        return (self.stem, self.adams_filtration, self.weight)

    def get_differential_targets(self, r: int) -> list[ExtClass]:
        """
        Returns the possible targets of the differential d_r applied to this class as a list of ExtClass instances.
        If d_r(x) = rho^r y, then y should be included in the list of targets.

        Args:
            r (int): The degree of the differential d_r.

        Returns:
            list[ExtClass]: A list of ExtClass instances that are possible targets of the differential d_r.
        """
        targets = []
        for target in find_differential.possible_differentials_by_r(self.get_degree(), r):
            targets.append(ExtClass(target['name'], target['stem'], target['Adams filtration'], target['weight']))
        return targets
        

    def __add__(self, other: ExtClass) -> ExtClass:
        """
        Constructs a new ExtClass instance that represents the sum of this class and another class.

        Args:
            other (ExtClass): The other ExtClass instance to add to this class.

        Returns:
            ExtClass: A new ExtClass instance that represents the sum of this class and the other
        """
        if self.get_degree() != other.get_degree():
            raise ValueError("Can only add Ext classes in the same tridegree")
        else :
            if self.get_name() == other.get_name():
                return ZeroClass
            if self.get_name() =

    def __mul__(self, other: ExtClass) -> ExtClass:
        """
        Constructs a new ExtClass instance that represents the product of this class and another class.
        This either just returns the naive juxtaposition of the two classes,
        or it returns the result of a known product in the Ext algebra.

        Args:
            other (ExtClass): The other ExtClass instance to multiply with this class.

        Returns:
            ExtClass: A new ExtClass instance that represents the product of this class and the other
        """
        return ExtClass(
            f"{self.name} {other.name}",
            self.stem + other.stem,
            self.adams_filtration + other.adams_filtration,
            self.weight + other.weight,
            min(self.tautorsion, other.tautorsion),
            self._ext,
        )

    def get_name_latex(self) -> str:
        """
        Returns the name of the class in LaTeX format as a string.
        """
        return self.name.replace("tau", r"\tau").replace("rho", r"\rho")

    def __hash__(self) -> int:
        return hash((self.get_name(), self.get_degree()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExtClass):
            return False
        return self.get_name() == other.get_name() and self.get_degree() == other.get_degree()

    def in_same_tridegree_as(self, other: ExtClass) -> bool:
        """
        Determines whether this class and other are in the same tridegree.

        Args:
            other (ExtClass): The other ExtClass instance to compare with this class.

        Returns:
            bool: True if this class and other are in the same tridegree, False otherwise
        """
        if other == ZeroClass:
            return True

        return self.get_degree() == other.get_degree()

ZeroClass: ExtClass = None
Undefined: ExtClass = None
