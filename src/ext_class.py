from __future__ import annotations
try:
    from . import find_differential
except ImportError:
    import find_differential


class ExtClass:
    """
    This class represents a class in the cohomology of the C-motivic steenrod algebra.
    """
    def __init__(self, tridegree: tuple[int, int, int], vector: list[bool]) -> None:


    def get_name(self) -> str:
        """
        Returns the name of the class as a string.
        """
        if not self._name:
            return "0"
        return " + ".join(self._name)

    def get_degree(self) -> tuple[int, int, int]:
        """
        Returns the tridegree (s, f, w) of the class as a tuple of three integers.
        """
        return (self._stem, self._filtration, self._weight)

    def get_differential_targets(self, r: int) -> list[ExtClass]:
        """
        Returns the possible targets of the differential d_r applied to this class as a list of ExtClass instances.
        If d_r(x) = rho^r y, then y should be included in the list of targets.

        Args:
            r (int): The degree of the differential d_r.

        Returns:
            list[ExtClass]: A list of ExtClass instances that are possible targets of the differential d_r.
        """
        return find_differential.possible_differentials_by_r(self.get_degree(), r)

    def __add__(self, other: ExtClass) -> ExtClass:
        if other is ZeroClass:
            return self
        if self.get_degree() != other.get_degree():
            raise ValueError("Cannot add ExtClass instances with different degrees")
        else:
            if self.get_name() == other.get_name():
                return ZeroClass
            else:
                new_terms = []
                temporary_terms = list(self._name, other._name)
                for term in other._name:
                    if counting(term, self._name) % 2 == 1:
                        continue
                
           

    def __mul__(self, other: ExtClass) -> ExtClass:
        pass

    def get_name_latex(self) -> str:
        pass

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
